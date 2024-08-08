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


def is_progress_complete(x):
    x = x.lower()
    return x == 'complete' or x == '100' or x == '100%'

def output_html_metrics(output_file, yaml_infos):

    count_complete = sum(is_progress_complete(x.get('progress', '')) for _, x in yaml_infos)
    count_wip = len(yaml_infos) - count_complete
    
    contributors = Counter(x.get('deck-author', '') for _, x in yaml_infos)
    contrib_names = list(k for k, _ in sorted(contributors.items(), key=lambda x: -x[1])) # from most to least decks

    metrics = [
        f'Decks Complete: {count_complete}',
        f'Decks In-Progress: {count_wip}',
        f'Contributors ({len(contributors)}): {", ".join(contrib_names)}',
    ]
    output_file.write("<ul>\n")
    for metric in metrics:
        output_file.write(f'  <li>{metric}</li>\n')
    output_file.write("</ul>\n")

def output_tsv_decks(output_file, yaml_infos):

    difficulty_colors = [
        '#FFFFFF',
        '#00FF00',
        '#32FF00',
        '#64FF00',
        '#96FF00',
        '#C8FF00',
        '#FFFF00',
        '#FFC800',
        '#FF9600',
        '#FF6400',
        '#FF3200',
        '#FF0000',
    ]

    def get_difficulty_index(value):

        if value is None: return 0
        if type(value) is int: return value
        if type(value) is float: return round(value)
        if type(value) is not str: raise ValueError(f'Difficulty of unhandled type {type(value)}"')

        match_unknown = re.match(r'^[\?\s]+$', value)
        if match_unknown:
            return 0

        # Check if the input matches the first format (e.g., "12" or "12?")
        match_single = re.match(r'^\s*(\d+)(\s*\?)?\s*$', value)
        if match_single:
            return int(match_single.group(1))
        
        # Check if the input matches the second format (e.g., "12-15" or "12-15?")
        match_range = re.match(r'^\s*(\d+)\s*\-\s*(\d+)(\s*\?)?\s*$', value)
        if match_range:
            num1 = int(match_range.group(1))
            num2 = int(match_range.group(2))
            return round((num1 + num2) / 2)
        
        raise ValueError(f'Difficulty format not recognized: "{value}"')

    is_first = True
    for _, info in yaml_infos:
        name = info.get('name') or ''
        store_links = info.get('store-links')
        difficulty = info.get('difficulty')
        difficulty_source = info.get('difficulty-source')
        progress = info.get('progress') or '??%'
        sortedness = info.get('sortedness') or ''
        quality = info.get('quality', '') or ''
        notes_and_sources = info.get('notes-and-sources') or '' # never allow None
        deck_author = info.get('deck-author') or ''

        if type(quality) is str and quality.endswith('?'): quality = f'<font color="#f8f">{quality[:-1]}</font>'
        if type(sortedness) is str and sortedness.endswith('?'): sortedness = f'<font color="#f8f">{sortedness[:-1]}</font>'

        title = name
        if not is_progress_complete(progress): title = f'{title} ({progress})'

        links_out = '' if not store_links else ';'.join(store_links)

        if difficulty is None:
            difficulty = ''
        else:
            diff_color = difficulty_colors[get_difficulty_index(difficulty)]
            if type(difficulty) is str: difficulty = difficulty.replace("-", "&#8209;") # non-breaking hyphen
            difficulty = f'<font color="{diff_color}">{difficulty}</font>'
            if difficulty_source:
                difficulty = f'{difficulty}&nbsp;<sub>{difficulty_source}</sub>'

        if is_first: is_first = False
        else: output_file.write('\n')

        row = [
            title,
            links_out,
            difficulty,
            sortedness,
            quality,
            notes_and_sources,
            deck_author,
        ]
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

        with open('docs/_includes/deck-metrics.html', 'w', encoding='utf-8') as output_file:
            output_html_metrics(output_file, yaml_infos)

        print("Metrics written to docs/_includes/deck-metrics.html")

        with open('docs/decks.tsv', 'w', encoding='utf-8') as output_file:
            output_tsv_decks(output_file, yaml_infos)
        
        print("Table written to docs/decks.tsv")


if __name__ == "__main__":
    main()
