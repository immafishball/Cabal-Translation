import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<main>'):
                current_section = 'main'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<awakenauremode_slot_msg>'):
                current_section = 'awakenauremode_slot_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</main>') or line.startswith('</awakenauremode_slot_msg>'):
                current_section = None
            elif line.startswith('<auramode_main'):
                match = re.search(r'Category="(\d+)"\s+category_name="([^"]*)"', line)
                if match:
                    category_id, category_name = match.groups()
                    data['main'][category_id] = {'category_name': category_name}
            elif line.startswith('<msg'):
                match = re.search(r'Category="(\d+)"\s+slot_index="(\d+)"\s+slot_name="([^"]*)"\s+desc="([^"]*)"', line)
                if match:
                    category_id, slot_index, slot_name, desc = match.groups()
                    data['awakenauremode_slot_msg'][(category_id, slot_index)] = {'slot_name': slot_name, 'desc': desc}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'Category="(\d+)"\s+slot_index="(\d+)"', line)
        if match:
            category_id, slot_index = match.groups()
            key = (category_id, slot_index)
            if key in translations:
                translation = translations[key]
                line = re.sub(r'slot_name="[^"]*"', f'slot_name="{translation.get("slot_name", "")}"', line)
                line = re.sub(r'desc="[^"]*"', f'desc="{translation.get("desc", "")}"', line)
            else:
                untranslated_lines.append(line)
        else:
            match = re.search(r'Category="(\d+)"', line)
            if match:
                category_id = match.group(1)
                if category_id in translations:
                    translation = translations[category_id]
                    line = re.sub(r'category_name="[^"]*"', f'category_name="{translation.get("category_name", "")}"', line)
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
        if line.strip().startswith('<awakenauremode_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<main>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'main'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</main>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<awakenauremode_slot_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'awakenauremode_slot_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</awakenauremode_slot_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</awakenauremode_msg>'):
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
file_name_dec = 'Awaken_auramode_msg.dec'
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
