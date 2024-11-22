import os
import shutil

def organize_kdef_images(kdef_root):
    # Define the target folders to be created
    target_folders = ["happy", "neutral", "sad"]
    
    # Create target folders in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_paths = {emotion: os.path.join(script_dir, emotion) for emotion in target_folders}
    
    # Create folders if they don't exist
    for path in target_paths.values():
        os.makedirs(path, exist_ok=True)
    
    # Emotion codes for identification
    emotion_mapping = {
        "happy": "HAS.JPG",
        "neutral": "NES.JPG",
        "sad": "SAS.JPG"
    }
    
    # Iterate over each subject folder in the root directory
    for subject_folder in os.listdir(kdef_root):
        subject_path = os.path.join(kdef_root, subject_folder)
        if os.path.isdir(subject_path):  # Ensure it's a directory
            # Check for images matching the required emotion codes
            for emotion, filename_suffix in emotion_mapping.items():
                image_file = f"{subject_folder}{filename_suffix}"
                image_path = os.path.join(subject_path, image_file)
                
                if os.path.isfile(image_path):  # Check if the image exists
                    target_path = target_paths[emotion]
                    shutil.copy(image_path, target_path)  # Copy the file to the target folder
                    print(f"Copied {image_file} to {emotion} folder.")
    
    print("All relevant images have been organized!")

# Example usage:
# Provide the root directory of the KDEF dataset as input
kdef_root = input("Enter the path to the root folder of the KDEF dataset: ").strip()
organize_kdef_images(kdef_root)