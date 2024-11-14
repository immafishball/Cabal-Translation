import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<category_num>'):
                current_section = 'category_num'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<grade_num>'):
                current_section = 'grade_num'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</category_num>') or line.startswith('</grade_num>'):
                current_section = None
            elif line.startswith('<name'):
                match = re.search(r'category="(\d+)"\s+msg="([^"]*)"', line)
                if match:
                    category_id, msg = match.groups()
                    data['category_num'][category_id] = {'msg': msg}
            elif line.startswith('<grade'):
                match = re.search(r'category="(\d+)"\s+num="(\d+)"\s+msg="([^"]*)"', line)
                if match:
                    category_id, num, msg = match.groups()
                    data['grade_num'][(category_id, num)] = {'msg': msg}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        if section == 'category_num':
            match = re.search(r'category="(\d+)"', line)
            if match:
                category_id = match.group(1)
                if category_id in translations:
                    translation = translations[category_id]
                    line = re.sub(r'msg="[^"]*"', f'msg="{translation.get("msg", "")}"', line)
                else:
                    untranslated_lines.append(line)
            else:
                untranslated_lines.append(line)
        elif section == 'grade_num':
            match = re.search(r'category="(\d+)"\s+num="(\d+)"', line)
            if match:
                category_id, num = match.groups()
                key = (category_id, num)
                if key in translations:
                    translation = translations[key]
                    line = re.sub(r'msg="[^"]*"', f'msg="{translation.get("msg", "")}"', line)
                else:
                    untranslated_lines.append(line)
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
        if line.strip().startswith('<cabal_drop_list_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<category_num>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'category_num'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</category_num>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<grade_num>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'grade_num'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</grade_num>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</cabal_drop_list_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
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
file_name_dec = 'drop_list_msg.dec'
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
