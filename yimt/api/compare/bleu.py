import sacrebleu

def calculatebleu_sacre(path_r,path_t,token):
    res = []
    tat=[]
    with open(path_r,'r',encoding='utf-8') as f:
        for line in f:
         res.append(line.strip().split('\r')[0])

    with open(path_t,'r',encoding='utf-8') as f:
        for line in f:
         tat.append(line.strip().split('\r')[0])
    print(res)
    print(tat)
    bleu = sacrebleu.corpus_bleu(res, [tat],tokenize=token)
    return bleu.score
