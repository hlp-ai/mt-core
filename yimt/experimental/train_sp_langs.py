import sentencepiece as spm


spm.SentencePieceTrainer.train(input="./langs.txt",
                               model_prefix="langs",
                               vocab_size = 300,
                               user_defined_symbols=["<tozh>", "<toen>"])

tokenizer = spm.SentencePieceProcessor(model_file = "./langs.model")
tokens = tokenizer.encode("<tozh>This is a book.", out_type=str)
print(tokens)
print(tokenizer.encode("This is a book.", out_type=str))

print()

ids = tokenizer.encode("<tozh>This is a book.")
print(ids)
print(tokenizer.encode("This is a book."))

print()

print(tokenizer.decode(ids))
for t in ids:
    print(t, tokenizer.decode([t]))