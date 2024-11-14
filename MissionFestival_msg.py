import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<MissionTitle_msg>'):
                current_section = 'MissionTitle_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<Count_msg>'):
                current_section = 'Count_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<Desc_msg>'):
                current_section = 'Desc_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<MissionList_msg>'):
                current_section = 'MissionList_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<Drop_Location>'):
                current_section = 'Drop_Location'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<Monster_Location>'):
                current_section = 'Monster_Location'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</MissionTitle_msg>') or line.startswith('</Count_msg>') or line.startswith('</Desc_msg>') or line.startswith('</MissionList_msg>') or line.startswith('</Drop_Location>') or line.startswith('</Monster_Location>'):
                current_section = None
            elif line.startswith('<msg'):
                match = re.search(r'(Title_Index|Count_Index|Desc_Index)="(\d+)"\s+desc="([^"]*)"', line)
                if match:
                    index_type, index, desc = match.groups()
                    data[current_section][index] = {'desc': desc}
            elif line.startswith('<Mission'):
                match = re.search(r'Type="(\d+)"\s+Title_Index="(\d+)"\s+Icon="([^"]*)"\s+Desc_Index="(\d+)"\s+Count_Index="(\d+)"', line)
                if match:
                    Type, Title_Index, Icon, Desc_Index, Count_Index = match.groups()
                    data[current_section][Title_Index] = {'Type': Type, 'Icon': Icon, 'Desc_Index': Desc_Index, 'Count_Index': Count_Index}
            elif line.startswith('<Item_Location'):
                match = re.search(r'Item_Index="(\d+)"\s+Dungeon_index="(\d+)"', line)
                if match:
                    Item_Index, Dungeon_index = match.groups()
                    data[current_section][Item_Index] = {'Dungeon_index': Dungeon_index}
            elif line.startswith('<Boss_Location'):
                match = re.search(r'Monster_index="(\d+)"\s+World_index="(\d+)"', line)
                if match:
                    Monster_index, World_index = match.groups()
                    data[current_section][Monster_index] = {'World_index': World_index}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'(Title_Index|Count_Index|Desc_Index)="(\d+)"', line)
        if match:
            index_type, index = match.groups()
            if index in translations:
                translation = translations[index]
                line = re.sub(r'desc="[^"]*"', f'desc="{translation.get("desc", "")}"', line)
            else:
                untranslated_lines.append(line)
        elif re.search(r'Type="(\d+)"\s+Title_Index="(\d+)"\s+Icon="([^"]*)"\s+Desc_Index="(\d+)"\s+Count_Index="(\d+)"', line):
            untranslated_lines.append(line)
        elif re.search(r'Item_Index="(\d+)"\s+Dungeon_index="(\d+)"', line):
            untranslated_lines.append(line)
        elif re.search(r'Monster_index="(\d+)"\s+World_index="(\d+)"', line):
            untranslated_lines.append(line)
        else:
            untranslated_lines.append(line)
        translated_lines.append(line)
    return translated_lines

def translate_file(input_file, translation_data, output_file, untranslated_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    translated_lines = []
    untranslated_lines = []
    section_lines = []
    current_section = None
    section_opened = False

    for line in lines:
        if line.strip().startswith('<MissionFestival_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<MissionTitle_msg>') or line.strip().startswith('<Count_msg>') or line.strip().startswith('<Desc_msg>') or line.strip().startswith('<MissionList_msg>') or line.strip().startswith('<Drop_Location>') or line.strip().startswith('<Monster_Location>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = line.strip().split('>')[0].replace('<', '').replace('>', '')
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</MissionTitle_msg>') or line.strip().startswith('</Count_msg>') or line.strip().startswith('</Desc_msg>') or line.strip().startswith('</MissionList_msg>') or line.strip().startswith('</Drop_Location>') or line.strip().startswith('</Monster_Location>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</MissionFestival_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        else:
            section_lines.append(line)

    # Handle any remaining lines in the last section
    if current_section and section_lines:
        translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
        translated_lines.append('</' + current_section + '>\n')

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    # Write untranslated file
    with open(untranslated_file, 'w', encoding='utf-8') as file:
        file.writelines(untranslated_lines)

# Paths relative to current directory
file_name_dec = 'MissionFestival_msg.dec'
current_directory = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(current_directory, 'KR', file_name_dec)
translation_file_path = os.path.join(current_directory, 'EN', file_name_dec)
output_file_path = os.path.join(current_directory, 'Translated', file_name_dec)
untranslated_file_path = os.path.join(current_directory, 'Untranslated', file_name_dec)

# Print File Path
print('KR Location: ' + input_file_path)
print('EN Location: ' + translation_file_path)
print('Translated Location: ' + output_file_path)
print('Untranslated Location: ' + untranslated_file_path)

# Parse translation data from file2.xml
translation_data = parse_dec_file(translation_file_path)

# Translate file1.xml using translation data
translate_file(input_file_path, translation_data, output_file_path, untranslated_file_path)
