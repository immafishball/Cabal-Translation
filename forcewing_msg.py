import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(dict)
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<wing_skill_msg>') or line.startswith('<wing_training_msg>') or line.startswith('<random_grade_msg>'):
                current_section = line.split('>')[0].replace('<', '')
                data[current_section] = defaultdict(dict)
            elif line.startswith('</wing_skill_msg>') or line.startswith('</wing_training_msg>') or line.startswith('</random_grade_msg>'):
                current_section = None
            elif line.startswith('<msg'):
                match = re.search(r'slot="(\d+)"\s+cont="([^"]*)"', line) or \
                        re.search(r't_slot="(\d+)"\s+cont="([^"]*)"', line) or \
                        re.search(r'grade="(\d+)"\s+cont="([^"]*)"', line)
                if match:
                    key, cont = match.groups()
                    data[current_section][key] = {'cont': cont}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'(slot|t_slot|grade)="(\d+)"', line)
        if match:
            key_type, key = match.groups()
            if key in translations:
                translation = translations[key]
                line = re.sub(r'cont="[^"]*"', f'cont="{translation.get("cont", "")}"', line)
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
        if line.strip().startswith('<wing_skill_msg>') or line.strip().startswith('<wing_training_msg>') or line.strip().startswith('<random_grade_msg>'):
            if section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            section_lines = [line]
            current_section = line.strip().split('>')[0].replace('<', '').replace('>', '')
        elif line.strip().startswith('</wing_skill_msg>') or line.strip().startswith('</wing_training_msg>') or line.strip().startswith('</random_grade_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            section_lines = []
            current_section = None
        else:
            section_lines.append(line)

    # Handle any remaining lines
    if section_lines:
        translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    # Write untranslated file
    with open(untranslated_file, 'w', encoding='utf-8') as file:
        file.writelines(untranslated_lines)

# Paths relative to current directory
file_name_dec = 'forcewing_msg.dec'
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
