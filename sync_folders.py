import os               # Module to interact with the operating system for file operations.
import shutil           # Module for high-level file operations like copying and removing.
import time             # Module to handle time-related functions like sleep.
import hashlib          # Module to calculate file hashes (MD5) for comparison.
import argparse         # Module to parse command-line arguments.
import logging          # Module to handle logging of information and errors.


def calculate_md5(file_path):
    """Calculate MD5 checksum of a file to check if two files are identical."""
    hash_md5 = hashlib.md5()  # Create a new md5 hash object.
    with open(file_path, "rb") as f:  # Open the file in binary mode.
        # Read the file in chunks to handle large files.
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)  # Update the hash object with the data chunk.
    return hash_md5.hexdigest()  # Return the hex representation of the checksum.

def synchronize_folders(source, replica, logger):
    """Synchronize the replica folder with the source folder."""
    # Traverse the source folder and replicate its structure and contents in the replica folder.
    for root, dirs, files in os.walk(source):
        # Determine the relative path of the current directory.
        rel_path = os.path.relpath(root, source)
        # Determine the corresponding directory in the replica.
        replica_root = os.path.join(replica, rel_path)

        # If the replica directory doesn't exist, create it.
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            logger.info(f"Created directory: {replica_root}")  # Log the directory creation.
        
        # Copy files from the source to the replica.
        for file_name in files:
            source_file = os.path.join(root, file_name)  # Full path of the source file.
            replica_file = os.path.join(replica_root, file_name)  # Full path of the replica file.
            
            # If the file doesn't exist in the replica or the files are different (based on MD5), copy it.
            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)  # Copy the file with metadata.
                logger.info(f"Copied: {source_file} to {replica_file}")  # Log the file copy operation.
        
        # Remove files from the replica that are not in the source.
        for file_name in os.listdir(replica_root):
            if file_name not in files:  # If the file is not in the source directory.
                replica_file = os.path.join(replica_root, file_name)
                os.remove(replica_file)  # Remove the file from the replica.
                logger.info(f"Removed: {replica_file}")  # Log the file removal.
    
    # Remove empty directories from the replica (cleanup).
    for root, dirs, files in os.walk(replica, topdown=False):  # Traverse from bottom to top.
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # If the directory is empty.
                os.rmdir(dir_path)  # Remove the directory.
                logger.info(f"Removed empty directory: {dir_path}")  # Log the directory removal.

def main():
    # Set up command-line argument parsing.
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('source', help='Path to the source folder')  # Path to the source folder.
    parser.add_argument('replica', help='Path to the replica folder')  # Path to the replica folder.
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')  # Time interval for synchronization.
    parser.add_argument('log_file', help='Path to the log file')  # Path to the log file.
    
    args = parser.parse_args()  # Parse the command-line arguments.

    # Configure logging to log both to a file and to the console.
    logging.basicConfig(filename=args.log_file, level=logging.INFO,
                        format='%(asctime)s - %(message)s')  # Log to the specified log file.
    logger = logging.getLogger()  # Get the logger instance.
    
    # Log to the console as well.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Main loop: Synchronize the folders at the specified interval.
    while True:
        try:
            logger.info("Starting synchronization...")  # Log the start of synchronization.
            synchronize_folders(args.source, args.replica, logger)  # Call the synchronization function.
            logger.info("Synchronization completed.")  # Log the completion of synchronization.
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")  # Log any errors during synchronization.
        
        time.sleep(args.interval)  # Wait for the specified interval before the next synchronization.

if __name__ == '__main__':
    main()  # Execute the main function when the script is run directly.
