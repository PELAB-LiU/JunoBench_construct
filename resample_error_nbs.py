import pandas as pd
import utils.config as config
import numpy as np
from pathlib import Path

def get_labeled_file():
    df_bm_labels = pd.read_excel(config.path_kaggle_benchmark_sheet, keep_default_na=False)
    df_bm_labels_k = df_bm_labels[df_bm_labels.nb_source==config.NB_SOURCE["kaggle"]]
    return df_bm_labels_k

# def get_excluded_file_names():
#     my_file = open(config.path_projects.joinpath("data_jupyter_nbs_empirical/0_complementary/Sampling/exclude_k_filenames.txt"), "r") 
#     exclude_k_filenames_exist = my_file.read() 
#     exclude_k_filenames_exist = exclude_k_filenames_exist.split("\n") 
#     my_file.close() 
#     return exclude_k_filenames_exist

# def get_already_sampled_file_names():
#     df_bm_labels = pd.read_excel(config.path_kaggle_benchmark_sheet_new, keep_default_na=False)
#     return df_bm_labels.fname.tolist()

def sample(libraries, sample_size, save_path):
    df_err_grouped_k = pd.read_excel(config.path_projects.joinpath("data_jupyter_nbs_empirical/Clustering/clusters_Kaggle_final.xlsx"))
    df_bm_labels_k = get_labeled_file()
    # filter based on ename
    # tmp_k = df_err_grouped_k[(df_err_grouped_k.ename != "nameerror") & df_err_grouped_k.ename.isin(df_bm_labels_k[(df_bm_labels_k.Reproduce==1)].ename.unique())]
    # filter based on previously excluded tutorial files
    # tmp_k = tmp_k[~tmp_k["fname"].isin(get_excluded_file_names())]
    # filter based on already labeled files
    tmp_k = df_err_grouped_k[~df_err_grouped_k["fname"].isin(df_bm_labels_k.fname.tolist())]
    # filter based on already sampled files
    # tmp_k = tmp_k[~tmp_k["fname"].isin(get_already_sampled_file_names())]
    # filter based on interested libraries
    imports_pd = pd.read_excel(config.path_projects.joinpath('data_jupyter_nbs_empirical/Kaggle/ml_library/nb_imports_all_final.xlsx'))
    imports_pd['imports'] = imports_pd['imports'].apply(eval)
    filtered_file_names = imports_pd[imports_pd['imports'].apply(lambda x: any(item in x for item in libraries))]['fname']
    tmp_k = tmp_k[tmp_k['fname'].isin(filtered_file_names)]
    print("The pool is of size", tmp_k.fname.nunique())

    # sample
    if tmp_k.fname.nunique() > sample_size:
        sample_k = tmp_k.sample(n=sample_size, random_state=43)
        sample_k = sample_k.reindex(columns=df_bm_labels_k.columns, fill_value="")
        sample_k.to_excel(save_path, index=False, engine='xlsxwriter')
        print ("Successfully sampled {} to {}".format(sample_size, save_path))
    else:
        print ("Cannot sample more than the pool size!")
        tmp_k = tmp_k.reindex(columns=df_bm_labels_k.columns, fill_value="")
        tmp_k.to_excel(save_path, index=False, engine='xlsxwriter')
        print ("Saved all {} to {}".format(tmp_k.fname.nunique(), save_path))

sample(libraries = ["torch", "sklearn", "tensorflow", "keras", "seaborn", "matplotlib", "statsmodels", "torchvision", "lightgbm"], sample_size = 500, save_path = config.path_kaggle_benchmark_sheet_new)
