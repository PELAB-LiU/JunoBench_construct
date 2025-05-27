import pandas as pd
import re
import ast
from collections import defaultdict
import hashlib
import os

def save_to_sheets(excel_path, dict_dfs):
    writer = pd.ExcelWriter(excel_path, engine = 'xlsxwriter')
    for sheet_name, df in dict_dfs.items():
        df.to_excel(writer, index=False, sheet_name = sheet_name)
    writer.close()
    
    
def parse_traceback(str_traceback):
    """Parses the traceback to remove all ansii escape characters."""
    ansi_escape = re.compile(r'\\x1b\[[0-9;]*m') #re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', str_traceback)

def list_traceback(str_traceback):
    try:
        txt_traceback = parse_traceback(str_traceback)
        tb_list = ast.literal_eval(txt_traceback)
        return tb_list
    except:
        print("exception when listing traceback")
        return None

def print_traceback(txt_traceback):
    tb_list = list_traceback(txt_traceback)
    if tb_list:
        for i in tb_list:
            print(i)

# Define keywords associated with popular ML libraries
LIBRARY_KEYWORDS = {
    "tensorflow": ["tensorflow", "tf."],
    "torch": ["torch", "pytorch"],
    "matplotlib": ["matplotlib", "plt."],
    "sklearn": ["sklearn", "scikit"],
    "keras": ["keras"],
    "xgboost": ["xgboost"],
    "seaborn": ["seaborn", "sns."],
    "scipy": ["scipy"],
    "plotly": ["plotly"],
    "cv2": ["cv2"],
    "lightgbm": ["lightgbm"],
    "torchvision": ["torchvision"],
    "nltk": ["nltk"],
    "transformers": ["transformers"],
    "catboost": ["catboost"],
    "statsmodels": ["statsmodels"],
    "imblearn": ["imblearn"],
    "wordcloud": ["wordcloud"],
    "missingno": ["missingno"],
    "optuna": ["optuna"],
    "skimage": ["skimage"],
    "datasets": ["datasets"],
    "pandas": ["pandas", "pd.", "df"],
    "numpy": ["numpy", "np."],
}

def detect_library_from_traceback(traceback_str):
    lines = list_traceback(traceback_str)
    if not lines:
        return "None"
    
    library_hits = defaultdict(int)

    for line in lines:
        for subline in line.splitlines():
            is_crash_line = "---->" in subline
            line_lower = subline.lower()
            for lib, keywords in LIBRARY_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        # Give higher weight to the crash line
                        library_hits[lib] += 3 if is_crash_line else 1

    if not library_hits:
        return "None"
#     print(library_hits)
    
    # Return the library with the most relevant hits, resolve the tie by using the order of LIBRARY_KEYWORDS.keys()
    detected_lib = max(library_hits, key=lambda x: (library_hits[x], -list(LIBRARY_KEYWORDS.keys()).index(x)))
#     print(f"Likely library causing the error: {detected_lib}")
    return detected_lib


def kaggle_notebook_url(username: str, notebook_slug: str) -> str:
    """
    Generate a Kaggle notebook URL based on username and notebook slug.
    
    Args:
        username (str): Kaggle username (e.g. "ryanholbrook")
        notebook_slug (str): Notebook slug (e.g. "intro-to-programming")

    Returns:
        str: Full URL to the Kaggle notebook
    """
    if check_isNa(username) or check_isNa(notebook_slug):
        print("kaggle_notebook_url -- username or url slug is None: ", username, notebook_slug)
        return None
    return f"https://www.kaggle.com/code/{username}/{notebook_slug}"

def kaggle_dataset_url(username: str, dataset_slug: str) -> str:
    """
    Generate a Kaggle dataset URL based on username and dataset slug.
    
    Args:
        username (str): Kaggle username (e.g. "ryanholbrook")
        dataset_slug (str): Dataset slug (e.g. "titanic")

    Returns:
        str: Full URL to the Kaggle dataset
    """
    if check_isNa(username) or check_isNa(dataset_slug):
        print("kaggle_dataset_url -- username or url slug is None: ", username, dataset_slug)
        return None
    return f"https://www.kaggle.com/datasets/{username}/{dataset_slug}"

def check_isNa(target_str: str) -> bool:
    return (pd.isna(target_str))|(target_str=="")|(target_str=="NaN")|(target_str=="nan")

def pseudonymize_nbfilename(username: str, slug: str) -> str:
    """
    Convert a filename like 'username_slug.ipynb' into 'XXXX_slug.ipynb'
    """
    if check_isNa(username) or check_isNa(slug):
        print("pseudonymize_nbfilename -- username or url slug is None: ", username, slug)
        return None
    # Generate short pseudonym from hash
    hash_digest = hashlib.sha256(username.encode()).hexdigest()
    pseudonym = f"{hash_digest[:6]}"

    new_name = f"{pseudonym}_{slug}.ipynb"
    return new_name

def rename_files(folder_path, folder_name, folder_name_new):
    old_file_path_1 = os.path.join(folder_path, folder_name+".ipynb")
    new_file_path_1 = os.path.join(folder_path, folder_name_new+".ipynb")
    if os.path.exists(old_file_path_1):
        os.rename(old_file_path_1, new_file_path_1)
    else:
        return False
        print(f"{os.path.basename(old_file_path_1)} not exist!")

    old_file_path_2 = os.path.join(folder_path, folder_name+"-reproduced.ipynb")
    new_file_path_2 = os.path.join(folder_path, folder_name_new+"_reproduced.ipynb")
    if os.path.exists(old_file_path_2):
        os.rename(old_file_path_2, new_file_path_2)
    else:
        return False
        print(f"{os.path.basename(old_file_path_2)} not exist!")
    

    old_file_path_3 = os.path.join(folder_path, folder_name+"-fixed.ipynb")
    new_file_path_3 = os.path.join(folder_path, folder_name_new+"_fixed.ipynb")
    if os.path.exists(old_file_path_3):
        os.rename(old_file_path_3, new_file_path_3)
    else:
        return False
        print(f"{os.path.basename(old_file_path_3)} not exist!")
    
    return True
    # print(f"Renamed files under folder: {folder_name} -> {folder_name_new}")

def rename_notebooks_in_directory(root_dir, dict_names):
    index = 0
    # Process each immediate subfolder under root
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            subfolder_path = entry.path
            folder_name = os.path.basename(subfolder_path)
            if (folder_name+".ipynb") in dict_names.keys():
                folder_name_new = dict_names[folder_name+".ipynb"]
                # First, rename files inside this subfolder
                res = rename_files(subfolder_path, folder_name, folder_name_new)
                if res:
                    # Then, rename the subfolder itself
                    new_subfolder_path = os.path.join(root_dir, folder_name_new)
                    os.rename(subfolder_path, new_subfolder_path)
                    # print(f"Renamed folder: {folder_name} -> {folder_name_new}")

                    index += 1
            else:
                print(f"{folder_name} not found in dataframe.")
    print(f"Renamed {index} notebook folders.")
