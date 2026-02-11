from pathlib import Path

path_projects = Path(r"C:\Users\yirwa29\Downloads")

# input file from the prior empirical study: data_jupyter_nbs_empirical/Manual_labeling
path_kaggle_benchmark_sheet = path_projects.joinpath("data/cluster_sampled_labeled_final.xlsx")
# intermediate/temporary files generated during the process of benchmarking, turned into the final benchmark description file: path_kaggle_benchmark_desc
path_kaggle_benchmark_sheet_new = "data/new_samples.xlsx"
path_kaggle_benchmark_sheet_all = "data/benchmark_processed.xlsx"
path_kaggle_benchmark_desc_pre = "data/benchmark_desc_pre.xlsx"
# final benchmark description file
path_kaggle_benchmark_desc = "data/benchmark_desc.xlsx"

# path_kaggle_benchmark_sheet_ori = "data/cluster_sampled_labeled_processed.xlsx"
# path_notebooks_sample = path_projects.joinpath("Dataset-Nb/sampled_notebooks")
# path_notebooks_reproduce_folder = path_projects.joinpath("Dataset-Nb/Docker_kaggle_env/benchmark")    
# path_notebooks_kerror = path_projects.joinpath("Dataset-Nb/nbdata_k_error/k_error_nbs")
# path_notebooks_reproduce_folder_new = path_projects.joinpath("Dataset-Nb/Docker_kaggle_env/0_new_samples")
# path_dbinfo = path_projects.joinpath("Dataset-Nb/NBData_KGTorrent/output_files")

path_plot_default = path_projects.joinpath("figures")

NB_SOURCE = {
    "kaggle": 1,
    "github": 2
}

license_type_full = {
    "Allow academic research": "This dataset originated from a Kaggle competition and is available for academic use.",
    "Competition Use and Academic, Non-Commercial Use Only": "This dataset originated from a Kaggle competition and is available for academic use.",
    "Allow any purpose": "This dataset originated from a Kaggle competition and is available for academic use.",
    "No private sharing outside teams": "This dataset originated from a Kaggle competition and is only available for competition use within teams. No private sharing allowed."
}

bm_lib_names = {
    "None": "nb",
    "tensorflow/keras": "tensorflow",
    "sklearn": "sklearn",
    "torch": "torch",
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "statsmodels": "statsmodels",
    "lightgbm": "lightgbm",
    "torchvision": "torchvision"
}