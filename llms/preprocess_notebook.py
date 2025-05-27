# Re-running the code after execution environment was reset

import json
from typing import List, Dict, Tuple, Optional
from nbformat import read, NO_CONVERT
import config_llm
import re
import html
import pandas as pd
import tokenize
from io import StringIO

def parse_traceback(str_traceback):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', str_traceback)

def extract_bug_location_from_cell(cell: dict) -> Optional[Tuple[Optional[int], Optional[str]]]:
    """
    Extract the crashing line number from the error traceback in a code cell's output.
    Returns a 1-based line number and line of code or None if not found.
    """
    if 'outputs' not in cell:
        return None, None
    
    for output in cell['outputs']:
        if output.output_type == 'error':
            traceback_lines = output.get('traceback', [])
            traceback_lines = parse_traceback("\n".join(traceback_lines))
            pattern = r'<ipython-input-(\d+)-[\da-f]+> in <cell line: (\d+)>()'
            match = re.search(pattern, traceback_lines)
            if match:
                line_number = int(match.group(2))
                source_lines = cell.get("source", [])
                if isinstance(source_lines, str):
                    source_lines = source_lines.splitlines()
                if 1 <= line_number <= len(source_lines):
                    return line_number, source_lines[line_number - 1].strip()
    return None, None

def find_buggy_cell_index_and_line(nb_cells: List[dict]) -> Tuple[Optional[int], Optional[int]]:
    """
    Identify the buggy code cell index and the crashing line number.
    """
    code_cell_index = 0
    for cell in nb_cells:
        if cell.cell_type != 'code':
            continue
        for output in cell.get('outputs', []):
            if output.output_type == 'error':
                line = extract_bug_location_from_cell(cell)
                return code_cell_index, line
        code_cell_index += 1
    return None, None

def normalize_whitespace(code):
    # Remove trailing spaces and tabs on each line
    lines = [line.rstrip() for line in code.splitlines()]
    
    # Replace multiple blank lines with a single blank line
    cleaned = []
    blank = False
    for line in lines:
        if line.strip() == "":
            if not blank:
                cleaned.append("")
                blank = True
        else:
            cleaned.append(re.sub(r'[ \t]+', ' ', line))  # Reduce inner spaces
            blank = False

    return '\n'.join(cleaned).strip()

def remove_comments(source_code):
    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    result = []
    last_lineno = -1
    last_col = 0

    for token in tokens:
        tok_type = token.type
        tok_string = token.string
        start_line, start_col = token.start

        if tok_type == tokenize.COMMENT:
            continue

        if start_line > last_lineno:
            result.append('\n' * (start_line - last_lineno - 1))
            last_col = 0

        if start_col > last_col:
            result.append(' ' * (start_col - last_col))

        result.append(tok_string)
        last_lineno, last_col = token.end

    cleaned_code = ''.join(result)
    # Optional: strip trailing spaces from each line
    cleaned_code = '\n'.join(line.rstrip() for line in cleaned_code.splitlines())
    return normalize_whitespace(cleaned_code)

# [for detecting if a target cell crash]
# process reproduced crashing notebooks to: a list of successfully executed code cells, crashing code cell (target)
def preprocess_buggy_notebook_auto_executed_code_cells(nb_path: str, out_name: str):
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = read(f, as_version=NO_CONVERT)

    buggy_index, _ = find_buggy_cell_index_and_line(nb.cells)
    if buggy_index is None:
        raise ValueError(f"No error output found in the notebook {out_name}.")

    processed_nb = {"executed": [], "target": None}
    code_cell_count = 0  # Track code cells for logical indexing

    for cell in nb.cells:
        if cell.cell_type == 'code':
            exec_count = cell.get('execution_count')
            first_line = cell.source.strip().splitlines()[0] if cell.source.strip() else ""
            if (("[re-execute]" in first_line) or ("[reexecute]" in first_line)) or (code_cell_count != buggy_index and exec_count is not None):
                processed_nb["executed"].append({
                    "execution_count": exec_count, 
                    "code_cell_id": code_cell_count, 
                    "code": remove_comments(cell.source.strip())})
            if code_cell_count == buggy_index:
                processed_nb["target"] = {
                    "code_cell_id": code_cell_count, 
                    "code": remove_comments(cell.source.strip())}
            code_cell_count += 1

    if processed_nb["target"] is None:
        print(f"No target cell assigned to {out_name}!")
    if len(processed_nb["executed"])<=0:
        print(f"No executed cell(s) assigned to {out_name}!")

    # print(processed_nb)
    output_path = config_llm.path_nb_buggy_processed.joinpath(f"{out_name}.json")
    output_path.write_text(json.dumps(processed_nb, ensure_ascii=False, indent=2), encoding="utf-8")

# [for detecting if a target cell crash]
# process fixed notebooks to: a list of successfully executed code cells, used-to-crash code cell (target)
def preprocess_fixed_notebook_auto_executed_code_cells(nb_buggy_path: str, nb_fix_path: str, out_name: str):
    with open(nb_buggy_path, 'r', encoding='utf-8') as f:
        nb_buggy = read(f, as_version=NO_CONVERT)
    with open(nb_fix_path, 'r', encoding='utf-8') as f:
        nb_fix = read(f, as_version=NO_CONVERT)

    processed_nb = {"executed": [], "target": None}
    code_cell_count = 0  # Track code cells for logical indexing
    executed_cell_ids_buggy = [d["code_cell_id"] for d in nb_buggy["executed"]]
    target_cell_id_buggy = nb_buggy["target"]["code_cell_id"]
    for cell in nb_fix.cells:
        if cell.cell_type == 'code':
            exec_count = cell.get('execution_count')
            if (code_cell_count in executed_cell_ids_buggy) and (code_cell_count != target_cell_id_buggy):
                processed_nb["executed"].append({
                    "execution_count": exec_count, 
                    "code_cell_id": code_cell_count, 
                    "code": remove_comments(cell.source.strip())})
            if code_cell_count == target_cell_id_buggy:
                processed_nb["target"] = {
                    "code_cell_id": code_cell_count, 
                    "code": remove_comments(cell.source.strip())}
            code_cell_count += 1

    if processed_nb["target"] is None:
        print(f"No target cell assigned to {out_name}!")
    if len(processed_nb["executed"])<=0:
        print(f"No executed cell(s) assigned to {out_name}!")

    # print(processed_nb)
    output_path = config_llm.path_nb_fixed_processed.joinpath(f"{out_name}.json")
    output_path.write_text(json.dumps(processed_nb, ensure_ascii=False, indent=2), encoding="utf-8")

df_bm_labels = pd.read_excel(config_llm.path_nbs_desc, keep_default_na=False)
for name in df_bm_labels["nb_name"]:
    file_path_buggy = config_llm.path_nbs.joinpath(f"{name}/{name}_reproduced.ipynb")
    # # preprocess_notebook_auto_all_code_cells(file_path_buggy, name)
    preprocess_buggy_notebook_auto_executed_code_cells(file_path_buggy, name) # buggy
    file_path_fixed = config_llm.path_nbs.joinpath(f"{name}/{name}_fixed.ipynb")
    preprocess_fixed_notebook_auto_executed_code_cells(config_llm.path_nb_buggy_processed.joinpath(f"{name}.json"), file_path_fixed, name) # fix

