"""
This is the main file of the search engine, which should be run as the main program. Usages are available by running `python search_small_corpus.py -h` or `python search_small_corpus.py --help`.

Author: Venderbad
Version: small-corpus-0.0.4
"""

import os
import builtins
import re
import math
from queue import PriorityQueue
import json
import argparse
# import cProfile
# import pstats
from porter import PorterStemmer
from typing import List, Dict, Tuple, Set
from datetime import datetime


### GLOBAL VARS ###

k: float = 1.0  # k1
b: float = 0.75  # b
avg_DL: float = 0.0  # average document length
total_word_count: int = 0  # total number of words in the corpus, only for avg_DL

p = None  # PorterStemmer LATER_INIT
stopword_set = set()  # stopword set LATER_LOAD

rank_cap:int = 15 # the maximum number of results to show
shell_result_page_size:int = 15 # the number of results to show per page in interactive mode

index: dict = {
    "global_vars": {"k": k, "b": b, "avg_DL": avg_DL},
    "doc_len_dict": {
        # "doc1": 100,
        # "doc2": 200,
        # # ...
        # "doc999": 300,
        # ...
    },
    "tf_dict": {
        # "word1": {"doc1": 1},
        # "word2": {"doc2": 1, "doc3": 1, "doc6": 1},
        # # ...
        # "word999": {"doc999": 1},
        # ...
    },
}

# index = {}

USELESS_SYMBOLS_REGEX = '[,.\(\)!?";:\[\]{}<>\\/]'

DESCRIPTION_TEXT = """
COMP3009J Search Engine By Venderbad,
ver small-corpus-0.0.4,
Based on Okapi BM25 Model
"""

INSTRUCTION_TEXT = """
Interactive mode instructions:
    1. type in your query string in the shell
    2. press enter to search
    
    If you want to quit, type in "QUIT" and press enter

Automatic mode instructions:
    In this mode the program will load queries from queries.txt in the same directory
    and output the results to results.txt in the same directory
"""
MY_UCD_NUM = "DELETED_FOR_GITHUB"

### END OF GLOBAL VARS ###


def search(querystr: str) -> PriorityQueue:
    """Search the query string and output a pile of results

    Args:
        querystr (str): The query to search for, in string format

    Returns:
        PriorityQueue: Contains the results, with each element's [0] being
        negative similarity (for priority queueing), [1] being the docname
    """
    global k, b, avg_DL, p, stopword_set

    # ensure global tools ( unnecessary theorectically )
    if p is None or len(stopword_set) == 0:
        init_global_tools()

    # process raw query string
    raw_tokens = re.sub(USELESS_SYMBOLS_REGEX, "", querystr).strip().split()
    q_tokens_set = set()
    for raw_token in raw_tokens:
        if raw_token not in stopword_set:
            token = p.stem(raw_token)
            q_tokens_set.add(token)

    ordered_result = PriorityQueue()
    for docname in index["doc_len_dict"].keys():
        sim = cal_bm25_sim(docname, q_tokens_set)
        reversed_sim = -sim
        ordered_result.put((reversed_sim, docname)) if reversed_sim != 0 else None
    return ordered_result


def cal_bm25_sim(docname: str, query_tokens: Set[str]) -> float:
    """Calculate the BM25 similarity between a document and a query

    Args:
        docname (str): The filename of the target document
        query_tokens (Set[str]): Processed query tokens in a set

    Returns:
        float: The calculated BM25 similarity
    """
    sim = 0.0
    for q_i in query_tokens:
        tf = get_tf(q_i, docname)
        idf = get_idf(q_i)
        numerator = tf * (k + 1)
        denominator = tf + k * (1 - b + b * (get_doc_len(docname) / avg_DL))
        sim += idf * (numerator / denominator)
    return sim


def get_tf(word: str, docname: str) -> int:
    """Get the term frequency of a word in a document from the index

    Args:
        word (str): The word to get the term frequency of
        docname (str): The document to get the term frequency in

    Returns:
        int: The term frequency of the word in the document
    """
    return index["tf_dict"].get(word, {}).get(docname, 0)


