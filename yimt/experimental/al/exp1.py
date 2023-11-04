from yimt.api.translator import TranslatorCkpt

import tensorflow as tf

translator_ckpt = TranslatorCkpt(config_file=r"D:\kidden\mt\mt-exp\en-zh\ccm1\run-29m-zhen-big\deploy.yml",
                                 sp_src_path=r"D:\kidden\mt\exp\sp\spm-bpe-zh-32000.model",
                                 lang_pair="zh-en")

input = translator_ckpt._preprocess(["我是一名大学教师。", "诗和远方对我来说是奢求。", "红鲤鱼和绿鲤鱼都是鱼。",
                                     "千金易得，一将难求。"])

# encode
features = translator_ckpt._model.features_inputter.make_features(features=input.copy())

# translate
_, outputs = translator_ckpt._model(features)

texts = translator_ckpt._postprocess(outputs)

print(outputs.keys())
print(texts)

print(outputs["log_probs"], outputs["log_probs"]/tf.cast(outputs["length"], tf.float32))
