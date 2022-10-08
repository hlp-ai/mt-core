import numpy as np


class BiTextScorer(object):
    def score(self, src, tgt):
        pass


# pip install bert-for-tf2
class LaserScorer(BiTextScorer):
    """Filter based on similarity of pair with Laser sentence embedding"""
    from laserembeddings import Laser

    laser = Laser()

    def __init__(self, lang1="en", lang2="zh"):
        self.lang1 = lang1
        self.lang2 = lang2

    def score(self, src, tgt):
        if isinstance(src, str) and isinstance(tgt, str):
            src = [src]
            tgt = [tgt]
        assert len(src) == len(tgt)

        embeddings_src = self.laser.embed_sentences(src, lang=self.lang1)
        embeddings_tgt = self.laser.embed_sentences(tgt, lang=self.lang2)
        # print(embeddings_en.shape, embeddings_zh.shape)

        norms_en = [np.linalg.norm(embeddings_src[i]) for i in range(embeddings_src.shape[0])]
        # print(norms_en)
        norms_zh = [np.linalg.norm(embeddings_tgt[i]) for i in range(embeddings_tgt.shape[0])]
        # print(norms_zh)

        # sim = np.matmul(embeddings_en, embeddings_zh.T)
        sim = [np.dot(embeddings_src[i], embeddings_tgt[i]) for i in range(embeddings_src.shape[0])]
        # print(sim.shape)

        for i in range(len(norms_en)):
            sim[i] = sim[i] / (norms_en[i] * norms_zh[i])

        return sim


class LaBSEScorer(object):

    def __init__(self, model_url, max_seq_length=128):
        self.max_seq_length = max_seq_length
        self.labse_model, labse_layer = self._get_model(model_url, max_seq_length)

        vocab_file = labse_layer.resolved_object.vocab_file.asset_path.numpy()
        do_lower_case = labse_layer.resolved_object.do_lower_case.numpy()

        import bert
        self.tokenizer = bert.bert_tokenization.FullTokenizer(vocab_file, do_lower_case)

    def score(self, src, tgt):
        sm = self._sim(src, tgt)
        # print(sm)
        # print(np.argmax(sm, axis=-1))
        return np.diagonal(sm)

    def _encode(self, input_text):
        input_ids, input_mask, segment_ids = self._create_input(input_text, self.tokenizer, self.max_seq_length)
        return self.labse_model([input_ids, input_mask, segment_ids])

    def _sim(self, src, tgt):
        src_embeddings = self._encode(src)
        tgt_embeddings = self._encode(tgt)

        sim_mat = np.matmul(src_embeddings, np.transpose(tgt_embeddings))

        return sim_mat

    def _get_model(self, model_url, max_seq_length):
        import tensorflow as tf
        import tensorflow_hub as hub

        labse_layer = hub.KerasLayer(model_url, trainable=False)

        input_word_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_word_ids")
        input_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_mask")
        segment_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="segment_ids")

        # LaBSE layer.
        pooled_output, _ = labse_layer([input_word_ids, input_mask, segment_ids])

        # The embedding is l2 normalized.
        pooled_output = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1))(pooled_output)

        # Define model.
        return tf.keras.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=pooled_output), labse_layer

    def _create_input(self, input_strings, tokenizer, max_seq_length):
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




