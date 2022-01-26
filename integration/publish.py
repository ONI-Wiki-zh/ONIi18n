import io
import json
import os
import os.path as path
import pathlib
import shutil

import babel.messages.catalog as catalog
import babel.messages.pofile as pofile
import typing

class Lang(typing.TypedDict):
    code: str
    name: str
    catalog: pofile.Catalog
    mods: dict

DIST_DIR = path.join('.', 'dist')
SOURCE_DIR = path.join('.', 'strings')
CONFIG_DIR = path.join(SOURCE_DIR, 'languages.json')

with open(CONFIG_DIR, 'r', encoding='utf-8') as f:
    lang_code = json.load(f)
languages: typing.Dict[str, Lang] = {code: {
    'code': code,
    'name': lang_code[code],
    'catalog': catalog.Catalog(project='ONIi18n', version='1.0.0'),
    'mods': {},
} for code in lang_code}

_, mods, _ = next(os.walk(SOURCE_DIR))
for mod in mods:
    curr_dir, _, files = next(os.walk(path.join(SOURCE_DIR, mod)))
    for lang in languages:
        f_name = f"{lang}.po"
        f_config = f"config.json"
        if f_name not in files:
            continue
        with open(path.join(curr_dir, f_name), 'r', encoding='utf-8') as f_obj:
            content = f_obj.read().strip()
            f_obj = io.StringIO(content)
            while (f_obj.readline()) != '\n':  # skip metadata
                pass
            mod_catalog = pofile.read_po(f_obj)
            for msg in mod_catalog:
                if not msg.string:
                    continue
                msg: pofile.Message
                curr_catalog: pofile.Catalog = languages[lang]['catalog']
                curr_catalog.add(id=msg.id, string=msg.string, context=msg.context)

        # data for lang.json
        mod_json = {}
        if f_config in files:
            with open(path.join(curr_dir, f_config), 'r', encoding='utf-8') as f:
                mod_json['config'] = json.load(f)
        else:
            mod_json['config'] = {}
        mod_json['translations'] = []
        for msg in mod_catalog:
            mod_json['translations'].append({
                'msgctxt': msg.context,
                'msgid': msg.id,
                'msgstr': msg.string,
            })
        languages[lang]['mods'][mod] = mod_json

pathlib.Path(DIST_DIR).mkdir(parents=True, exist_ok=True)
for lang in languages:
    # code.po
    curr_catalog: catalog.Catalog = languages[lang]['catalog']
    curr_catalog.project = "ONIi18n"
    curr_catalog.version = "v1.0.0"
    with open(path.join(DIST_DIR, f'{lang}.po'), 'wb') as f_obj:
        pofile.write_po(f_obj, curr_catalog)

    # code.json
    with open(path.join(DIST_DIR, f'{lang}.json'), 'w', encoding='utf-8') as f_obj:
        json.dump({
            'code': languages[lang]['code'],
            'name': languages[lang]['name'],
            'mods': languages[lang]['mods'],
        }, f_obj, indent='\t', ensure_ascii=False)

shutil.copyfile(CONFIG_DIR, path.join(DIST_DIR, 'languages.json'))
