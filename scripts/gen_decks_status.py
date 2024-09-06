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

def output_metrics(output_file, yaml_infos):

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

    output_file.write('<ul>\n')
    for metric in metrics:
        output_file.write(f'  <li>{metric[0]}: {metric[1]}</li>\n')
    output_file.write('</ul>\n')


def format_name(name, progress):
    if is_progress_complete(progress): return str(name)
    return f"{name} ({progress})"

def data_for_link(url, game_title):
    if url.startswith('https://store.steampowered.com'): return 'icons/steam.svg', f"Steam store page for {game_title}"
    if url.startswith('https://www.gog.com'): return 'icons/gog.png', f"GOG store page for {game_title}"
    if url.startswith('https://store.epicgames.com'): return 'icons/epic_games.png', f"Epic Games store page for {game_title}"
    return 'icons/external_link.svg', f"Store page for {game_title}"

def format_store_links(links, game_title):
    if not links: return ''
    
    result = '<div class="store-links">'

    for link in links.split('|'):
        icon, alt = data_for_link(link, game_title)

        result += f'<a href="{link}" target="_blank" rel="noopener noreferrer">'
        result += f'<img src="{icon}" alt="{alt}" width="16" height="16">'
        result += '</a>'
    
    result += '</div>'
    return result

rgx_int = re.compile(r'^\s*(\d+)(\s*\?)?\s*$')
rgx_real = re.compile(r'^\s*(\d+\.\d*?|\d*\.\d+)(\s*\?)?\s*$')
rgx_int_range = re.compile(r'^\s*(\d+)\s*\-\s*(\d+)(\s*\?)?\s*$')

def parse_difficulty(value):
    if value is None or value == '':
        return '', 0

    match_int = rgx_int.match(value)
    if match_int:
        num = int(match_int.group(1))
        return num, num
    
    match_real = rgx_real.match(value)
    if match_real:
        num = float(match_real.group(1))
        return f"{num:.1f}", round(num)
    
    match_int_range = rgx_int_range.match(value)
    if match_int_range:
        num1 = int(match_int_range.group(1))
        num2 = int(match_int_range.group(2))
        num = (num1 + num2) * 0.5
        return f"{num1}-{num2}", round(num)
    
    raise ValueError(f"Difficulty format not recognized: \"{value}\"")

difficulty_colors = [
    '#FFFFFF', '#00FF00', '#32FF00', '#64FF00', '#96FF00', '#C8FF00',
    '#FFFF00', '#FFC800', '#FF9600', '#FF6400', '#FF3200', '#FF0000',
]

def format_difficulty(difficulty_str, diff_src=None):
    difficulty, color_idx = parse_difficulty(str(difficulty_str))
    color = difficulty_colors[color_idx]
    difficulty = f'<font color="{color}">{difficulty}</font>'
    
    if not diff_src: diff_src = "manual"
    
    return f'<span title="{diff_src}">{difficulty}</span>'

def format_sortedness(s):
    s = str(s)
    if s.endswith('?'): s = f'<font color="#f8f">{s[:-1]}</font>'
    return s

def format_quality(s):
    s = str(s)
    if s.endswith('?'): s = f'<font color="#f8f">{s[:-1]}</font>'
    return s

def format_unique_words(s):
    return str(s)


def accumulate_csv_counts(counter, csv_path):
    with open(csv_path, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            key = (row[0], row[1])
            count = int(row[2])
            counter[key] += count

def output_decks(html_out, tsv_out, yaml_infos):

    index = -1
    for game_dir, info in yaml_infos:
        index += 1

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

        tsv_row = [
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
        if index > 0: tsv_out.write('\n')
        tsv_out.write('\t'.join(str(x) for x in tsv_row))

        html_cols = [
            '', # blank for expander widget
            str(index), # name index
            format_name(name, progress),
            format_store_links(links_out, name),
            format_difficulty(difficulty, difficulty_source),
            format_sortedness(sortedness),
            format_quality(quality),
            format_unique_words(unique_word_count),
            #format_total_words(total_word_count, unique_word_count),
        ]
        html_out.write("<tr><td>" + "</td><td>".join(html_cols) + "</td></tr>\n")

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

        with open('docs/_includes/deck-metrics.html', 'w', encoding='utf-8') as output_file:
            output_metrics(output_file, yaml_infos)

        print("Metrics written to docs/_includes/deck-metrics.html")

        with open('docs/decks.tsv', 'w', encoding='utf-8') as output_tsv, \
            open('docs/_includes/decks-body.html', 'w', encoding='utf-8') as output_html:

            output_decks(output_html, output_tsv, yaml_infos)
        
        print("Table written to docs/decks.tsv and docs/_includes/decks-body.html")


if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
