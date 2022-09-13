import io
import os
import tempfile
import uuid
from functools import wraps
from html import unescape

from flask import (Flask, abort, jsonify, render_template, request, send_file, url_for)
from werkzeug.utils import secure_filename
from yimt.api.translators import Translators
from yimt.api.utils import detect_lang
from yimt.api.text_splitter import word_segment

from yimt.files.translate_files import support, translate_doc
from yimt.files.translate_tag import translate_html


from yimt.service import remove_translated_files
from yimt.service.api_keys import Database
from yimt.service.utils import path_traversal_check, SuspiciousFileOperation

# log_service = get_logger(log_filename="service.log", name="service")


def get_upload_dir():
    upload_dir = os.path.join(tempfile.gettempdir(), "yimt-files-translate")

    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    return upload_dir


def get_req_api_key():
    if request.is_json:
        json = get_json_dict(request)
        ak = json.get("api_key")
    else:
        ak = request.values.get("api_key")

    return ak


def get_json_dict(request):
    d = request.get_json()
    if not isinstance(d, dict):
        abort(400, description="Invalid JSON format")
    return d


def get_remote_address():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0]
    else:
        ip = request.remote_addr or "127.0.0.1"

    # log_service.info("Request from: " + ip)

    return ip


def get_req_limits(default_limit, api_keys_db, multiplier=1):
    req_limit = default_limit

    if api_keys_db:
        api_key = get_req_api_key()

        if api_key:
            db_req_limit = api_keys_db.lookup(api_key)
            if db_req_limit is not None:
                req_limit = db_req_limit * multiplier

    return req_limit


def get_routes_limits(default_req_limit, daily_req_limit, api_keys_db):
    if default_req_limit == -1:
        # TODO: better way?
        default_req_limit = 9999999999999

    def minute_limits():
        return "%s per minute" % get_req_limits(default_req_limit, api_keys_db)

    def daily_limits():
        return "%s per day" % get_req_limits(daily_req_limit, api_keys_db, 1440)

    res = [minute_limits]

    if daily_req_limit > 0:
        res.append(daily_limits)

    return res


