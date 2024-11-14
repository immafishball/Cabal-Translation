import os
import re
from collections import defaultdict

def parse_dec_file(file_path):
    data = defaultdict(lambda: defaultdict(dict))
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('<RaidBoss_Info_msg>'):
                current_section = 'RaidBoss_Info_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<RewardList_Msg>'):
                current_section = 'RewardList_Msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('</RaidBoss_Info_msg>') or line.startswith('</RewardList_Msg>'):
                current_section = None
            elif line.startswith('<BossInfo_name'):
                match = re.search(r'WorldIdx="(\d+)"\s+BossIdx="(\d+)"\s+Nickname="([^"]*)"\s+BossName="([^"]*)"', line)
                if match:
                    world_idx, boss_idx, nickname, boss_name = match.groups()
                    data['RaidBoss_Info_msg'][(world_idx, boss_idx)] = {'Nickname': nickname, 'BossName': boss_name}
            elif line.startswith('<RewardList'):
                match = re.search(r'WorldIdx="(\d+)"\s+BossIdx="(\d+)"\s+RewardItem="(\d+)"', line)
                if match:
                    world_idx, boss_idx, reward_item = match.groups()
                    data['RewardList_Msg'][(world_idx, boss_idx)] = {'RewardItem': reward_item}
    return data

def translate_section_lines(lines, translations, section, untranslated_lines):
    translated_lines = []
    for line in lines:
        if section == 'RaidBoss_Info_msg':
            match = re.search(r'WorldIdx="(\d+)"\s+BossIdx="(\d+)"', line)
            if match:
                world_idx, boss_idx = match.groups()
                key = (world_idx, boss_idx)
                if key in translations:
                    translation = translations[key]
                    line = re.sub(r'Nickname="[^"]*"', f'Nickname="{translation.get("Nickname", "")}"', line)
                    line = re.sub(r'BossName="[^"]*"', f'BossName="{translation.get("BossName", "")}"', line)
                else:
                    untranslated_lines.append(line)
            else:
                untranslated_lines.append(line)
        elif section == 'RewardList_Msg':
            match = re.search(r'WorldIdx="(\d+)"\s+BossIdx="(\d+)"', line)
            if match:
                world_idx, boss_idx = match.groups()
                key = (world_idx, boss_idx)
                if key in translations:
                    translation = translations[key]
                    line = re.sub(r'RewardItem="[^"]*"', f'RewardItem="{translation.get("RewardItem", "")}"', line)
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
        if line.strip().startswith('<RaidBoss_Msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            untranslated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('<RaidBoss_Info_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'RaidBoss_Info_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</RaidBoss_Info_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<RewardList_Msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'RewardList_Msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</RewardList_Msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('</RaidBoss_Msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data[current_section], current_section, untranslated_lines))
            current_section = None
            untranslated_lines.append(line)
            section_lines = []
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
file_name_dec = 'FieldBossRaid_msg.dec'
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
