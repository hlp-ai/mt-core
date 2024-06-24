import io
import os
import tempfile
import uuid
from functools import wraps
from html import unescape

from flask import (Flask, abort, jsonify, render_template, request, send_file, url_for, g)
from werkzeug.utils import secure_filename

from yimt.api.text_recognizer import TextRecognizers
from yimt.api.translator import Progress
from yimt.api.translators import Translators, translator_factory
from yimt.api.utils import detect_lang, get_logger

from yimt.files.translate_files import support, translate_doc
from yimt.files.translate_html import translate_tag_list
from yimt.files.translate_tag import translate_html
from yimt.segmentation.text_splitter import may_combine_paragraph

from yimt.service import remove_translated_files
from yimt.service.api_keys import APIKeyDB
from yimt.service.translate_fn import translate_image_fn, tts_fn
from yimt.service.utils import path_traversal_check, SuspiciousFileOperation

log_service = get_logger(log_filename="service.log", name="service")


class TranslationProgress(Progress):
    def __init__(self):
        self._progress_info = ""

    def report(self, total, done):
        self._progress_info = "{}/{}".format(done, total)
        print(self._progress_info)

    def get_info(self):
        return self._progress_info



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

    log_service.info("Request from: " + ip)

    return ip


def get_req_limits(default_limit, api_keys_db, multiplier=1):
    req_limit = default_limit

    if api_keys_db:
        api_key = get_req_api_key()

        if api_key:
            db_req_limit = api_keys_db.lookup(api_key)  # get req limit for api key
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


def run_ocr(image_path, source_lang, queue):
    recognizers = TextRecognizers()
    text = recognizers.recognize(image_path, source_lang)

    queue.put(text)


def run_translate(src, text_format, source_lang, target_lang, queue):
    translators = translator_factory

    translator = translators.get_translator(source_lang, target_lang)
    if translator is None:
        return None

    if text_format == "html":
        translation = str(translate_html(translator, src))
    else:
        src = may_combine_paragraph(src)
        translation = translator.translate_paragraph(src)

    queue.put(translation)