def create_app(args):
    app = Flask(__name__)

    if not args.disable_files_translation:
        remove_translated_files.setup(get_upload_dir())

    translators = Translators()

    lang_pairs, from_langs, to_langs = translators.support_languages()

    api_keys_db = None

    if args.req_limit > 0 or args.api_keys or args.daily_req_limit > 0:
        print("Applying request limit...")
        api_keys_db = Database() if args.api_keys else None

        from flask_limiter import Limiter

        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=get_routes_limits(args.req_limit, args.daily_req_limit, api_keys_db),
        )
    else:
        from yimt.service.utils import NoLimiter

        limiter = NoLimiter()

    def access_check(f):
        @wraps(f)
        def func(*a, **kw):
            ip = get_remote_address()

            if args.api_keys:
                ak = get_req_api_key()
                if ak and api_keys_db.lookup(ak) is None:
                    abort(403, description="Invalid API key")
                elif (
                    args.require_api_key_origin
                    and api_keys_db.lookup(ak) is None
                    and request.headers.get("Origin") != args.require_api_key_origin  # ?
                ):
                    abort(403, description="Please contact the server operator to obtain an API key")

            return f(*a, **kw)

        return func

    @app.errorhandler(400)
    def invalid_api(e):
        return jsonify({"error": str(e.description)}), 400

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e.description)}), 500

    @app.errorhandler(429)
    def slow_down_error(e):
        return jsonify({"error": "Slowdown: " + str(e.description)}), 429

    @app.errorhandler(403)
    def denied(e):
        return jsonify({"error": str(e.description)}), 403

    @app.route("/")
    @limiter.exempt
    def index():
        if args.disable_web_ui:
            abort(404)

        return render_template('text.html')

    @app.route("/file")
    @limiter.exempt
    def file():
        if args.disable_web_ui:
            abort(404)

        return render_template('file.html')

    @app.get("/languages")
    @limiter.exempt
    def languages():
        """Retrieve list of supported languages"""
        # log_service.info("/languages")
        supported_languages = from_langs
        return jsonify(supported_languages)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Authorization, Content-Type"
        )
        response.headers.add("Access-Control-Expose-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Max-Age", 60 * 60 * 24 * 20)
        return response

    @app.post("/translate")
    @app.get("/translate")
    @access_check
    def translate():
        """Translate text from a language to another"""
        if request.is_json:
            json = get_json_dict(request)
            q = json.get("q")
            source_lang = json.get("source")
            target_lang = json.get("target")
            text_format = json.get("format")
        else:
            q = request.values.get("q")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")
            text_format = request.values.get("format")

        if not q:
            abort(400, description="Invalid request: missing q parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        if not text_format:
            text_format = "text"

        if text_format not in ["text", "html"]:
            abort(400, description="%s format is not supported" % text_format)

        q = unescape(q)
        q = q.strip()
        if len(q) == 0:
            return jsonify({'translatedText': ""})

        if args.char_limit != -1:
            chars = len(q)

            if args.char_limit < chars:
                abort(
                    400,
                    description="Invalid request: Request (%d) exceeds character limit (%d)"
                                % (chars, args.char_limit),
                )

        if source_lang == "auto":
            source_lang = detect_lang(q)

        if source_lang not in from_langs:
            abort(400, description="%s is not supported" % source_lang)

        if target_lang not in to_langs:
            abort(400, description="%s is not supported" % target_lang)

        src = q
        lang = source_lang + "-" + target_lang

        tokens = word_segment(src, source_lang)
        if len(tokens) == 1:
            # log_service.info("->Translated by WordTranslator")
            word_translator = translators.get_word_translator(source_lang, target_lang)
            translation = tokens[0]
            if word_translator.has(tokens[0]):
                translation = word_translator.lookup(tokens[0])

            # log_service.info("/translate: " + q + "; " + source_lang + "-" + target_lang + "; " + text_format
            #                  + "-->" + translation)

            return jsonify({'translatedText': translation})

        translator = translators.get_translator(source_lang, target_lang)
        if translator is None:
            return "'Note: {}' not supported currently.".format(lang)

        if text_format == "html":
            translation = str(translate_html(translator, src))
        else:
            translation = translator.translate_paragraph(src)

        # log_service.info("/translate: " + q + "; " + source_lang + "-" + target_lang + "; " + text_format
        #                  + "-->" + translation)

        resp = {
            'translatedText': translation
        }
        return jsonify(resp)

    @app.post("/translate_file")
    @access_check
    def translate_file():
        """Translate file from a language to another"""
        if args.disable_files_translation:
            abort(403, description="Files translation are disabled on this server.")

        source_lang = request.form.get("source")
        target_lang = request.form.get("target")
        file = request.files['file']

        if not file:
            abort(400, description="Invalid request: missing file parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        if file.filename == '':
            abort(400, description="Invalid request: empty file")

        # log_service.info("/translate_file: " + file.filename)

        file_type = os.path.splitext(file.filename)[1]

        if not support(file_type):
            abort(400, description="Invalid request: file format not supported")

        try:
            filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename)
            filepath = os.path.join(get_upload_dir(), filename)
            file.save(filepath)

            translated_file_path = translate_doc(filepath, source_lang, target_lang)
            translated_filename = os.path.basename(translated_file_path)

            # log_service.info("->Translated: from " + filepath + " to " + translated_filename)

            return jsonify(
                {
                    "translatedFileUrl": url_for('download_file', filename=translated_filename, _external=True)
                }
            )
        except Exception as e:
            abort(500, description=e)

    @app.get("/download_file/<string:filename>")
    def download_file(filename: str):
        """Download a translated file"""
        if args.disable_files_translation:
            abort(400, description="Files translation are disabled on this server.")

        filepath = os.path.join(get_upload_dir(), filename)
        try:
            checked_filepath = path_traversal_check(filepath, get_upload_dir())
            if os.path.isfile(checked_filepath):
                filepath = checked_filepath
        except SuspiciousFileOperation:
            abort(400, description="Invalid filename")

        # log_service.info("/download_file: " + filepath)

        return_data = io.BytesIO()
        with open(filepath, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)

        download_filename = filename.split('.')
        download_filename.pop(0)
        download_filename = '.'.join(download_filename)

        return send_file(return_data, as_attachment=True, download_name=download_filename)


    return app
