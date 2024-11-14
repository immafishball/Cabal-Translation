import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<cabal_msg>'):
                current_section = 'cabal_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<dungeon_msg>'):
                current_section = 'dungeon_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<event_script>'):
                current_section = 'event_script'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<event_bingo_msg>'):
                current_section = 'event_bingo_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<msg'):
                # Handle common <msg> elements
                match = re.search(r'id="([^"]*)"\s+desc1="([^"]*)"\s+desc2="([^"]*)"\s+desc3="([^"]*)"\s+desc4="([^"]*)"\s+name="([^"]*)"', line)
                if match:
                    msg_id, desc1, desc2, desc3, desc4, name = match.groups()
                    data[current_section][msg_id] = {'desc1': desc1, 'desc2': desc2, 'desc3': desc3, 'desc4': desc4, 'name': name}
                
                # Handle <event_bingo_msg> specific attributes
                match = re.search(r'type="([^"]*)"\s+index="([^"]*)"\s+desc="([^"]*)"', line)
                if match:
                    msg_type, index, desc = match.groups()
                    data[current_section][msg_type + '_' + index] = {'desc': desc}
            elif line.startswith('<event_child'):
                match = re.search(r'msg_id="([^"]*)"\s+cont="([^"]*)"', line)
                if match:
                    msg_id, cont = match.groups()
                    data[current_section][msg_id] = {'cont': cont}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'id="([^"]*)"', line)
        if match:
            msg_id = match.group(1)
            if msg_id in translations:
                translation = translations[msg_id]
                for key, value in translation.items():
                    if key in ['desc1', 'desc2', 'desc3', 'desc4', 'name']:
                        value = value.replace('\\', '\\\\')
                        line = re.sub(rf'{key}="[^"]*"', f'{key}="{value}"', line)
                    elif key == 'cont':
                        value = value.replace('\\', '\\\\')
                        line = re.sub(r'cont="[^"]*"', f'cont="{value}"', line)
            else:
                untranslated_lines.append(line)
        elif 'type' in line and 'index' in line:  # Handling for <event_bingo_msg>
            match = re.search(r'type="([^"]*)"\s+index="([^"]*)"', line)
            if match:
                type_index = match.group(1) + '_' + match.group(2)
                if type_index in translations:
                    translation = translations[type_index]
                    if 'desc' in translation:
                        desc_escaped = translation["desc"].replace('\\', '\\\\')
                        line = re.sub(r'desc="[^"]*"', f'desc="{desc_escaped}"', line)
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
        if line.strip().startswith('<cabal_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<version	index="1"	/>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<dungeon_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'dungeon_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</dungeon_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<event_script>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'event_script'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</event_script>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<event_bingo_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'event_bingo_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</event_bingo_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</cabal_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        else:
            section_lines.append(line)

    # Handle any remaining lines in the last section
    if current_section and section_lines:
        translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
        translated_lines.append('</' + current_section + '>\n')

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    # Write untranslated file
    with open(untranslated_file, 'w', encoding='utf-8') as file:
        file.writelines(untranslated_lines)

# Paths relative to current directory
file_name_dec = 'cont2_msg.dec'
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
