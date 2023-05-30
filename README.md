# COMP3009J Search Engine By Venderbad
## Intro

As the requirement of COMP3009J, this is a search engine based on Okapi BM25 Model, which supports **both small corpus and large corpus**.

For searching, Both interactive and automatic mode are implemented. The programm will automatically load the index file if it exists, otherwise it will build the index file first. You can also force the programm to rebuild the index file by using `--rebuild` argument. Using `--result-cap` argument to override the default result cap, which is **15** for small corpus and **35** for large corpus. Other argument related information can be found in the Usages section, or by using `-h` or `--help` argument when running the programm.

I used the **PriorityQueue** datastructure from standard library to contain the search results, which is quite efficient. The programm will automatically sort the results by score and output the top **15** result. `--result-cap` argument **only works for automatic mode** now.

Code itself is well commented, ratinally structured and easy to read. Every function has a docstring to explain its purpose and usage. I was trying to use pure functional programming style yet I still have space to improve.

Indexing for small corpus takes about **1-5** seconds, depends on the machine and intepreter. On a Ryzon R7 4800HS, indexing for large corpus takes about **130s** with python 3.11, **170s** with pypy3. On Apple ARM chips it could shrink to **30-45s**, tested on a borrowed Macbook Pro. With a pre-build index file, the **index loading process** takes about **5** seconds for large corpus, almost **no time** for small corpus. Search operation itself takes **no perceivable time** at all.
### Sample Run

- Search, Interactive Mode
```sh
$ python search_small_corpus.py

Successfuly loaded info for 6694 wordstems and 1398 documents
Enter Query:
>> satellite
Results for query [ satellite ]
1 449 9.283385564593411
2 619 8.916543708086344
3 616 8.903633013863084
4 448 8.374766703258947
5 622 8.2749859537503
6 1150 8.138596861209232
7 617 8.095354002011966
8 615 8.02429477338402
9 162 7.794027688521246
10 613 7.610134294421624
11 618 7.522462846789785
12 438 7.041386705208574
13 614 6.74537204978093
14 983 6.61348351238984
15 620 6.496118716299744
Enter Query:
>> QUIT
Quiting program...
```

- Search, Automatic Mode
```sh
$ python search_small_corpus.py -m automatic
Successfuly loaded info for 6694 wordstems and 1398 documents
$ cat results.txt
1 51 1 28.025676808044484
1 486 2 25.96956699435358
1 12 3 22.495026915140116
1 878 4 22.22528002768472
1 573 5 19.948025651589287
...
225 794 14 12.515047196566169
225 173 15 12.482577448405493
```

- Evaluate
```sh
$ python evaluate_small_corpus.py
Evaluation scores for results.txt
Prec   :  0.2281481481481483
Recall :  0.4821974056420944
P@10   :  0.2915555555555555
R-Prec :  0.3756253357366914
MAP    :  0.3614382308508725
bpref  :  0.35976824734050045

$ python evaluate_large_corpus.py
Evaluation scores for results.txt
Prec   :  0.44514991181657865
Recall :  0.8205778812249046
P@10   :  0.574074074074074
R-Prec :  0.5255959353894083
MAP    :  0.5192817685902295
bpref  :  0.5243283746096367
```

## Usages

### Search

- Search Small Corpus
  
```sh
$ python search_small_corpus.py -h

usage: search_small_corpus.py [-h] [-m {interactive,automatic}] [-k K] [-b B] [--result-cap CAP] [--rebuild]

COMP3009J Search Engine By Venderbad, ver small-corpus-0.0.4, Based on Okapi BM25 Model

optional arguments:
  -h, --help            show this help message and exit
  -m {interactive,automatic}, --mode {interactive,automatic}
                        mode: interactive or automatic, default is interactive
  -k K, --k K           k1, default 1.0
  -b B, --b B           b, default 0.75
  --result-cap CAP      set rank until which number, default 15
  --rebuild             force rebuilding index
```


- Search Large Corpus

```sh
$ python search_large_corpus.py -h

usage: search_large_corpus.py [-h] [-m {interactive,automatic}] [-k K] [-b B] [--result-cap CAP] [--rebuild]

COMP3009J Search Engine By Venderbad, ver large-corpus-0.0.4, Based on Okapi BM25 Model

optional arguments:
  -h, --help            show this help message and exit
  -m {interactive,automatic}, --mode {interactive,automatic}
                        mode: interactive or automatic, default is interactive
  -k K, --k K           k1, default 1.0
  -b B, --b B           b, default 0.75
  --result-cap CAP      set rank until which number, default 35
  --rebuild             force rebuilding index
```

## Evaluate


- Evaluate Small Corpus Search Results
```sh
$ python evaluate_small_corpus.py -h

usage: evaluate_small_corpus.py [-h] [--target TARGET]

Evaluator

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET, -t TARGET
                        target result file name, default 'results.txt'
```

- Evaluate Large Corpus Search Results
```sh
$ python evaluate_large_corpus.py -h

usage: evaluate_large_corpus.py [-h] [--target TARGET]

Evaluator

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET, -t TARGET
                        target result file name, default 'results.txt'
```
