from yimt.corpus.utils import norm


def dedup_rel(base_path, in_path, out_path,
              dedup_srctgt=False, dedup_src=True, dedup_tgt=False,
              lower=True, remove_noletter=True):
    """Deduplicate bitext based on a base bitext"""
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0
    print("Scanning base file...")
    with open(base_path, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 10000 == 0:
                print(total)
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

    print(total)

    unique = 0
    total = 0

    print("Deduping...")
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
