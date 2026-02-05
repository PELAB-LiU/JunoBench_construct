import pandas as pd
import utils.config as config
import utils.util as util

df_bm_labels = pd.read_excel(config.path_kaggle_benchmark_sheet_new, keep_default_na=False)
df_bm_labels["Libs-cause-auto"] = df_bm_labels["traceback"].map(util.detect_library_from_traceback)

df_bm_labels.to_excel("data/tmp_samples.xlsx", index=False, engine='xlsxwriter')