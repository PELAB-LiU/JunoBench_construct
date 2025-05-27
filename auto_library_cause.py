import pandas as pd
import utils.config as config
import utils.util as util

df_bm_labels = pd.read_excel("data/new_new_samples.xlsx", keep_default_na=False)
df_bm_labels["Libs-cause-auto"] = df_bm_labels["traceback"].map(util.detect_library_from_traceback)

df_bm_labels.to_excel("data/new_new_samples_1.xlsx", index=False, engine='xlsxwriter')