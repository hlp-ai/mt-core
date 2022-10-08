from yimt.corpus.normalizers import NoPrintNormalizer

if __name__ == "__main__":
    normalizer = NoPrintNormalizer()
    s1 = "​Piazza 20 Settembre, 23 Tourist Information Office, 23900레코이탈리아	Piazza XX Settembre, 23 Tourist Information Office,莱科意大利"
    print(s1)
    print(normalizer.normalize(s1))