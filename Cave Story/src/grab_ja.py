import requests
from bs4 import BeautifulSoup
import os
import csv
import sys
import shutil

# Ensure the output directory is passed as a command line argument
if len(sys.argv) != 2:
    print("Usage: python grab_ja.py <output_directory>")
    sys.exit(1)

# Get the output directory from the command line argument
output_dir = sys.argv[1]

# Clear the output directory on start
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Get URLs to process
url_prefix = "https://www.cavestory.org/game-info/tsc-script.php/ja/"
csv_file_path = 'urls_and_names.csv'
file_urls = []
file_titles = []
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        file_urls.append(row[0])
        file_titles.append(row[1])

def get_content_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find('div', {'id': 'atcont0'})
        if content_div:
            pre_tag = content_div.find('pre')
            if pre_tag:
                return pre_tag.text
    return None

for i in range(len(file_urls)):
    url = url_prefix + file_urls[i]
    title = file_titles[i]
    content = get_content_from_url(url)
    if content:
        filename = os.path.join(output_dir, title + '.txt')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as file: file.write(content)
        print(f"Content saved to {filename}")
    else:
        print(f"Failed to extract content from {url}")

print("Done")
