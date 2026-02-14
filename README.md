# JunoBench Source Code Repository

This is the source code repository for our paper "[*JunoBench: A Benchmark Dataset of Crashes in Python Machine Learning Jupyter Notebooks*](https://arxiv.org/abs/2510.18013)" which constructs a benchmark dataset of crashes in Python ML notebooks, with a balanced coverage of popular ML libraries. It also covers notebook-specific out-of-order execution issues.

The constructed benchmark - JunoBench can be found on [Hugging Face](https://huggingface.co/datasets/PELAB-LiU/JunoBench).

## Data collection

Our **data source** is the published data, [data_jupyter_nbs_empirical](https://doi.org/10.5281/zenodo.14070487), from the previous empirical study [1]. 

* We first use the labeled dataset (*data_jupyter_nbs_empirical/Manual_labeling*) from the empirical study. Inside the excel file (*cluster_sampled_labeled_final.xlsx*), we **filtered** the labeled crashes:
    + using only Kaggle notebooks (nb_source == *1*);
    + keeping only ML bugs (label_if_ML_bug == *ML/data science library related (ML imports, error raised by library)*) and notebook-specific issues (label_root_cause == *nb specific ...*);
    + excluding root cause being as environment-related (i.e., *module not installed, change of environment, file/path not found or exist, library versions incompatible, settings(permission, environment), external control (window closed), insufficient resources, and error inside library*)
* Then we **resampled** additional unlabeled Kaggle crashes based on the file containing all kaggle crashes in the released dataset (*data_jupyter_nbs_empirical/Clustering/clusters_Kaggle_final.xlsx*).
    + [resample_error_nbs.py](./resample_error_nbs.py)
* For the unlabeled crashes, we implemented a lightweight tool to automatically estimate the ML libraries that are in use when the crashes occur.
    + [auto_library_cause.py](./auto_library_cause.py)
* The ML library cause estimation tool is tested against the labeled crashes and achieved an accurarcy of 80%.
    + [test_auto_library_cause.ipynb](./test_auto_library_cause.ipynb)

## Benchmark construction

* We first retrieved information about the **input datasets** associated with the notebooks in our dataset, using the [KGTorrent](https://github.com/collab-uniba/KGTorrent) [2] with the [Meta Kaggle dataset](https://www.kaggle.com/datasets/kaggle/meta-kaggle). The information includes dataset titles, licenses, and downloading links. 

* We use the links to download the input datasets required to reproduce each crashing notebook. For large dataset, we downsampled them if possible:
    + [dataset_sample.py](./dataset_sample.py)

* For the four datasets with private licenses, we replace them with synthetic datasets:
    + [dataset_synthetic.py](./dataset_synthetic.py)

* For each notebook, we retain the original notebook and create a **reproduced version** where we manually reproduce the crash, and a **fixed version** where we manually allocate and repair the root cause while preserving the original intent of the developer.

* We **manually validated** the labels of the labaled dataset during the reproducing and fixing process, and found 7 out of 74 cases with incorrect root cause labels:

    | fname | eid | ename | evalue | library_cause | root_cause |
    |----|----|----|----|----|----|
    | 60034e_item-demand-sarima.ipynb  |  a92d34a3-1c75-3575-bfbc-08543c41a9b1  |  valueerror  |  could not broadcast input array from shape (92,) into shape (181,)  |  statsmodels  |  **data confusion -> API misuse**  |
    | ef7972_clase-1-modulo-4.ipynb  |  0632671a-dd6f-30b9-93b8-e2a121561569  |  valueerror  |  columns overlap but no suffix specified: Index(['name_count'], dtype='object')  |  pandas  |  **data confusion -> API misuse**  |
    | 19f92e_mcm2023-c-1-b-lr.ipynb  |  698da925-8121-3961-92ac-9445e54cad54  |  valueerror  |  operands could not be broadcast together with shapes (68,) (272,)  |  **sklearn -> None**  | **data confusion -> nb specific (execution order)** |
    | d38a44_machado-dom-casmurro-pytorch.ipynb  |  f3fcfa58-4438-3b6f-a471-b7ece7c3ee71  |  runtimeerror  |  one of the variables needed for gradient computation has been modified by an inplace operation  |  torch  |  **unknown -> wrong implementation**  |
    | 4a8b2c_amell.ipynb  |  4e2518d8-4c04-38c4-98f4-6d402cc01c9f  |  runtimeerror  |  Given groups=1, weight of size [64, 3, 7, 7], expected input[3, 256, 256, 1] to have 3 channels, but got 256 channels instead  |  torchvision  |  **ML model mismatch -> wrong implementation** |
    | 52c815_23205-pss3e5.ipynb  |  3e0645e7-6fed-3afe-ac64-83f9ec38f16b  |  valueerror  |  Input contains NaN, infinity or a value too large for dtype('float64').  |  **Optuna -> lightgbm**  |  **unknown -> data confusion**  |
    | 4ac82e_fer-2013-facial-expression-recognition-detection..pynb  |  b6935f7d-9c9b-3c57-8888-0d8ead2ec1a9  |  error  |  OpenCV(4.8.1) /io/opencv/modules/imgproc/src/color.cpp:182: error: (-215:Assertion failed) !_src.empty() in function 'cvtColor'  |  cv2  |  **unknown -> environment issue (external control)**  |


* For the crashes we included in the benchmark from the resampled notebooks (37/500), we **manually labeled** them following the dimensions established in our empirical study [1].

* Overall, 111 notebooks with crashes are included in [JunoBench](https://huggingface.co/datasets/PELAB-LiU/JunoBench). The description of the benchmark dataset can be found in [benchmark_desc.xlsx](data/benchmark_desc.xlsx).
The statistics about JunoBench can be found in: [statistics_benchmark_all.ipynb](./statistics_benchmark_all.ipynb).

## Docker environment

### Provided docker environment
We built a unified Docker image to reproduce all notebooks in JunoBench. This image includes the Kaggle notebook platform environment as well as all libraries required by all the notebooks in JunoBench.

The image is based on the official Kaggle CPU Docker image (*sha256:0b88fd200569a8649c3297b22a1795f9efd71701cb3dd4af7222864e727a8c0d*) and is built using our [fork of the official Kaggle repository](https://github.com/yarinamomo/docker-kaggle-python).

On top of this base image, we installed all Python libraries required by the notebooks in JunoBench. The complete list of dependencies can be found in the “benchmark dataset related” section of [requirement.txt](data/requirements.txt).

The final Docker image is compiled and publicly available on [DockerHub](https://hub.docker.com/repository/docker/yarinamomo/kaggle_python_env) with digest (*sha256:73380761b1f37a83aef2c247a9d725c796c6196abf14bccc92b92b25c7eb81b9*).

### Built own docker environment (simplified)
We also provide instructions for users who prefer to build a simplified Docker image themselves. This image includes essential Jupyter-related libraries along with the dependencies required by the ML notebooks in JunoBench, but excludes the Kaggle web-based platform. It is suitable for specialized hardware environments or for users who want a smaller, more lightweight image.

The corresponding setup details and Dockerfiles are available in the [docker](docker/) directory. For step-by-step instructions, please refer to [Docker_ReadMe](docker/README.md).

## Potential research opportunities - LLM as a crash detector

Here we explore the usage of JunoBench for evaluating LLMs in crash detection for ML notebooks. The related code, results, and intermediate data can be found in 📁 [`llms`](./llms/)

### Experimental setup

* Goal: Given all the successfully executed code cells of a notebook, predict whether a target cell will crash if next to execute.

* Evaluated LLMs: 
    + llama3.3:70b, 
    + mistral-small3.1:latest (24B)

* Prediction:
    + 5 runs/notebook
    + independently run on both **buggy** version (ground truth: **TRUE**) and **fixed** version (ground truth: **FALSE**) of each case
    + Skip when exceeding max tokens of the LLMs
        + llama3.3:70b: Skipped 11 cases for each versions
        + mistral-small3.1:latest (24B): Skipped 3 cases for each versions

* Input user message:
    + All successfully executed code cells, in execution order. 
    + Target cell (the crashing cell in the reproduced buggy version, cell with the same cell id in the fixed version)
    + Removed cell output/error information/comments in the code

* Expected output:
    + TRUE: crash
    + FALSE: not crash
    
* Evaluation Metrics:
    + Accurarcy with majority votes strategy


### Results


| LLMs (version)<br>/Crash | mistral-small3.1:latest<br>(Buggy) | mistral-small3.1:latest<br>(Fixed) | llama3:70b<br>(Buggy) | llama3:70b<br>(Fixed) |
|----------|----------|----------|----------|----------|
| NBspecific | 15 / 20 | 7 / 20  | 16 / 18 | 4 / 18  |
| pandas     | 6 / 15  | 10 / 15 | 11 / 15 | 7 / 15  |
| numpy      | 8 / 13  | 7 / 13  | 5 / 12  | 10 / 12 |
| sklearn    | 7 / 15  | 13 / 15 | 6 / 14  | 12 / 14 |
| tensorflow/keras | 12 / 15 | 11 / 15 | 8 / 15 | 7 / 15 |
| torch      | 10 / 14 | 5 / 14  | 6 / 12 | 9 / 12 |
| matplotlib | 3 / 6   | 4 / 6   | 2 / 5  | 2 / 5  |
| seaborn    | 1 / 6   | 5 / 6   | 3 / 5  | 4 / 5  |
| statsmodels| 0 / 2   | 2 / 2   | 0 / 2  | 1 / 2  |
| lightgbm   | 0 / 1   | 1 / 1   | 0 / 1  | 1 / 1  |
| torchvision| 1 / 1   | 0 / 1   | 1 / 1  | 0 / 1  |
| **Total** | **63 / 108** | **65 / 108** | **58 / 100** | **57 / 100** |


### References

[1] Wang, Yiran, Willem Meijer, José Antonio Hernández López, Ulf Nilsson, and Dániel Varró, "Why do Machine Learning Notebooks Crash? An Empirical Study on Public Python Jupyter Notebooks," in IEEE Transactions on Software Engineering, doi: 10.1109/TSE.2025.3574500.

[2] Quaranta, Luigi, Calefato, Fabio, & Lanubile, Filippo. (2021). collab-uniba/KGTorrent: First release (v. 1.0.0) of KGTorrent (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.4472990