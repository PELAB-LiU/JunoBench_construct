#!/usr/bin/env python3
"""
Requirements Filtering Tool for JunoBench
==========================================

Filters requirements_docker_image.txt to include only packages imported in benchmark notebooks.
Includes smart package group handling and manually curated essential packages.

Usage: python filter_requirements.py
"""

import pandas as pd
import re
from typing import Set, List, Tuple

# File paths
path_imports = "data/nbdata_k_imports.xlsx"  # Note: using the actual file name
path_nbs = "data/benchmark_datalicensecomplete_processed.xlsx" # fname

# MANUALLY CURATED ESSENTIAL PACKAGES
# These packages are always included regardless of import detection
MANUAL_PACKAGES = [
    
]

def extract_all_imports(path_imports):
    df = pd.read_excel(path_imports) 
    # Parse string representations of sets into individual imports
    all_imports = set()
    for imports_str in df['imports']:
        try:
            # Parse string representation of set
            imports_set = eval(imports_str)
            if isinstance(imports_set, set):
                all_imports.update(imports_set)
            elif isinstance(imports_set, (list, tuple)):
                all_imports.update(imports_set)
        except:
            continue
    return all_imports


def extract_benchmark_imports(path_imports, path_nbs):
    """Extract imports only from benchmark notebooks (111 notebooks)"""
    
    try:
        benchmark_df = pd.read_excel(path_nbs)
        print(f"Loaded {len(benchmark_df)} benchmark notebooks")

        # Use fname column for matching
        benchmark_files = set(benchmark_df['fname'].unique())        
    except Exception as e:
        print(f"Error loading benchmark data: {e}")
        return
    
    imports_df = pd.read_excel(path_imports)
    
    # Filter imports to only those from benchmark notebooks
    if 'fname' in imports_df.columns:
        benchmark_imports_df = imports_df[imports_df['fname'].isin(benchmark_files)]
    else:
        print("fname column not found, checking for alternatives...")
        return
        
    # Get unique imports from benchmark notebooks
    # The 'imports' column contains string representations of sets, need to parse them
    all_imports = set()
    for imports_str in benchmark_imports_df['imports']:
        try:
            # Parse string representation of set into actual set
            # e.g., "{'PIL', 'pandas', 'matplotlib'}" -> {'PIL', 'pandas', 'matplotlib'}
            imports_set = eval(imports_str)
            if isinstance(imports_set, set):
                all_imports.update(imports_set)
            elif isinstance(imports_set, (list, tuple)):
                all_imports.update(imports_set)
        except:
            # If parsing fails, skip this entry
            continue
    
    unique_benchmark_imports = all_imports
    
    print(f"Found {len(unique_benchmark_imports)} unique imports in benchmark notebooks")
    
    return unique_benchmark_imports


