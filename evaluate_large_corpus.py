"""
This script is used to evaluate the performance of the search engine.

Author: Venderbad
"""

import os
import argparse
from typing import List, Tuple, Dict

all_ret_ls_dict:Dict = {
    # '''
    # THE DOCS MY SYS RETURNED
    # # sample data
    # "query1": ["doc1", "doc2", "doc3", "doc4", "doc5"],
    # "query2": ["doc1", "doc2", "doc3", "doc4"],
    # "query3": ["doc8", "doc9", "doc10", "doc11", "doc12"],
    # ...
    # "query999": ["doc854", "doc926", "doc1428"]
    # '''
}
all_rel_ls_dict:Dict = {
    # '''
    # TRULY RELEVANT SAID BY EXPERTS
    # # sample data
    # "query1": ["doc1", "doc2", "doc3", "doc4"],
    # "query2": ["doc4", "doc9", "doc10", "doc11"],
    # ...
    # "query999": ["doc854", "doc926", "doc1428", "doc1499"]
    # '''
}
all_irr_ls_dict:Dict = {
    # '''
    # CONFIRMED IRRELEVANT DOCUMENTS
    # # sample data
    # "query1": ["doc5"],
    # "query2": ["doc1", "doc2", "doc3", "doc5"],
    # ...
    # "query999": ["doc857"]
    # '''
}

target_filename = "results.txt"

def load_global_vars():
    with open(os.path.join(os.path.dirname(__file__), target_filename), "r") as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.split()
            query_id = tokens[0]
            docname = tokens[1]
            rank_for_query = tokens[2]
            grade = tokens[3]
            all_ret_ls_dict.setdefault(query_id, [])
            all_ret_ls_dict.get(query_id).append(docname)


    
    with open(os.path.join(os.path.dirname(__file__), "qrels.txt"), "r") as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.split()
            query_id = tokens[0]
            useless_0 = tokens[1]
            docname = tokens[2]
            grade = tokens[3]
            if int(grade) > 0:
                # confirmed relevant
                all_rel_ls_dict.setdefault(query_id, [])
                all_rel_ls_dict.get(query_id).append(docname)
            elif int(grade) == 0:
                # confirmed irrelevant
                all_irr_ls_dict.setdefault(query_id, [])
                all_irr_ls_dict.get(query_id).append(docname)
    
    
    # print("all_ret_rank_lss: ", all_ret_rank_lss)
    # print("all_rel_rank_lss: ", all_rel_rank_lss)

def cal_precision_and_recall(ret_rank_ls:List, rel_rank_ls:List)->Tuple[float, float]:
    ret_set = set(ret_rank_ls)
    rel_set = set(rel_rank_ls)
    return (len(ret_set.intersection(rel_set)) / len(ret_set), len(ret_set.intersection(rel_set)) / len(rel_set))

def cal_precision_at_n(ret_rank_ls: List, rel_rank_ls: List, n)-> float:
    ret_set = set(ret_rank_ls[:n])
    rel_set = set(rel_rank_ls)
    return len(ret_set.intersection(rel_set)) / n

def cal_r_precision(ret_rank_ls: List, rel_rank_ls: List)-> float:
    return cal_precision_at_n(ret_rank_ls, rel_rank_ls, len(rel_rank_ls))

def cal_map(ret_rank_ls: List, rel_rank_ls: List)-> float:
    ret_set = set(ret_rank_ls)
    rel_set = set(rel_rank_ls)
    sum = 0
    relret_amount_sofar = 0
    for i in range(0, len(ret_rank_ls)):
        if ret_rank_ls[i] in rel_set:
            relret_amount_sofar += 1
            sum += relret_amount_sofar / (i+1) # i+1 is the rank
    return sum / len(rel_set)

def cal_bpref(ret_rank_ls: List, rel_rank_ls: List, irr_rank_ls: List)-> float:
    rel_set = set(rel_rank_ls)
    irr_set = set(irr_rank_ls)
    sum = 0
    non_rel_sofar = set()
    for i in range(0, len(ret_rank_ls)):
        if ret_rank_ls[i] in rel_set and ret_rank_ls[i] in irr_set:
            raise Exception("WHAT THE FUCK")
        elif ret_rank_ls[i] in rel_set:
            sum += max( 1 - len(non_rel_sofar)/len(rel_set), 0)
        elif ret_rank_ls[i] in irr_set:
            non_rel_sofar.add(ret_rank_ls[i])
        else:
            pass
        
    return sum / len(rel_set)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Evaluator")
    parser.add_argument("--target", "-t", action="store", type=str, dest="target", default="results.txt", help="target result file name, default 'results.txt'")
    
    args = parser.parse_args()
    
    # override
    target_filename = args.target
    
    load_global_vars()
    
    results = {
        "precisions": [],
        "recalls": [],
        "p@10s": [],
        "r-precisions": [],
        "maps": [],
        "bprefs": []
    }
    
    if len(all_ret_ls_dict) != len(all_rel_ls_dict):
        raise Exception("all_ret_rank_lss and all_rel_rank_lss should have the same length")
    
    for q_id in all_ret_ls_dict:
        ret_ls = all_ret_ls_dict.get(q_id, [])
        rel_ls = all_rel_ls_dict.get(q_id, [])
        irr_ls = all_irr_ls_dict.get(q_id, [])
        setbased_pair = cal_precision_and_recall(ret_ls, rel_ls)
        results["precisions"].append(setbased_pair[0])
        results["recalls"].append(setbased_pair[1])
        results["p@10s"].append(cal_precision_at_n(ret_ls, rel_ls, 10))
        results["r-precisions"].append(cal_r_precision(ret_ls, rel_ls))
        results["maps"].append(cal_map(ret_ls, rel_ls))
        results["bprefs"].append(cal_bpref(ret_ls, rel_ls, irr_ls))
    
    
    print("Evaluation scores for", target_filename)
    print("Prec   : ", sum(results["precisions"])/len(results["precisions"]))
    print("Recall : ", sum(results["recalls"])/len(results["recalls"]))
    print("P@10   : ", sum(results["p@10s"])/len(results["p@10s"]))
    print("R-Prec : ", sum(results["r-precisions"])/len(results["r-precisions"]))
    print("MAP    : ", sum(results["maps"])/len(results["maps"]))
    print("bpref  : ", sum(results["bprefs"])/len(results["bprefs"]))
    # print("NDCG : ", )