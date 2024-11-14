import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<honor_medal_name_msg>'):
                current_section = 'honor_medal_name_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<honor_medal_force_msg>'):
                current_section = 'honor_medal_force_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</honor_medal_name_msg>') or line.startswith('</honor_medal_force_msg>'):
                current_section = None
            elif line.startswith('<msg'):
                match = re.search(r'id="([^"]+)"\s+cont1="([^"]*)"\s+cont2="([^"]*)"', line)
                if match:
                    msg_id, cont1, cont2 = match.groups()
                    data[current_section][msg_id] = {'cont1': cont1, 'cont2': cont2}
                else:
                    match = re.search(r'force_id="(\d+)"\s+cont="([^"]*)"', line)
                    if match:
                        force_id, cont = match.groups()
                        data[current_section][force_id] = {'cont': cont}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'id="([^"]+)"', line) or re.search(r'force_id="(\d+)"', line)
        if match:
            msg_id = match.group(1)
            if msg_id in translations:
                translation = translations[msg_id]
                if section == 'honor_medal_name_msg':
                    line = re.sub(r'cont1="[^"]*"', f'cont1="{translation.get("cont1", "")}"', line)
                    line = re.sub(r'cont2="[^"]*"', f'cont2="{translation.get("cont2", "")}"', line)
                elif section == 'honor_medal_force_msg':
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
    section_opened = False

    for line in lines:
        if line.strip().startswith('<honor_medal_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<honor_medal_name_msg>') or line.strip().startswith('<honor_medal_force_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = line.strip().split('>')[0].replace('<', '').replace('>', '')
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</honor_medal_name_msg>') or line.strip().startswith('</honor_medal_force_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</honor_medal_message>'):
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
file_name_dec = 'honor_medal_msg.dec'  # Adjust to your actual file name
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
