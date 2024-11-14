import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(dict)
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<cabal_msg>'):
                current_section = 'cabal_msg'
                data[current_section] = {}
            elif line.startswith('</cabal_msg>'):
                current_section = None
            elif line:
                match = re.match(r'(\d+)@ (.*)', line)
                if match:
                    msg_id, cont = match.groups()
                    data[current_section][msg_id] = {'cont': cont}
    return data

def translate_section_lines(lines, translations, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'(\d+)@ ', line)
        if match:
            msg_id = match.group(1)
            if msg_id in translations:
                translation = translations[msg_id]
                if 'cont' in translation:
                    line = f'{msg_id}@ {translation["cont"]}'
            else:
                untranslated_lines.append(line)
        else:
            untranslated_lines.append(line)
        translated_lines.append(line + '\n')
    return translated_lines

def translate_file(input_file, translation_data, output_file, untranslated_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    translated_lines = []
    untranslated_lines = []
    section_lines = []
    current_section = None

    for line in lines:
        if line.strip().startswith('<cabal_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), untranslated_lines))
            current_section = 'cabal_msg'
            section_lines = [line]
        elif line.strip().startswith('</cabal_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), untranslated_lines))
            current_section = None
            section_lines = []
        else:
            section_lines.append(line)

    # Handle any remaining lines in the last section
    if current_section and section_lines:
        translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), untranslated_lines))

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    # Write untranslated file
    with open(untranslated_file, 'w', encoding='utf-8') as file:
        file.writelines(untranslated_lines)

# Paths relative to current directory
file_name_dec = 'ui.dts'
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