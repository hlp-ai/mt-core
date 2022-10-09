Tools for Parallel Corpus

## Preprocessing Steps for OPUS dataset
1. Download datasets of Moses format for specific language pair from [Web](https://opus.nlpl.eu/) into one directory.
2. Use corpus/bin/extract_zips.py to unzip zip files of datasets into one directory (*unzip* directory).
3. **OPTIONAL**: For tokenized Chinese text, use corpus/bin/detok_zh.py to detokenize it, and replace the original file with detokenized file.
4. Use corpus/bin/merge_moses.py to merge each dataset with two files into one parallel file, and put them in one directory (*tsv* directory).
5. Use corpus/bin/merge.py to merge all tsv files into one tsv file.
6. Use corpus/bin/normalize.py to normalize the corpus, i.e. the tsv file generated in the previous step.
7. Use corpus/bin/dedup.py to deduplicate the corpus.
8. Use corpus/bin/filter.py to apply initial filtering on the corpus, and copy the filtered file into a new directory (score).
9. Use corpus/bin/split.py to split the corpus into a number of files.
10. Use corpus/bin/score_and_filter.py to score and filer the files or subcorpus.
11. Move the filtered files into one directory, and merge them into one file.
12. Use corpus/bin/to_single to split the parallel file into two files.