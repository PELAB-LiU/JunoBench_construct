import json
import os
from collections import defaultdict

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# def check_majority_vote(predictions, groundtruth, threshold=3):
#     count = 0
#     for pred_res in predictions:
#         if pred_res.strip().lower() == groundtruth.strip().lower():
#             count += 1
#     return count >= threshold

def check_first_prediction(predictions, groundtruth):
    for prediction in predictions:
        if prediction.strip().lower() in ['true', 'false']:
            return prediction.strip().lower() == groundtruth.strip().lower()

def check_all_json_outputs(folder_path_llm, groundtruth):
    n = 0
    n_correct = 0
    res = {}
    for filename in os.listdir(folder_path_llm):
        if filename.endswith('.json'):
            n += 1
            file_path_llm = os.path.join(folder_path_llm, filename)
            llm_predicts = load_json(file_path_llm)
            # res_majority = check_majority_vote(llm_predicts, groundtruth)
            res_first = check_first_prediction(llm_predicts, groundtruth)
            n_correct += res_first

            res[filename[len("crash_detection_results_"):-len(".json")]] = {
                # "majority": res_majority,
                "correct": res_first
            }

    print(f"Final results: {n_correct} out of {n} ({n_correct/n}) is correct.")
    return res

def summarize_results_by_library(results_dict):
    summary = defaultdict(lambda: {"correct": 0, "total": 0})

    for key, outcome in results_dict.items():
        if "_" not in key:
            continue  # skip malformed keys
        library = key.rsplit("_", 1)[0]  # everything before last underscore

        summary[library]["total"] += 1

        if outcome.get("correct", False):
            summary[library]["correct"] += 1
    
    sorted_summary = dict(
        sorted(summary.items(), key=lambda item: item[1]["total"], reverse=True)
    )
    return sorted_summary

# calculate results
for predict_model_path in ['llama3_70b', "mistralsmall31_latest"]:
    print(f"Model: {predict_model_path}")
    for target_version in ["fixed", "buggy"]:
        print(f"Version: {target_version}")
        res = check_all_json_outputs(f"llms/detect_if_cell_crash/{predict_model_path}/results_{target_version}", "TRUE" if target_version=="buggy" else "FALSE")
        res_summary = summarize_results_by_library(res)
        for lib, stats in res_summary.items():
            print(f"{lib}:")
            print(f"  Correct:     {stats['correct']} / {stats['total']}")
