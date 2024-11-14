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
            elif line.startswith('<item_msg>'):
                current_section = 'item_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<itemtype_msg>'):
                current_section = 'itemtype_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<mob_msg>'):
                current_section = 'mob_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<ckit_hair_brand_msg>'):
                current_section = 'ckit_hair_brand_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<ckit_design_msg>'):
                current_section = 'ckit_design_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<ckit_color_msg>'):
                current_section = 'ckit_color_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<ckit_face_msg>'):
                current_section = 'ckit_face_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<alt_core_name_msg>'):
                current_section = 'alt_core_name_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<alt_core_desc_msg>'):
                current_section = 'alt_core_desc_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<war_ft_name_msg>'):
                current_section = 'war_ft_name_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<war_ft_desc_msg>'):
                current_section = 'war_ft_desc_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<war_fort_name_msg>'):
                current_section = 'war_fort_name_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<war_map_desc_msg>'):
                current_section = 'war_map_desc_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<war_reward_desc_msg>'):
                current_section = 'war_reward_desc_msg'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<g1_name>'):
                current_section = 'g1_name'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<g2_name>'):
                current_section = 'g2_name'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<g3_name>'):
                current_section = 'g3_name'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<g4_name>'):
                current_section = 'g4_name'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<g5_name>'):
                current_section = 'g5_name'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<attack>'):
                current_section = 'attack'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<effect>'):
                current_section = 'effect'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<lordofwar>'):
                current_section = 'lordofwar'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<rateability_recipe>'):
                current_section = 'rateability_recipe'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<assistant>'):
                current_section = 'assistant'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<battlemode3>'):
                current_section = 'battlemode3'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<buff_group>'):
                current_section = 'buff_group'
                data[current_section] = defaultdict(dict)
            elif line.startswith('<msg'):
                match = re.search(r'id="([^"]*)"\s+cont="([^"]*)"', line)
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
                if 'cont' in translation:
                    cont_escaped = translation["cont"].replace('\\', '\\\\')
                    line = re.sub(r'cont="[^"]*"', f'cont="{cont_escaped}"', line)
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
        elif line.strip().startswith('<version index="1"	/>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<cabal_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'cabal_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</cabal_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<item_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'item_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</item_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<itemtype_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'itemtype_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</itemtype_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<mob_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'mob_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</mob_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<ckit_hair_brand_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'ckit_hair_brand_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</ckit_hair_brand_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<ckit_design_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'ckit_design_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</ckit_design_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<ckit_color_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'ckit_color_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</ckit_color_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<ckit_face_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'ckit_face_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</ckit_face_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<alt_core_name_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'alt_core_name_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</alt_core_name_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<alt_core_desc_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'alt_core_desc_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</alt_core_desc_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<war_ft_name_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'war_ft_name_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</war_ft_name_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<war_ft_desc_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'war_ft_desc_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</war_ft_desc_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<war_fort_name_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'war_fort_name_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</war_fort_name_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<war_map_desc_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'war_map_desc_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</war_map_desc_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<war_reward_desc_msg>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'war_reward_desc_msg'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</war_reward_desc_msg>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<g1_name>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'g1_name'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</g1_name>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<g2_name>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'g2_name'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</g2_name>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<g3_name>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'g3_name'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</g3_name>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<g4_name>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'g4_name'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</g4_name>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<g5_name>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'g5_name'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</g5_name>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<attack>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'attack'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</attack>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<effect>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'effect'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</effect>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<lordofwar>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'lordofwar'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</lordofwar>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<rateability_recipe>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'rateability_recipe'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</rateability_recipe>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<assistant>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'assistant'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</assistant>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<battlemode3>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'battlemode3'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</battlemode3>'):
            section_lines.append(line)
            translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
            current_section = None
            section_lines = []
            section_opened = False
        elif line.strip().startswith('<buff_group>'):
            if current_section and section_lines:
                translated_lines.extend(translate_section_lines(section_lines, translation_data.get(current_section, {}), current_section, untranslated_lines))
                translated_lines.append('</' + current_section + '>\n')
            if not section_opened:
                untranslated_lines.append(line)
                section_opened = True
            current_section = 'buff_group'
            translated_lines.append(line)
            section_lines = []
        elif line.strip().startswith('</buff_group>'):
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
file_name_dec = 'cabal_msg.dec'
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
