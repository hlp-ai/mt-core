import regex

not_letter = regex.compile(r'[^\p{L}]')


def norm(s, lower=True, remove_noletter=True):
    if lower:
        s = s.lower()

    if remove_noletter:
        s = regex.sub(not_letter, "", s)
    return s


def dedup(in_path, out_path,
          dedup_srctgt=True, dedup_src=False, dedup_tgt=False,
          lower=True, remove_noletter=True):
    """Deduplicate bitext file"""
    pairs = set()
    srcs = set()
    tgts = set()

    n = 0
    total = 0

    with open(in_path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out_f, \
            open(in_path+".deduped", "w", encoding="utf-8") as deduped_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Unique:", n)

            if dedup_src or dedup_tgt:
                pp = p.split("\t")
                if len(pp) != 2:
                    # logger.warn("dedup: not tab for pair, ommitted: {}".format(p))
                    deduped_f.write(p + "\n")
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if dedup_src:
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs in srcs:
                        # logger.debug("Source duplicate: {}".format(p))
                        deduped_f.write(p + "\n")
                        continue
                    else:
                        srcs.add(hs)
                if dedup_tgt:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht in tgts:
                        # logger.debug("Target duplicate: {}".format(p))
                        deduped_f.write(p + "\n")
                        continue
                    else:
                        tgts.add(ht)

            if dedup_srctgt:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h in pairs:
                    # logger.debug("Source-Target duplicate: {}".format(p))
                    deduped_f.write(p + "\n")
                    continue
                else:
                    pairs.add(h)

            n += 1
            out_f.write(p + "\n")

    print("Total:", total, "Unique:", n)


def dedup_rel(base_path, in_path, out_path,
              dedup_srctgt=False, dedup_src=True, dedup_tgt=False,
              lower=True, remove_noletter=True):
    """Deduplicate bitext based on a base bitext"""
    pairs = set()
    srcs = set()
    tgts = set()
    with open(base_path, encoding="utf-8") as bf:
        for p in bf:
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                print("dedup_rel: not tab for pair, ommitted:", p)
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    unique = 0
    total = 0

    with open(in_path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out_f, \
            open(in_path+".deduped", "w", encoding="utf-8") as deduped_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Unique:", unique)

            if dedup_src or dedup_tgt:
                pp = p.split("\t")
                if len(pp) != 2:
                    deduped_f.write(p + "\n")
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if dedup_src:
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs in srcs:
                        deduped_f.write(p + "\n")
                        continue

                if dedup_tgt:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht in tgts:
                        deduped_f.write(p + "\n")
                        continue

            if dedup_srctgt:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h in pairs:
                    deduped_f.write(p + "\n")
                    continue

            unique += 1
            out_f.write(p + "\n")

    print("Total:", total, "Unique:", unique)