def create_app(args):
    app = Flask(__name__)

    if not args.disable_files_translation:  # clean uploaded files periodically
        remove_translated_files.setup(get_upload_dir())

    translators = translator_factory
    # recognizers = TextRecognizers()

    translate_progress = TranslationProgress()

    lang_pairs, from_langs, to_langs, langs_api = translators.support_languages()

    api_keys_db = None

    if args.req_limit > 0 or args.api_keys or args.daily_req_limit > 0:
        print("Applying request limit...")
        api_keys_db = APIKeyDB() if args.api_keys else None

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
        """Check API key"""
        @wraps(f)
        def func(*a, **kw):
            if args.api_keys:  # need API key
                ak = get_req_api_key()
                if not ak:
                    abort(403, description="NO API key")
                elif api_keys_db.lookup(ak) is None:
                    abort(403, description="Invalid API key")

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

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")  # Allow CORS from anywhere
        response.headers.add(
            "Access-Control-Allow-Headers", "Authorization, Content-Type"
        )
        response.headers.add("Access-Control-Expose-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Max-Age", 60 * 60 * 24 * 20)
        return response

    ##############################################################################################
    #
    # Path for Web server
    #
    ##############################################################################################

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
    
    @app.route('/text')
    @limiter.exempt
    def text():
        if args.disable_web_ui:
            abort(404)

        return render_template('text.html')

    @app.route('/mobile')
    @limiter.exempt
    def mobile():
        if args.disable_web_ui:
            abort(404)

        return render_template('mobile_text.html')

    @app.route('/usage')
    @limiter.exempt
    def usage():
        if args.disable_web_ui:
            abort(404)

        return render_template('usage.html')

    @app.route('/api_usage')
    @limiter.exempt
    def api_usage():
        if args.disable_web_ui:
            abort(404)

        return render_template('api_usage.html')

    ##############################################################################################
    #
    # 对外接口
    #
    ##############################################################################################

    @app.get("/languages")
    @limiter.exempt
    def languages():
        """Retrieve list of supported languages
        No parameter
        :return list of language dictionary
        """
        log_service.info("/languages")
        supported_languages = langs_api
        return jsonify(supported_languages)

    @app.post("/translate")
    @access_check
    def translate():
        """Translate text from a language to another"""
        if request.is_json:  # json data in body of POST method
            json = get_json_dict(request)
            log_service.info(json)
            q = json.get("q")
            source_lang = json.get("source")
            target_lang = json.get("target")
            text_format = json.get("format")
            api_key = json.get("api_key")
        else:  # url data in body of POST method
            q = request.values.get("q")
            source_lang = request.values.get("source")
            target_lang = request.values.get("target")
            text_format = request.values.get("format")
            api_key = request.values.get("api_key")

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

        if not api_key:
            api_key = ""

        if isinstance(q, list):  # 浏览器插件元素列表翻译
            translations = translate_tag_list(q, source_lang, target_lang)
            resp = {
                'translatedText': translations
            }
            return jsonify(resp)

        q = unescape(q)
        q = q.strip()
        if len(q) == 0:
            return jsonify({'translatedText': ""})

        # Check the length of input text
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
            abort(400, description="Source language %s is not supported" % source_lang)

        if target_lang not in to_langs:
            abort(400, description="Target language %s is not supported" % target_lang)

        src = q
        lang = source_lang + "-" + target_lang

        translator = translators.get_translator(source_lang, target_lang)
        if translator is None:
            abort(400, description="Language pair %s is not supported" % lang)

        if text_format == "html":
            translation = str(translate_html(translator, src))
        else:
            translation = translator.translate_paragraph(src)

        log_service.info("/translate: " + "&source=" + source_lang + "&target=" + target_lang
                         + "&format=" + text_format + "&api_key=" + api_key)

        resp = {
            'translatedText': translation
        }
        return jsonify(resp)

    @app.post("/translate_image")
    @access_check
    def translate_image():
        """Translate image from a language to another"""
        # if args.disable_image_translation:
        # abort(403, description="Image translation are disabled on this server.")

        source_lang = request.form.get("source")
        target_lang = request.form.get("target")
        api_key = request.form.get("api_key")
        file = request.files['file']

        if not file:
            abort(400, description="Invalid request: missing file parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if source_lang == "auto":
            abort(400, description="Require source language when translating image")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        if file.filename == '':
            abort(400, description="Invalid request: empty file")

        log_service.info("/translate_image: " + file.filename)

        file_type = os.path.splitext(file.filename)[1]

        # if not support(file_type):
            # abort(400, description="Invalid request: file format not supported")

        try:
            filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename)
            filepath = os.path.join(get_upload_dir(), filename)
            file.save(filepath)

            result = translate_image_fn(filepath, source_lang, target_lang)
            if result is None:
                abort(400, description="NO OCR or NO translator")

            return jsonify(
                {
                    'originalText': result[0],
                    'translatedText': result[1]
                }
            )
        except Exception as e:
            abort(500, description=e)

    @app.post("/translate_file")
    @access_check
    def translate_file():
        """Translate file from a language to another"""
        if args.disable_files_translation:
            abort(403, description="Files translation are disabled on this server.")

        source_lang = request.form.get("source")
        target_lang = request.form.get("target")
        file = request.files['file']

        api_key = request.form.get("api_key")
        if not api_key:
            api_key = ""

        if not file:
            abort(400, description="Invalid request: missing file parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")

        if file.filename == '':
            abort(400, description="Invalid request: empty file")

        log_service.info("/translate_file: " + file.filename + "&source=" + source_lang + "&target=" + target_lang
                         + "&api_key=" + api_key)

        file_type = os.path.splitext(file.filename)[1]

        if not support(file_type):
            abort(400, description="Invalid request: file format not supported")

        try:
            filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename)
            filepath = os.path.join(get_upload_dir(), filename)
            file.save(filepath)

            translated_file_path = translate_doc(filepath, source_lang, target_lang, callbacker=translate_progress)
            translated_filename = os.path.basename(translated_file_path)

            suffix = filepath.split(".")[-1]

            # log_service.info("->Translated: from " + filepath + " to " + translated_filename)

            return jsonify(
                {
                    "translatedFileUrl": url_for('download_file', filename=translated_filename, _external=True),
                    "filepath": filepath,
                    "translated_file_path": translated_file_path,
                    "file_type": suffix
                }
            )
        except Exception as e:
            abort(500, description=e)

    @app.post("/translate_image2text")
    # @access_check
    def translate_image2text():
        json = get_json_dict(request)
        image_64_string = json.get("base64")
        token = json.get("token")
        source_lang = json.get("source")
        target_lang = json.get("target")

        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")
        if not image_64_string:
            abort(400, description="Invalid request: missing base64 parameter")

        if source_lang not in from_langs:
            abort(400, description="Source language %s is not supported" % source_lang)
        if target_lang not in to_langs:
            abort(400, description="Target language %s is not supported" % target_lang)

        log_service.info("/translate_image2text: " + "&source=" + source_lang + "&target=" + target_lang
                         + "&api_key=" + token)

        import base64
        image_data = base64.b64decode(image_64_string)

        filepath = os.path.join(get_upload_dir(), "decoded_image.png")

        with open(filepath, "wb") as image_file:
            image_file.write(image_data)

        # result = translate_image_fn(filepath, source_lang, target_lang)
        # if result is None:
        #     abort(400, description="NO OCR or NO translator")

        resp = {
            'text': "this is a test for ocr."
        }
        return jsonify(resp)

    @app.post("/translate_audio2text")
    # @access_check
    def translate_audio2text():
        json = get_json_dict(request)
        audio_64_string = json.get("base64")
        format = json.get("format")
        rate = json.get("rate")
        channel = json.get("channel")
        token = json.get("token")
        len = json.get("len")
        source_lang = json.get("source")
        target_lang = json.get("target")

        from_audio_formats = ["pcm", "wav", "amr", "m4a"]
        q = "audio2text"  # for test

        if not format:
            abort(400, description="Invalid request: missing format parameter")
        if not audio_64_string:
            abort(400, description="Invalid request: missing base64 parameter")
        if not rate:
            abort(400, description="Invalid request: missing rate parameter")
        if not channel:
            abort(400, description="Invalid request: missing channel parameter")
        if not len:
            abort(400, description="Invalid request: missing len parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source parameter")
        if not target_lang:
            abort(400, description="Invalid request: missing target parameter")
        if source_lang == "auto":
            source_lang = detect_lang(q)
        if source_lang not in from_langs:
            abort(400, description="Source language %s is not supported" % source_lang)
        if target_lang not in to_langs:
            abort(400, description="Target language %s is not supported" % target_lang)

        if format not in from_audio_formats:
            abort(400, description="Audio format %s is not supported" % format)

        import base64
        audio_data = base64.b64decode(audio_64_string)
        with open("decoded_audio.wav", "wb") as audio_file:
            audio_file.write(audio_data)
        resp = {
            'text': "this is a test for asr"
        }
        return jsonify(resp)

    @app.post("/translate_text2audio")
    # @access_check
    def translate_text2audio():
        json = get_json_dict(request)
        token = json.get("token")
        text = json.get("text")
        lang = json.get("lang")

        log_service.info("/translate_text2audio: " + "&text=" + text + "&lang=" + lang
                         + "&api_key=" + token)

        if not text:
            abort(400, description="Invalid request: missing text parameter")
        if not lang:
            abort(400, description="Invalid request: missing source parameter")
        # if lang == "auto":
        #     lang = detect_lang(text)
        # if lang not in from_langs:
        #     abort(400, description="Source language %s is not supported" % lang)

        import base64
        audio_64_string = base64.b64encode(open("dida.wav", "rb").read())  # 这里设置本地音频路径
        # print(audio_64_string.decode('utf-8')) # for test
        type = "wav"
        resp = {
            'base64': audio_64_string.decode('utf-8'),
            'type': type
        }
        return jsonify(resp)

    @app.post("/text2speech")
    # @access_check
    def text2speech():
        json = get_json_dict(request)
        token = json.get("token")
        text = json.get("text")
        source_lang = json.get("lang")

        if not text:
            abort(400, description="Invalid request: missing text parameter")
        if not source_lang:
            abort(400, description="Invalid request: missing source language parameter")
        if source_lang == "auto":
            source_lang = detect_lang(text)
        # if source_lang not in from_langs:
        #     abort(400, description="Source language %s is not supported" % source_lang)

        result = tts_fn(text, source_lang)
        if result is None:
            abort(400, description="NO TTS")

        import base64
        audio_64_string = base64.b64encode(result[0].numpy().tobytes())
        resp = {
            'base64': audio_64_string.decode('utf-8'),
            'rate': result[1]
        }
        return jsonify(resp)

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

        log_service.info("/download_file: " + filepath)

        return_data = io.BytesIO()
        with open(filepath, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)

        download_filename = filename.split('.')
        download_filename.pop(0)  # remove the prefix generated by system
        download_filename = '.'.join(download_filename)

        return send_file(return_data, as_attachment=True, download_name=download_filename)

    @app.post("/request_ad")
    # @access_check
    def request_ad():
        json = get_json_dict(request)
        platform = json.get("platform")
        support_platforms = ["app", "web", "plugin"]

        if not platform:
            abort(400, description="Invalid request: missing parameter: platform")
        if platform not in support_platforms:
            abort(400, description="platform %s is not supported" % platform)

        ad_id = "AD-20221020"
        if platform == "web" or platform == "app":
            type = "image"
        else:
            type = "text"

        ad_text = "Welcome!\n This is a just test."
        if type == "text":
            content = ad_text
        else:
            import base64
            with open("./static/img/ad11.png", "rb") as image_file:  # 设置本地图片路径
                encoded_image = base64.b64encode(image_file.read())
            image_file.close()
            content = encoded_image.decode('utf-8')

        ad_url = "http://www.hust.edu.cn/"  # for test

        log_service.info("/request_ad: " + "platform=" + platform + "&ad_id=" + ad_id)

        resp = {
            'ad_id': ad_id,
            'type': type,
            'content': content,
            'url': ad_url
        }
        return jsonify(resp)

    #####################################################################
    #
    # 内部路径
    #
    #####################################################################

    @app.route("/reference")
    @limiter.exempt
    def reference():
        if args.disable_web_ui:
            abort(404)
        return render_template('reference.html')


    @app.route("/translate_file_progress", methods=['GET', 'POST'])
    def get_translate_progress():
        file = request.files['file']
        file_type = os.path.splitext(file.filename)[1]
        progress = translate_progress.get_info()

        return progress

    @app.post("/get_blob_file")
    # @access_check
    def get_blob_file():
        json = get_json_dict(request)
        file_path = json.get("file_path")
        import base64
        file_64_string = base64.b64encode(open(file_path, "rb").read())
        resp = {
            'base64': file_64_string.decode('utf-8')
        }
        return jsonify(resp)

    @app.get("/pptx")
    def pptx():
        file_path = request.args.get('file_path')
        return send_file(file_path)

    @app.get("/request_source")
    def request_source():
        file_type = request.args.get('file_type')
        file_path = request.args.get('file_path')
        if file_type == 'docx' or file_type == 'pptx' or file_type == 'xlsx':
            file_path_str = url_for('static', filename=file_path)
            file_path_str = file_path_str.replace('/static/', '/')
            file_path_str = file_path_str.lstrip('/')
            return render_template("media_source.html", file_type=file_type, file_path=file_path_str)

        return send_file(file_path)

    @app.get("/request_target")
    def request_target():
        file_type = request.args.get('file_type')
        file_path = request.args.get('translated_file_path')
        if file_type == 'docx' or file_type == 'pptx' or file_type == 'xlsx':
            file_path_str = url_for('static', filename=file_path)
            file_path_str = file_path_str.replace('/static/', '/')
            file_path_str = file_path_str.lstrip('/')
            return render_template("media_target.html", file_type=file_type, file_path=file_path_str)

        return send_file(file_path)

    return app
