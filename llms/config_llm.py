from pathlib import Path
import utils.config as config

path_default = config.path_projects.joinpath("Dataset-Nb/Docker_kaggle_env/JunoBench")
path_nbs = path_default.joinpath("benchmark")
path_nbs_desc = path_default.joinpath("benchmark_desc.xlsx")

param_options={"temperature": 0.1, "max_tokens": 128000}

# [for detecting if a target cell crash]
path_nb_buggy_processed = Path("detect_if_cell_crash/input_nb_buggy_processed")
path_nb_fixed_processed = Path("detect_if_cell_crash/input_nb_fixed_processed")
prompt_instruct = """You are an automated crash detector for ML notebooks. Given a sequence of code cells that have been successfully executed, determine whether the next code cell (the target cell) will crash upon execution. Output TRUE it will crash, otherwise output FALSE. Do not output anything else.
"""