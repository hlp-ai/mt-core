# coding:utf-8
# !pip install bert-for-tf2
import sys
import time

import bert
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub


class LaBSEScorer(object):

    def __init__(self, model_url, max_seq_length):
        self.max_seq_length = max_seq_length
        self.labse_model, labse_layer = get_model(model_url, max_seq_length)

        vocab_file = labse_layer.resolved_object.vocab_file.asset_path.numpy()
        do_lower_case = labse_layer.resolved_object.do_lower_case.numpy()
        self.tokenizer = bert.bert_tokenization.FullTokenizer(vocab_file, do_lower_case)

    def score(self, src, tgt):
        sm = self.sim(src, tgt)
        # print(sm)
        # print(np.argmax(sm, axis=-1))
        return np.diagonal(sm)

    def encode(self, input_text):
        input_ids, input_mask, segment_ids = create_input(input_text, self.tokenizer, self.max_seq_length)
        return self.labse_model([input_ids, input_mask, segment_ids])

    def sim(self, src, tgt):
        src_embeddings = self.encode(src)
        tgt_embeddings = self.encode(tgt)

        sim_mat = np.matmul(src_embeddings, np.transpose(tgt_embeddings))

        return sim_mat


def get_model(model_url, max_seq_length):
    labse_layer = hub.KerasLayer(model_url, trainable=True)

    input_word_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_word_ids")
    input_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_mask")
    segment_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="segment_ids")

    # LaBSE layer.
    pooled_output, _ = labse_layer([input_word_ids, input_mask, segment_ids])

    # The embedding is l2 normalized.
    pooled_output = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1))(pooled_output)

    # Define model.
    return tf.keras.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=pooled_output), labse_layer


def create_input(input_strings, tokenizer, max_seq_length):
    input_ids_all, input_mask_all, segment_ids_all = [], [], []
    for input_string in input_strings:
        # Tokenize input.
        input_tokens = ["[CLS]"] + tokenizer.tokenize(input_string) + ["[SEP]"]
        input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
        sequence_length = min(len(input_ids), max_seq_length)

        # Padding or truncation.
        if len(input_ids) >= max_seq_length:
            input_ids = input_ids[:max_seq_length]
        else:
            input_ids = input_ids + [0] * (max_seq_length - len(input_ids))

        input_mask = [1] * sequence_length + [0] * (max_seq_length - sequence_length)

        input_ids_all.append(input_ids)
        input_mask_all.append(input_mask)
        segment_ids_all.append([0] * max_seq_length)
    return np.array(input_ids_all), np.array(input_mask_all), np.array(segment_ids_all)


def main(in_path, out_path):
    scorer = LaBSEScorer("D:/kidden/mt/open/mt-ex/mt/data/labse1", 72)

    srcs = []
    tgts = []
    n_buf = 256
    cnt = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        lines = in_f.readlines()
        print("# of lines:", len(lines))
        for line in lines:
            line = line.strip()
            pair = line.split("\t")
            src = pair[0]
            tgt = pair[1]

            if len(srcs) < n_buf:
                srcs.append(src)
                tgts.append(tgt)
            else:
                ss = scorer.score(srcs, tgts)
                for i in range(len(ss)):
                    out_f.write("{:.4f}\t{}\t{}\n".format(ss[i], srcs[i], tgts[i]))
                srcs.clear()
                tgts.clear()
                print(cnt)

            cnt += 1

        if len(srcs) > 0:
            ss = scorer.score(srcs, tgts)
            for i in range(len(ss)):
                out_f.write("{:.4f}\t{}\t{}\n".format(ss[i], srcs[i], tgts[i]))
        print(cnt)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
