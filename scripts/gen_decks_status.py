import os
import yaml
import re
from collections import Counter

def validate_yaml(yaml_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            yaml.safe_load(file)
        return True

    except yaml.YAMLError as e:
        print(f"Error in {yaml_file}: {e}")
        return False

def scrape_info(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def is_progress_complete(x): # NOTE: logic duplicated in decks.js
    x = x.lower()
    return x == 'complete' or x == '100' or x == '100%'

def output_tsv_metrics(output_file, yaml_infos):

    count_complete = sum(is_progress_complete(x.get('progress', '')) for _, x in yaml_infos)
    count_wip = len(yaml_infos) - count_complete
    
    contributors = Counter(x.get('deck-author', '') for _, x in yaml_infos)
    contrib_names = list(f'{k} ({count})' for k, count in sorted(contributors.items(), key=lambda x: -x[1])) # from most to least decks

    metrics = [
        ['Decks Complete', str(count_complete)],
        ['Decks In-Progress', str(count_wip)],
        ['Contributors', ", ".join(contrib_names)],
    ]

    is_first = True
    for metric in metrics:
        if is_first: is_first = False
        else: output_file.write('\n')

        output_file.write(metric[0] + '\t' + metric[1])

def output_tsv_decks(output_file, yaml_infos):

    is_first = True
    for _, info in yaml_infos:
        name = info.get('name') or ''
        progress = info.get('progress') or '??%'
        store_links = info.get('store-links')
        difficulty = info.get('difficulty') or ''
        difficulty_source = info.get('difficulty-source') or ''
        sortedness = info.get('sortedness') or ''
        quality = info.get('quality', '') or ''
        deck_author = info.get('deck-author') or ''
        notes_and_sources = info.get('notes-and-sources') or ''

        links_out = '' if not store_links else '|'.join(store_links)
        notes_and_sources = notes_and_sources.replace('\n', '\\n').replace('\t', '  ')

        row = [
            name,
            progress,
            links_out,
            difficulty,
            difficulty_source,
            sortedness,
            quality,
            deck_author,
            notes_and_sources, # most likely to cause format error, so we'll put it last
        ]
        if is_first: is_first = False
        else: output_file.write('\n')
        output_file.write('\t'.join(str(x) for x in row))

def main():
    base_dir = os.getcwd()
    yaml_infos = []
    invalid_files = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == 'info.yml' or file == 'info.yaml':
                file_path = os.path.join(root, file)
                if validate_yaml(file_path):
                    yaml_infos.append((file_path, scrape_info(file_path)))
                else:
                    invalid_files.append(file_path)

    if invalid_files:
        print("The following info.yaml files are invalid:")
        for invalid_file in sorted(invalid_files):
            print(f" - {invalid_file}")
        exit(1)
    else:
        print("All info.yml files are valid. Generating metrics and composite table...")
        yaml_infos.sort(key=lambda x: x[0])

        if not os.path.exists('docs/_includes'): os.makedirs('docs/_includes')

        with open('docs/deck-metrics.tsv', 'w', encoding='utf-8') as output_file:
            output_tsv_metrics(output_file, yaml_infos)

        print("Metrics written to docs/_includes/deck-metrics.html")

        with open('docs/decks.tsv', 'w', encoding='utf-8') as output_file:
            output_tsv_decks(output_file, yaml_infos)
        
        print("Table written to docs/decks.tsv")


if __name__ == "__main__":
    main()
