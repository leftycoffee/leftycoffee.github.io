import os
import shutil
from PIL import Image

def resize_image(file_path, resize_factor=0.7):
    # Open an image file
    with Image.open(file_path) as img:
        # Calculate the new size
        new_size = tuple([int(dim * resize_factor) for dim in img.size])
        # Resize the image
        img_resized = img.resize(new_size, Image.LANCZOS)
        # Save the resized image back to the same path
        img_resized.save(file_path)
        print(f"Resized image: {file_path}")

def backup_and_resize_images(folder, backup_folder, size_threshold=1 * 1024 * 1024):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".jpg"):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > size_threshold:
                    # Create backup folder if it doesn't exist
                    if not os.path.exists(backup_folder):
                        os.makedirs(backup_folder)
                    # Backup the original file
                    backup_path = os.path.join(backup_folder, os.path.relpath(file_path, folder))
                    backup_dir = os.path.dirname(backup_path)
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    shutil.copy2(file_path, backup_path)
                    print(f"Backed up original image: {file_path} to {backup_path}")
                    # Resize the image
                    resize_image(file_path)

if __name__ == "__main__":
    folder_to_check = "."  # Replace with the path to the folder you want to check
    backup_folder = "/home/ketvin/backup"  # Replace with the path to the backup folder
    backup_and_resize_images(folder_to_check, backup_folder)

