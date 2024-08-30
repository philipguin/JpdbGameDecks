import os
import yaml
import re
import csv
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
    contribs_sorted =  sorted(contributors.items(), key=lambda x: -x[1]) # from most to least decks
    contrib_names = list(f'<span class="contributor" title="Decks Contributed: {count}">{k}</span>' for k, count in contribs_sorted)

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

def accumulate_csv_counts(counter, csv_path):
    with open(csv_path, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            key = (row[0], row[1])
            count = int(row[2])
            counter[key] += count

def output_tsv_decks(output_file, yaml_infos):

    is_first = True
    for game_dir, info in yaml_infos:
        name = info.get('name') or ''
        progress = info.get('progress') or '??%'
        store_links = info.get('store-links')
        difficulty = info.get('difficulty') or ''
        difficulty_source = info.get('difficulty-source') or ''
        sortedness = info.get('sortedness') or ''
        quality = info.get('quality', '') or ''
        deck_author = info.get('deck-author') or ''
        notes_and_sources = info.get('notes-and-sources') or ''
        include_filter = info.get('include-filter')
        exclude_filter = info.get('exclude-filter')

        links_out = '' if not store_links else '|'.join(store_links)
        notes_and_sources = notes_and_sources.replace('\n', '\\n').replace('\t', '  ')

        include_pattern = re.compile(include_filter) if include_filter else None
        exclude_pattern = re.compile(exclude_filter) if exclude_filter else None

        deck_paths = []
        word_counts = Counter()
        for root, _, files in os.walk(game_dir):
            root = root.replace('\\', '/')
            if '/src/' in root or root.endswith('/src'): continue
            
            for file in files:
                if not file.endswith('.csv'): continue

                file_path = os.path.join(root, file)
                file_path_test = os.path.relpath(file_path, game_dir).replace('\\', '/').lstrip('./')

                tsv_path = file_path.replace('\\', '/').replace('|', '\\|')
                tsv_path = tsv_path[tsv_path.index('/') + 1:]
                deck_paths.append(tsv_path)

                is_match = True
                if include_pattern and not include_pattern.fullmatch(file_path_test): is_match = False
                elif exclude_pattern and exclude_pattern.fullmatch(file_path_test): is_match = False
                if is_match:
                    accumulate_csv_counts(word_counts, file_path)

        unique_word_count = len(word_counts)
        word_count = word_counts.total()
        #print(f'{game_dir}:\t{unique_word_count}\t{word_count}')

        row = [
            name,
            progress,
            links_out,
            difficulty,
            difficulty_source,
            sortedness,
            quality,
            unique_word_count,
            word_count,
            deck_author,
            '|'.join(deck_paths),
            notes_and_sources, # most likely to cause format error, so we'll put it last
        ]
        if is_first: is_first = False
        else: output_file.write('\n')
        output_file.write('\t'.join(str(x) for x in row))

def main():
    decks_dir = 'decks'
    yaml_infos = []
    invalid_files = []

    for root in os.scandir(decks_dir):
        if not root.is_dir(): continue
        if root.name.startswith('.'): continue

        for file in os.listdir(root):
            if file == 'info.yml' or file == 'info.yaml':
                file_path = os.path.join(root, file)
                if validate_yaml(file_path):
                    yaml_infos.append((os.path.join(decks_dir, root.name), scrape_info(file_path)))
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
    try: main()
    except KeyboardInterrupt: sys.exit(0)
