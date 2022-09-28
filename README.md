# mt-core
Transformer based Nerual Machine Translation

## Features
1. Based on Tensorflow2
2. Support gradient accumulation and mixed precision traning
3. Effective and efficient data pipline
4. Support checkpoint averaging
5. Beam search for inference
6. Support file translation: TXT, DOC, DOCX, PPTX, PDF, HTML, XML
7. Preserve file format after translation
8. A common and easy-to-use Translator interface.
9. Support several NMT model types, such as Checkpoint, SavedModel and CTranslate2.
10. Manage NMT models through config file.
11. RESTful service interface for translation
12. Provide Web interface for text and file translation
13. Support translation volume limit and API key

## Contents
The contents of this repository are as follows:
+ Package yimt.core: [Core NMT](./yimt/core/README.md)
+ Package yimt.api: [Translator API](./yimt/api/README.md)
+ Package yimt.files: [File Translation](./yimt/files/README.md)
+ Package yimt.service: [Translation Service](./yimt/service/README.md)
+ Package yimt.corpus: [Corpus Tools](./yimt/corpus/README.md)
+ Package yimt.admin: [Corpus Tools](./yimt/admin/README.md)

## References
1. https://github.com/OpenNMT/OpenNMT-tf
2. https://github.com/ymoslem/DesktopTranslator
3. https://github.com/kakaobrain/word2word
4. https://github.com/argosopentech/translate-html
5. https://github.com/argosopentech/argos-translate
6. https://github.com/LibreTranslate/LibreTranslate
