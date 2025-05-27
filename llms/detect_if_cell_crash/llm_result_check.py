import json
import os
from collections import defaultdict

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_majority_vote(predictions, groundtruth, threshold=3):
    count = 0
    for pred_res in predictions:
        if pred_res.strip().lower() == groundtruth.strip().lower():
            count += 1
    return count >= threshold

def check_all_json_outputs(folder_path_llm, groundtruth):
    n = 0
    n_majority = 0
    res = {}
    for filename in os.listdir(folder_path_llm):
        if filename.endswith('.json'):
            n += 1
            file_path_llm = os.path.join(folder_path_llm, filename)
            llm_predicts = load_json(file_path_llm)
            res_majority = check_majority_vote(llm_predicts, groundtruth)
            n_majority += res_majority

            res[filename[len("crash_detection_results_"):-len(".json")]] = {
                "majority": res_majority
            }

    print(f"Majority vote results: {n_majority} out of {n} ({n_majority/n}) is correct.")
    return res

def summarize_results_by_library(results_dict):
    summary = defaultdict(lambda: {"majority_correct": 0, "total": 0})

    for key, outcome in results_dict.items():
        if "_" not in key:
            continue  # skip malformed keys
        library = key.rsplit("_", 1)[0]  # everything before last underscore

        summary[library]["total"] += 1

        if outcome.get("majority", False):
            summary[library]["majority_correct"] += 1
    
    sorted_summary = dict(
        sorted(summary.items(), key=lambda item: item[1]["total"], reverse=True)
    )
    return sorted_summary


predict_model_path = 'llama3_70b' # "mistralsmall31_latest" #
target_version = "fixed" #"buggy" # "fixed" #
res = check_all_json_outputs(f"{predict_model_path}/results_{target_version}", "TRUE" if target_version=="buggy" else "FALSE")
res_summary = summarize_results_by_library(res)

for lib, stats in res_summary.items():
    print(f"{lib}:")
    print(f"  Majority:     {stats['majority_correct']} / {stats['total']}")