import pandas as pd
import numpy as np
import random
import string

# Function to generate fake value based on original column properties
def generate_fake_value(dtype, col_series):
    if pd.api.types.is_integer_dtype(dtype):
        min_val = col_series.min()
        max_val = col_series.max()
        return random.randint(min_val if not np.isnan(min_val) else 0,
                               max_val if not np.isnan(max_val) else 100)
    elif pd.api.types.is_float_dtype(dtype):
        min_val = col_series.min()
        max_val = col_series.max()
        return round(random.uniform(min_val if not np.isnan(min_val) else 0,
                                     max_val if not np.isnan(max_val) else 100), 2)
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        min_date = col_series.min()
        max_date = col_series.max()
        if pd.isnull(min_date) or pd.isnull(max_date):
            min_date = pd.Timestamp('2000-01-01')
            max_date = pd.Timestamp('2020-01-01')
        delta_days = (max_date - min_date).days
        random_days = random.randint(0, delta_days)
        return min_date + pd.to_timedelta(random_days, unit='d')
    else:  # Assume object/categorical
        unique_vals = col_series.dropna().unique()
        if len(unique_vals) > 0:
            return random.choice(unique_vals)
        else:
            return ''.join(random.choices(string.ascii_letters, k=8))

def generate_fake_dataset(path_ori):
    if not path_ori.endswith(".csv"):
        print("Can only handle .csv format.")
        return

    original = pd.read_csv(path_ori)
    fake_data = original.copy()
    for col in fake_data.columns:
        dtype = fake_data[col].dtype
        col_series = original[col]
        mask = fake_data[col].isnull()
        fake_data[col] = [generate_fake_value(dtype, col_series) if not is_na else np.nan for is_na in mask]

    path_new = path_ori[:-4] + "_synthetic.csv"
    fake_data.to_csv(path_new, index=False)
    print(f"Synthetic dataset generated and saved as '{path_new}'.")


path_ori = r'C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\reproduced\mathyseizaecrepin_paris-house-price-regression-analysis\data\ParisHousing.csv'
generate_fake_dataset(path_ori)