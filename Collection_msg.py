import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<Collection>'):
                current_section = 'Collection'
            elif line.startswith('<Mission>'):
                current_section = 'Mission'
            elif line.startswith('<Mission_item>'):
                current_section = 'Mission_item'
            elif line.startswith('</Collection>') or line.startswith('</Mission>') or line.startswith('</Mission_item>'):
                current_section = None
            elif line.startswith('<type_info'):
                match = re.search(r't_id="(\d+)"', line)
                if match:
                    t_id = match.group(1)
                    data[current_section][t_id] = defaultdict(dict)
            elif line.startswith('<Item_msg'):
                if current_section == 'Collection':
                    match = re.search(r'c_id="(\d+)"\s+name="([^"]*)"', line)
                    if match:
                        c_id, name = match.groups()
                        data['Collection'][t_id][c_id] = {'name': name}
                elif current_section == 'Mission':
                    match = re.search(r'c_id="(\d+)"\s+m_id="(\d+)"\s+name="([^"]*)"', line)
                    if match:
                        c_id, m_id, name = match.groups()
                        data['Mission'][t_id][(c_id, m_id)] = {'name': name}
                elif current_section == 'Mission_item':
                    match = re.search(r'type_id="(\d+)"\s+item_id="(\d+)"\s+name="([^"]*)"', line)
                    if match:
                        type_id, item_id, name = match.groups()
                        data['Mission_item'][(type_id, item_id)] = {'name': name}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    t_id = None

    for line in lines:
        if section == 'Collection':
            match = re.search(r't_id="(\d+)"', line)
            if match:
                t_id = match.group(1)
            match = re.search(r'c_id="(\d+)"', line)
            if match:
                c_id = match.group(1)
                key = c_id
                if t_id in translations and key in translations[t_id]:
                    translation = translations[t_id][key]
                    line = re.sub(r'name="[^"]*"', f'name="{translation.get("name", "")}"', line)
                else:
                    untranslated_lines.append(line)
            else:
                untranslated_lines.append(line)
        elif section == 'Mission':
            match = re.search(r't_id="(\d+)"', line)
            if match:
                t_id = match.group(1)
            match = re.search(r'c_id="(\d+)"\s+m_id="(\d+)"', line)
            if match:
                c_id, m_id = match.groups()
                key = (c_id, m_id)
                if t_id in translations and key in translations[t_id]:
                    translation = translations[t_id][key]
                    line = re.sub(r'name="[^"]*"', f'name="{translation.get("name", "")}"', line)
                else:
                    untranslated_lines.append(line)
            else:
                untranslated_lines.append(line)
        elif section == 'Mission_item':
            match = re.search(r'type_id="(\d+)"\s+item_id="(\d+)"', line)
            if match:
                type_id, item_id = match.groups()
                key = (type_id, item_id)
                if key in translations:
                    translation = translations[key]
                    line = re.sub(r'name="[^"]*"', f'name="{translation.get("name", "")}"', line)
                else:
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

    for line in lines:
        if line.strip().startswith('<Collection_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            untranslated_lines.append(line)
        elif line.strip().startswith('<Collection>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            current_section = 'Collection'
            section_lines = [line]
        elif line.strip().startswith('</Collection>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
        elif line.strip().startswith('<Mission>'):
            translated_lines.append('\n')
            untranslated_lines.append('\n')
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            current_section = 'Mission'
            section_lines = [line]
        elif line.strip().startswith('</Mission>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
        elif line.strip().startswith('<Mission_item>'):
            translated_lines.append('\n')
            untranslated_lines.append('\n')
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            current_section = 'Mission_item'
            section_lines = [line]
        elif line.strip().startswith('</Mission_item>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
        elif line.strip().startswith('</Collection_message>'):
            untranslated_lines.append('\n')
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            untranslated_lines.append(line)
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
file_name_dec = 'Collection_msg.dec'
current_directory = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(current_directory, 'KR', file_name_dec)
translation_file_path = os.path.join(current_directory, 'EN', file_name_dec)
output_file_path = os.path.join(current_directory, 'Translated', file_name_dec)
untranslated_file_path = os.path.join(current_directory, 'Untranslated', file_name_dec)

# Print File Path
print('KR Location: ' + input_file_path)
print('EN Location: ' + translation_file_path)
print('Translated Location: ' + output_file_path)
print('Untranslate Location: ' + untranslated_file_path)

# Parse translation data from file2.xml
translation_data = parse_dec_file(translation_file_path)

# Translate file1.xml using translation data
translate_file(input_file_path, translation_data, output_file_path, untranslated_file_path)
