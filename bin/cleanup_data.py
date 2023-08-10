import os
import time
import shutil

print("Deleting all data older than 14 days!")
# Relative path to the data directory from the bin folder
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
current_time = time.time()

# Define the age threshold
two_weeks_in_seconds = 14 * 24 * 60 * 60  # 14 days converted to seconds

for folder_name in os.listdir(data_path):
    folder_path = os.path.join(data_path, folder_name)
    
    # Ensure the item is a directory
    if os.path.isdir(folder_path):
        folder_creation_time = os.path.getctime(folder_path)
        
        # If the folder is older than the threshold, delete it
        if (current_time - folder_creation_time) > two_weeks_in_seconds:
            shutil.rmtree(folder_path)  # This will delete non-empty directories
            print(f"Deleted {folder_path}")

print("Cleanup complete!")