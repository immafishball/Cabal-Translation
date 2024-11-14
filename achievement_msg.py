import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<category>'):
                current_section = 'category'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<achievement>'):
                current_section = 'achievement'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<title>'):
                current_section = 'title'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<who>'):
                current_section = 'who'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<action>'):
                current_section = 'action'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<target>'):
                current_section = 'target'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<situation>'):
                current_section = 'situation'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</category>') or line.startswith('</achievement>') or line.startswith('</title>') or line.startswith('</who>') or line.startswith('</action>') or line.startswith('</target>') or line.startswith('</situation>'):
                current_section = None
            elif line.startswith('<') and 'msg_id' in line:
                match = re.search(r'msg_id="(\d+)"\s+name1="([^"]*)"\s+name2="([^"]*)"\s+name3="([^"]*)"\s+desc="([^"]*)"', line)
                if match:
                    msg_id, name1, name2, name3, desc = match.groups()
                    data[current_section][msg_id] = {'name1': name1, 'name2': name2, 'name3': name3, 'desc': desc}
                else:
                    match = re.search(r'msg_id="(\d+)"\s+name="([^"]*)"\s+summary="([^"]*)"', line)
                    if match:
                        msg_id, name, summary = match.groups()
                        data[current_section][msg_id] = {'name': name, 'summary': summary}
                    else:
                        match = re.search(r'msg_id="(\d+)"\s+msg1="([^"]*)"\s+msg2="([^"]*)"', line)
                        if match:
                            msg_id, msg1, msg2 = match.groups()
                            data[current_section][msg_id] = {'msg1': msg1, 'msg2': msg2}
                        else:
                            match = re.search(r'msg_id="(\d+)"\s+msg="([^"]*)"', line)
                            if match:
                                msg_id, msg = match.groups()
                                data[current_section][msg_id] = {'msg': msg}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        match = re.search(r'msg_id="(\d+)"', line)
        if match:
            msg_id = match.group(1)
            if msg_id in translations:
                translation = translations[msg_id]
                if section == 'title':
                    line = re.sub(r'name1="[^"]*"', f'name1="{translation.get("name1", "")}"', line)
                    line = re.sub(r'name2="[^"]*"', f'name2="{translation.get("name2", "")}"', line)
                    line = re.sub(r'name3="[^"]*"', f'name3="{translation.get("name3", "")}"', line)
                    line = re.sub(r'desc="[^"]*"', f'desc="{translation.get("desc", "")}"', line)
                elif section == 'achievement':
                    line = re.sub(r'name="[^"]*"', f'name="{translation.get("name", "")}"', line)
                    line = re.sub(r'summary="[^"]*"', f'summary="{translation.get("summary", "")}"', line)
                elif 'msg' in translation:
                    line = re.sub(r'msg="[^"]*"', f'msg="{translation["msg"]}"', line)
                elif 'msg1' in translation and 'msg2' in translation:
                    line = re.sub(r'msg1="[^"]*"', f'msg1="{translation.get("msg1", "")}"', line)
                    line = re.sub(r'msg2="[^"]*"', f'msg2="{translation.get("msg2", "")}"', line)
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
        if line.strip().startswith('<achievement_message>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<category>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'category'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</category>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<achievement>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'achievement'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</achievement>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<title>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'title'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</title>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<who>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'who'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</who>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<action>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'action'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</action>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<target>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'target'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</target>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<situation>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'situation'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</situation>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</achievement_message>'):
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
file_name_dec = 'achievement_msg.dec'
current_directory = os.path.dirname(os.path.abspath(__file__))
input_file_path = os.path.join(current_directory, 'KR', file_name_dec)
translation_file_path = os.path.join(current_directory, 'EN', file_name_dec)
output_file_path = os.path.join(current_directory, 'Translated', file_name_dec)
untranslated_file_path = os.path.join(current_directory, 'Untranslated', file_name_dec)

#Print File Path
print('KR Location: ' + input_file_path)
print('EN Location: ' + translation_file_path)
print('Translated Location: ' + output_file_path)
print('Untranslate Location: ' + untranslated_file_path)

# Parse translation data from file2.xml
translation_data = parse_dec_file(translation_file_path)

# Translate file1.xml using translation data
translate_file(input_file_path, translation_data, output_file_path, untranslated_file_path)