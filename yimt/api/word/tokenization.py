# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
from itertools import chain, islice, product, repeat
from multiprocessing import Pool
import operator
import re
from tqdm import tqdm

from yimt.api.text_splitter import word_segment


def process_line(line, lang, cased):
    """Strip, uncase (optionally), and tokenize line.

    multiprocessing helper for get_sents()."""
    line = line.strip() if cased else line.strip().lower()
    return word_segment(line, lang)


def get_sents(fin, lang, cased, n_lines, num_workers=8):
    """Load parallel corpus and segment words using multiprocessing."""

    with open(fin, encoding='utf-8') as f:
        # lines = islice(f, n_lines)
        lines = f.readlines()[:n_lines]
        sents = []
        for line in tqdm(lines, total=len(lines), desc=lang):
            sents.append(process_line(line, lang, cased))
        return sents
        # if num_workers <= 1:
        #     return [process_line(line, lang, tokenizer, cased)
        #             for line in lines]
        # else:
        #     print(f"Entering multiprocessing with {num_workers} workers...")
        #     with Pool(num_workers) as p:
        #         return p.starmap(
        #             process_line,
        #             zip(lines, repeat(lang), repeat(tokenizer), repeat(cased))
        #         )


def get_vocab(sents):
    word2idx, idx2word, idx2cnt = dict(), dict(), dict()

    word2cnt = Counter(tqdm(list(chain.from_iterable(sents)))).most_common()
    word2cnt.sort(key=operator.itemgetter(1, 0), reverse=True)
    for idx, (word, cnt) in enumerate(tqdm(word2cnt)):
        word2idx[word] = idx
        idx2word[idx] = word
        idx2cnt[idx] = cnt

    return word2idx, idx2word, idx2cnt


def update_dicts(sents1, sents2, vocab1, vocab2, cutoff):
    """Get monolingual and cross-lingual count dictionaries.

    'cutoff' determines how many collocates are considered in each language.
    """

    def u2_iter(t1, t2, same_ignore=False, cut_t2=None):
        for t in product(t1, t2):
            if (not same_ignore or t[0] != t[1]) and (not cut_t2 or t[1] < cut_t2):
                yield t

    def build_ddi():
        return defaultdict(lambda: defaultdict(int))

    x_x_dict = build_ddi()  # number of tokens co-occurence in lang1
    y_y_dict = build_ddi()
    x_y_dict = build_ddi()  # number of bilingual tokens co-occurence
    y_x_dict = build_ddi()

    for sent1, sent2 in tqdm(zip(sents1, sents2), total=len(sents1)):
        xs = [vocab1[wx] for wx in sent1 if wx in vocab1]  # why if?
        ys = [vocab2[wy] for wy in sent2 if wy in vocab2]

        for xx1, xx2 in u2_iter(xs, xs, same_ignore=True, cut_t2=cutoff):
            x_x_dict[xx1][xx2] += 1
        for yy1, yy2 in u2_iter(ys, ys, same_ignore=True, cut_t2=cutoff):
            y_y_dict[yy1][yy2] += 1
        for xx, yy in u2_iter(xs, ys, same_ignore=False):
            x_y_dict[xx][yy] += 1
            y_x_dict[yy][xx] = x_y_dict[xx][yy]

    # convert to ordinary dicts for pickling
    def ddi2dict(ddi):
        return {k: dict(v) for k, v in ddi.items()}

    return tuple(ddi2dict(ddi)
                 for ddi in [x_x_dict, y_y_dict, x_y_dict, y_x_dict])
