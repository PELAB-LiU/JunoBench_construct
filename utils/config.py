from pathlib import Path

path_kaggle_benchmark_sheet_ori = "data/cluster_sampled_labeled_processed.xlsx"
path_kaggle_benchmark_sheet = "data/empirical_study_dataset_construct.xlsx"
path_kaggle_benchmark_sheet_new = "data/new_samples.xlsx"
path_kaggle_benchmark_sheet_all = "data/benchmark_processed.xlsx"
path_kaggle_benchmark_sheet_all_data_license_complete = "data/benchmark_datalicensecomplete.xlsx"
path_kaggle_benchmark_sheet_all_data_license_complete_processed = "data/benchmark_datalicensecomplete_processed.xlsx"

path_notebooks_sample = Path(r"C:\Users\yirwa29\Downloads\Dataset-Nb\sampled_notebooks")
path_notebooks_reproduce_folder = Path(r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\benchmark")    

path_notebooks_kerror = Path(r"C:\Users\yirwa29\Downloads\Dataset-Nb\nbdata_k_error\k_error_nbs")
path_notebooks_reproduce_folder_new = Path(r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\0_new_samples")

path_plot_default = Path(r"C:\Users\yirwa29\Downloads\figures")

path_dbinfo = Path(r"C:\Users\yirwa29\Downloads\Dataset-Nb\NBData_KGTorrent\output_files")

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