def get_idf(word: str) -> float:
    """Get the inverse document frequency of a word by calculating it

    Args:
        word (str): The word to get the inverse document frequency of

    Returns:
        float: The inverse document frequency of the word
    """
    return cal_idf(word)


def cal_idf(word: str) -> float:
    """Calculate the inverse document frequency of a word

    Args:
        word (str): The word to calculate the inverse document frequency of

    Returns:
        float: The calculated inverse document frequency of the word
    """
    return (
        max(
            math.log2(
                (
                    len(index["doc_len_dict"].keys())
                    - len(index["tf_dict"][word].keys())
                    + 0.5
                )
                / (len(index["tf_dict"][word].keys()) + 0.5)
            ),
            0.0,
        ) # to avoid negative idf
        if word in index["tf_dict"].keys()
        else 0.0 # if not in index then never appear, so idf = 0
    )


def get_doc_len(docname: str) -> int:
    """Get the length of a document from the index

    Args:
        docname (str): The document filename to get the length of

    Returns:
        int: The length of the document
    """
    return index["doc_len_dict"].get(docname, 0)


def load_index():
    """Load index from json file"""
    global index
    with open(os.path.join(os.path.dirname(__file__), "index.json"), "r") as f:
        index = json.load(f)


def write_index():
    """Write index into json file"""
    global index
    with open(os.path.join(os.path.dirname(__file__), "index.json"), "w") as f:
        json.dump(index, f, indent="\t")


def load_global_vars():
    """Load global variables""" # this is not elegant as I thought, TBH
    global index, k, b, avg_DL
    k = index["global_vars"].get("k")
    b = index["global_vars"].get("b")
    avg_DL = index["global_vars"].get("avg_DL")


def rebuild_index():
    """Rebuild the index datastructure from scratch"""
    # ensure global tools ( unnecessary theorectically )
    if p is None or len(stopword_set) == 0:
        init_global_tools()
    # build index for large corpus in large docs folder
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")

    for root, dirs, filenames in os.walk(docs_dir):
        for filename in filenames:
            update_index_by_file(root, filename)

    # update avg_DL
    global avg_DL
    avg_DL = total_word_count / len(index["doc_len_dict"])

    # write in global vars
    index["global_vars"]["avg_DL"] = avg_DL
    index["global_vars"]["k"] = k
    index["global_vars"]["b"] = b


def update_index_by_file(root: str, filename: str):
    """Update index by a document with given filename under given root

    Args:
        root (str): The root directory of the document
        filename (str): The filename of the document
    """
    path_to_file = os.path.join(root, filename)
    with open(path_to_file) as docfile:
        lines = docfile.readlines()
        for line in lines:
            # meaningless symbol removal
            line = re.sub(USELESS_SYMBOLS_REGEX, "", line)
            words = line.strip().split()
            # update total_word_count
            global total_word_count
            total_word_count += len(words)
            for word in words:
                # plus doc_len by 1
                index["doc_len_dict"][filename] = (
                    index["doc_len_dict"].setdefault(filename, 0) + 1
                )
                # stopword removal & stemming
                word = word.lower()
                if word not in stopword_set:
                    word = p.stem(word)

                    # plus term freq by 1 in tf_dict tf_dict
                    index["tf_dict"][word][filename] = (
                        index["tf_dict"].setdefault(word, {}).setdefault(filename, 0)
                        + 1
                    )


def init_global_tools():
    """Initialize global tools including the stemmer and stopword set"""
    # init stemmer
    global p
    p = PorterStemmer()

    # init stopword set
    with open(os.path.join(os.path.dirname(__file__), "stopwords.txt")) as f:
        for line in f:
            stopword_set.add(line.strip())


