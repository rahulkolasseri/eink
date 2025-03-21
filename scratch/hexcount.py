import sys
from collections import Counter

def print_unique_hex_codes(file_path):
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Read all bytes from the file
            binary_data = file.read()
        
        # Count occurrences of each byte
        byte_counter = Counter(binary_data)
        
        # Print unique hex codes
        print(f"Found {len(byte_counter)} unique byte values in {file_path}:")
        for byte, count in sorted(byte_counter.items()):
            print(f"0x{byte:02X}: {count} occurrences")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <binary_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print_unique_hex_codes(file_path)
