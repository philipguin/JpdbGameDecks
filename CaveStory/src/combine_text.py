import os
import sys

def merge_files(order_path, input_path, output_path):

    with open(order_path, 'r', encoding='utf-8') as order_file:
        file_paths = order_file.read().splitlines()

    with open(output_path, 'w', encoding='utf-8') as output_file:
        for file_path in file_paths:
            input_file_path = os.path.join(input_path, file_path)
            if os.path.exists(input_file_path):
                with open(input_file_path, 'r', encoding='utf-8') as input_file:
                    output_file.write(input_file.read())
                    output_file.write('\n')  # Add a newline to separate files
            else:
                print(f"Warning: {file_path} does not exist, skipping.")
        
    print(f"Finished!")

if len(sys.argv) != 4:
    print("Usage: python combine_text.py  <file_order_file> <input_dir> <output_file>")
    sys.exit(1)

merge_files(sys.argv[1], sys.argv[2], sys.argv[3])
