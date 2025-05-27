import os
import random
import shutil
import zipfile
import tarfile
from collections import defaultdict

def sample_images_per_class(input_dir, output_dir, num_images=10):
    """
    Samples a few images per subfolder and preserves the directory structure.

    Args:
        input_dir (str): Path to the main dataset folder.
        output_dir (str): Path to save the sampled dataset.
        num_images (int): Number of images to sample per class.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    is_subclass = False
    # Loop through each subfolder (class)
    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)

        # Check if it's a directory
        if os.path.isdir(class_path):
            is_subclass = True
            # List all images in the subfolder
            images = [img for img in os.listdir(class_path)] # if img.lower().endswith(('.png', '.jpg', '.jpeg'))
            
            # Skip empty folders
            if not images:
                continue
            
            # Sample a fixed number of images (or all if fewer exist)
            sampled_images = random.sample(images, min(num_images, len(images)))

            # Create corresponding output subfolder
            output_class_path = os.path.join(output_dir, class_name)
            os.makedirs(output_class_path, exist_ok=True)

            # Copy sampled images to the new directory
            for img in sampled_images:
                src = os.path.join(class_path, img)
                dst = os.path.join(output_class_path, img)
                shutil.copy2(src, dst)

            print(f"Copied {len(sampled_images)} images from '{class_name}'.")

    # sample directly from the folder
    if not is_subclass:
        # List all images in the subfolder
        images = [img for img in os.listdir(input_dir) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Skip empty folders
        if images:
            # Sample a fixed number of images (or all if fewer exist)
            sampled_images = random.sample(images, min(num_images, len(images)))
            # Copy sampled images to the new directory
            for img in sampled_images:
                src = os.path.join(input_dir, img)
                dst = os.path.join(output_dir, img)
                shutil.copy2(src, dst)

            print(f"Copied {len(sampled_images)} images.")

    print("✅ Sampling complete!")


def sample_unzip_across_folders(archive_path, output_dir, proportion=0.1, seed=42):
    random.seed(seed)

    def extract_sample_from_dict(file_dict, extractor_func):
        for folder, files in file_dict.items():
            sample_size = max(1, int(len(files) * proportion))
            sampled_files = random.sample(files, sample_size)
            for file in sampled_files:
                extractor_func(file)

    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as archive:
            files_by_folder = defaultdict(list)
            for file in archive.namelist():
                if file.endswith('/'):
                    continue
                parts = file.split('/')
                top_folder = parts[0] if len(parts) > 1 else 'root'
                files_by_folder[top_folder].append(file)

            extract_sample_from_dict(files_by_folder, lambda f: archive.extract(f, output_dir))

    elif archive_path.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2')):
        with tarfile.open(archive_path, 'r:*') as archive:
            files_by_folder = defaultdict(list)
            for member in archive.getmembers():
                if member.isdir():
                    continue
                parts = member.name.split('/')
                top_folder = parts[0] if len(parts) > 1 else 'root'
                files_by_folder[top_folder].append(member)

            extract_sample_from_dict(files_by_folder, lambda m: archive.extract(m, output_dir))

    else:
        raise ValueError("Unsupported archive format. Please provide a .zip or .tar[.gz/.bz2/.xz/.tgz] file.")

    print(f"Sampled extraction completed in '{output_dir}'.")


# Example usage
# input_folder = r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\0_new_new_samples\sidhantssrivastava_cnn-yoga\data\yoga_poses\train"
# output_folder = r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\0_new_new_samples\sidhantssrivastava_cnn-yoga\data_small\yoga_poses\train"
# sample_images_per_class(input_folder, output_folder, num_images=10)

input_zip = r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\0_new_new_samples\ashioyajotham_pytorch-image-classifier\flower_data1.tar"
output_folder = r"C:\Users\yirwa29\Downloads\Dataset-Nb\Docker_kaggle_env\0_new_new_samples\ashioyajotham_pytorch-image-classifier\data_small\flower_data"
sample_unzip_across_folders(input_zip, output_folder, proportion=0.1)