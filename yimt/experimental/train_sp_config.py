import sentencepiece as spm

from yimt.api.translator import detok_pretok_str

# sp_config_train = {
#     "model_type": "bpe",
#     "vocab_size": 3200,
#     "normalization_rule_name": "identity",
#     "remove_extra_whitespaces": False,
# }

# spm.SentencePieceTrainer.train(input=r"D:\mt-train\th-test.txt",
#                                model_prefix="th-sp",
#                                **sp_config_train)

tokenizer = spm.SentencePieceProcessor(model_file = "./th-test.txt-sp-3200.model")
tokens = tokenizer.encode("มันดีจริงๆ   ที่ มีชีวิตอยู่   ใช่ไหม ?", out_type=str)
print(tokens)
t = "".join(tokens).replace("▁", " ")
print(t)
print(detok_pretok_str(t))
