import os
import sys

if len(sys.argv) != 4:
    print("Usage: python bulk_change_prefix.py <directory_path> <old_prefix> <new_prefix>")
    sys.exit(1)

directory_path = sys.argv[1]
old_prefix = sys.argv[2]
new_prefix = sys.argv[3]

old_prefix_len = len(old_prefix)
count = 0

for filename in os.listdir(directory_path):
    if filename.startswith(old_prefix):
        new_filename = new_prefix + filename[old_prefix_len:]
        old_file_path = os.path.join(directory_path, filename)
        new_file_path = os.path.join(directory_path, new_filename)
        os.rename(old_file_path, new_file_path)
        count += 1

print(f"Renamed {count} files.")