def filter_requirements_by_imports(imports_set, requirements_file="data/requirements_docker_image.txt", output_file="requirements.txt"):
    """Filter requirements_docker_image.txt based on imports used in notebooks"""
    import re
    
    # Import name -> Package name mappings for common mismatches
    import_to_package = {
        'pil': 'pillow',
        'cv2': 'opencv-python', 
        'skimage': 'scikit-image',
        'sklearn': 'scikit-learn',
        'mpl_toolkits': 'matplotlib',
        'pylab': 'matplotlib',
        'imblearn': 'imbalanced-learn',
        'kerastuner': 'keras-tuner',
        'pandas_profiling': 'pandas-profiling',
        'qiskit_algorithms': 'qiskit-algorithms',
        'qiskit_machine_learning': 'qiskit-machine-learning',
        'sklearn_pandas': 'sklearn-pandas',
        'category_encoders': 'category-encoders',
        'chart_studio': 'chart-studio'
    }
    
    # Base package groups - when base is imported, include core + commonly used extensions
    package_groups = {
        'keras': ['keras', 'keras-tuner'],  # Core + tuning (most common)
        'tensorflow': ['tensorflow', 'tensorflow-hub'],  # Core + hub models
        'pandas': ['pandas'],  # Just core, extensions are specialized
        'matplotlib': ['matplotlib'],  # Just core
        'scikit-learn': ['scikit-learn']  # Just core, others are specialized
    }
    
    # Python builtin modules (don't need installation)
    python_builtin = {
        'argparse', 'ast', 'collections', 'copy', 'csv', 'datetime', 'functools', 'glob', 
        'io', 'itertools', 'json', 'logging', 'math', 'ntpath', 'os', 'pickle', 'platform', 
        'pprint', 'random', 're', 'shutil', 'statistics', 'string', 'subprocess', 'sys', 
        'time', 'typing', 'urllib', 'warnings'
    }
    
    # Read original requirements
    try:
        with open(requirements_file, 'r') as f:
            req_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {requirements_file} not found!")
        return [], []
    
    print(f"Original requirements file has {len(req_lines)} lines")
    
    # Extract package names and match against imports
    matched_requirements = []
    processed_imports = set()
    unmatched_imports = set()
    
    # Add manually curated packages FIRST
    # print(f"\nAdding {len(MANUAL_PACKAGES)} manually curated packages...")
    manual_package_names = set()
    for pkg in MANUAL_PACKAGES:
        matched_requirements.append(pkg)
        pkg_name = re.match(r'^([a-zA-Z0-9\-_\.]+)', pkg).group(1).lower()
        manual_package_names.add(pkg_name)
        print(f"  + {pkg_name}")
    
    # Build lookup of all available packages
    available_packages = {}
    for line in req_lines:
        original_line = line.strip()
        if not original_line or original_line.startswith('#') or original_line.startswith('-'):
            continue
            
        # Extract package name
        match = re.match(r'^([a-zA-Z0-9\-_\.]+)', original_line)
        if match:
            package_name = match.group(1).lower()
            available_packages[package_name] = original_line
        
    # Process each import
    for imp in imports_set:
        imp_lower = imp.lower()
        
        # Skip Python builtin modules
        if imp_lower in python_builtin:
            processed_imports.add(imp)
            continue
        
        # Get target package name (handle import/package name mismatches)
        target_package = import_to_package.get(imp_lower, imp_lower)
        
        # Track if this import was matched
        import_matched = False
        
        # Check if this import has a package group
        if target_package in package_groups:
            group_packages = package_groups[target_package]
            # print(f"📦 Found group for '{imp}' -> {group_packages}")
            
            for group_pkg in group_packages:
                if group_pkg in available_packages and group_pkg not in manual_package_names:
                    matched_requirements.append(available_packages[group_pkg])
                    import_matched = True
                    # print(f"  ✓ Added: {group_pkg}")
                elif group_pkg in manual_package_names:
                    print(f"  ⚠️ Skipped {group_pkg} (already in manual packages)")
                    import_matched = True  # Still matched, just using manual version
        else:
            # Single package match
            if target_package in available_packages and target_package not in manual_package_names:
                matched_requirements.append(available_packages[target_package])
                import_matched = True
                # print(f"✓ '{target_package}' matched import '{imp}'")
            elif target_package in manual_package_names:
                print(f"⚠️ Skipped '{target_package}' (already in manual packages)")
                import_matched = True  # Still matched, just using manual version
        
        # Only add to processed_imports if it was actually matched
        if import_matched:
            processed_imports.add(imp)
    
    # Find truly unmatched imports
    for imp in imports_set:
        if imp not in processed_imports and imp.lower() not in python_builtin:
            unmatched_imports.add(imp)
    
    print(f"\nMatched {len(set(matched_requirements)) - len(MANUAL_PACKAGES)} additional packages from requirements_docker_image.txt")
    print(f"Python builtin modules (ignored): {len([imp for imp in imports_set if imp.lower() in python_builtin])}")
    print(f"Unmatched imports (not in requirements): {len(unmatched_imports)}")
    
    # Create filtered requirements file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Remove duplicates while preserving order, then sort
        seen = set()
        unique_requirements = []
        for req in matched_requirements:
            if req not in seen:
                seen.add(req)
                unique_requirements.append(req)
        
        for req in sorted(unique_requirements):
            f.write(req + '\n')
        
        # if unmatched_imports:
        #     f.write('\n# The following imports were found in notebooks but not in requirements_docker_image.txt:\n')
        #     f.write('# These may need to be added manually:\n')
        #     for imp in sorted(unmatched_imports):
        #         f.write(f"# {imp}\n")
    
    print(f"\n✅ Created {output_file}")
    print(f"   - {len(seen)} total packages included")
    print(f"   - {len(MANUAL_PACKAGES)} manually curated packages")
    print(f"   - {len(seen) - len(MANUAL_PACKAGES)} packages from imports matching")
    print(f"   - {len(unmatched_imports)} imports may need manual addition")
    
    return list(seen), list(unmatched_imports)

if __name__ == "__main__":
    print("🔍 Filtering requirements_docker_image.txt based on BENCHMARK notebook imports...")
    print("=" * 60)
    
    # Extract imports only from benchmark notebooks
    imports = extract_benchmark_imports(path_imports, path_nbs)
    
    # Show some sample imports
    print(f"\nSample imports found: {sorted(list(imports))[:10]}")
    
    # Filter requirements_docker_image.txt
    print("\n📝 Filtering requirements_docker_image.txt...")
    print("-" * 40)
    matched, unmatched = filter_requirements_by_imports(imports)
    
    if unmatched:
        print(f"\n🔍 Unmatched imports to investigate:")
        for imp in sorted(unmatched):
            print(f"     {imp}")