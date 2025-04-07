import os
import sys

def is_esp32c3():
    """
    Check if the code is running on an ESP32C3 device.
    
    Returns:
        bool: True if running on ESP32C3, False otherwise.
    """
    try:
        #Check using os.uname() in MicroPython
        if hasattr(os, 'uname'):
            uname_info = os.uname()
            if hasattr(uname_info, 'machine') and 'ESP32C3' in uname_info.machine:
                return True
        
        return False
    except Exception as e:
        print(f"Error checking for ESP32C3: {e}")
        return False

def is_directory(path):
    """Check if path is a directory by trying to list its contents."""
    try:
        os.listdir(path)
        return True
    except:
        return False

def recursive_rmdir(directory):
    """
    Recursively remove a directory and all its contents without using os.path.
    
    Args:
        directory (str): Path to directory to be removed
    """
    try:
        for item in os.listdir(directory):
            item_path = directory + "/" + item if directory.endswith("/") else directory + "/" + item
            try:
                # Try to list contents to see if it's a directory
                os.listdir(item_path)
                # If we get here, it's a directory
                recursive_rmdir(item_path)
            except:
                # If we can't list contents, it's a file
                os.remove(item_path)
                print(f"Deleted file: {item_path}")
        
        # After all contents are removed, remove the directory itself
        os.rmdir(directory)
        print(f"Deleted directory: {directory}")
    except Exception as e:
        print(f"Error while deleting {directory}: {e}")

def delete_webpage_contents():
    """
    Delete all contents of the /webpage folder.
    Only executes if running on an ESP32C3 device.
    """
    if not is_esp32c3():
        print("Safety check failed: Not running on ESP32C3. Deletion aborted.")
        return False
    
    webpage_path = "/webpage"
    
    # Check if the path exists by trying to access it
    try:
        os.listdir(webpage_path)
    except:
        print(f"The directory {webpage_path} does not exist.")
        return False
    
    try:
        # Walk through the directory and delete all contents
        for item in os.listdir(webpage_path):
            item_path = webpage_path + "/" + item
            try:
                # Try to list contents to see if it's a directory
                os.listdir(item_path)
                # If we get here, it's a directory
                recursive_rmdir(item_path)
            except:
                # If we can't list contents, it's a file
                os.remove(item_path)
                print(f"Deleted file: {item_path}")
        
        print(f"Successfully deleted all contents of {webpage_path}")
        return True
    except Exception as e:
        print(f"Error deleting contents of {webpage_path}: {e}")
        return False