def start_simple_shell():
    """Start a simple shell for user to interactively enter queries and get search results"""
    while True:
        try:
            user_input = builtins.input("Enter Query: \n>> ")  # listen for user input
        except KeyboardInterrupt:
            print("\nForce quiting program...")
            break

        # handling input
        if user_input == "":  # if user input is empty, continue loop
            continue
        elif user_input == "QUIT":
            print("Quiting program...")
            break
        else:
            print("Results for query [", user_input, "]")
            results: PriorityQueue = search(user_input)
            if results.qsize() == 0:
                print("Nothing is retrieved!")
            else:
                rank = 0
                while not results.empty():
                    result = results.get()
                    rank += 1
                    if rank <= shell_result_page_size: # formerly using rank_cap directly
                        print(
                            rank, result[1], -result[0]
                        )  # negative symbol for reversing back
                    else:
                        break


def batch_search_queries():
    """Search queries in queries.txt and write results into results.txt

    Raises:
        SyntaxError: The queries.txt file is corrupted or in wrong format
    """
    with open(
        os.path.join(os.path.dirname(__file__), "queries.txt"), "r"
    ) as queries_f, open(
        os.path.join(os.path.dirname(__file__), "results.txt"), "w"
    ) as results_f:
        lines = queries_f.readlines()
        for line in lines:
            match = re.search(r"\d+", line)
            if match:
                query_id = match.group()
                query_str = re.sub(r"\d+", "", line, count=1)
                results: PriorityQueue = search(query_str)
                rank = 0
                while not results.empty():
                    result = results.get()
                    rank += 1
                    if rank <= rank_cap:
                        to_write: str = (
                            str(query_id)
                            + " "
                            # + "Q0"
                            # + " "
                            + str(result[1])  # docname
                            + " "
                            + str(rank)
                            + " "
                            + str(-result[0])  # reverse back sim score
                            # + " "
                            # + MY_UCD_NUM
                            + "\n"
                        )  # no more TREC format due to the updated homework requirements
                        results_f.write(to_write)
                    else:
                        break
            else:
                raise SyntaxError("File queries.txt is corrupted or in wrong format")


if __name__ == "__main__":
    # args parsing
    parser = argparse.ArgumentParser(description=DESCRIPTION_TEXT)
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["interactive", "automatic"],
        help="mode: interactive or automatic, default is interactive",
        default="interactive",
    )
    parser.add_argument("-k", "--k", type=float, help="k1, default 1.0", default=k)
    parser.add_argument("-b", "--b", type=float, help="b, default 0.75", default=b)
    parser.add_argument("--result-cap", action="store", type=int, dest="cap", default=rank_cap, help="set rank until which number, default " + str(rank_cap))
    parser.add_argument("--rebuild", action="store_true", help="force rebuilding index")
    # parser.add_argument("-t", "--test", action="store_true", help="test mode")

    args = parser.parse_args()

    # override global vars
    k = args.k
    b = args.b
    
    rank_cap = args.cap

    # init global tools
    init_global_tools()

    # if args.test:
    #     cProfile.run("rebuild_index()", "output.dat")
    #     pstat = pstats.Stats("output.dat")
    #     pstat.sort_stats("cumulative").print_stats()

    # rebuild or load index
    if args.rebuild:
        print("Force rebuilding index, please wait...")
        rebuild_index()
        write_index()
    elif not os.path.exists(os.path.join(os.path.dirname(__file__), "index.json")):
        print("No index file detected, building index now...")
        rebuild_index()
        write_index()
    else:
        try:
            load_index()
            load_global_vars()
            print(
                "Successfuly loaded info for",
                str(len(index["tf_dict"])),
                "wordstems and",
                str(len(index["doc_len_dict"])),
                "documents",
            )
        except:
            print("Seems like index file is corrupted, trying to rebuild index now...")
            rebuild_index()
            write_index()

    if args.mode == "interactive":
        # start simple shell
        start_simple_shell()
    elif args.mode == "automatic":
        # auto search through queries.txt file
        # start_time = datetime.now().timestamp()
        batch_search_queries()
        # print("Batch search finished using", datetime.now().timestamp() - start_time, "s")

    else:
        raise RuntimeError("Default value non functioning?")
