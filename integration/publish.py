import json
import os
import os.path as path
import pathlib
import shutil

import babel.messages.catalog as catalog
import babel.messages.pofile as pofile

DIST_DIR = path.join('..', 'dist')
SOURCE_DIR = path.join('..', 'strings')
CONFIG_DIR = path.join(SOURCE_DIR, 'languages.json')

with open(CONFIG_DIR, 'r', encoding='utf-8') as f:
    languages = json.load(f)
languages = {lang: {"name": lang, 'catalog': catalog.Catalog(project='ONIi18n', version='1.0.0')} for lang in languages}

_, mods, _ = next(os.walk(SOURCE_DIR))
for mod in mods:
    curr_dir, _, files = next(os.walk(path.join(SOURCE_DIR, mod)))
    for lang in languages:
        f_name = f"{lang}.po"
        if f_name not in files:
            continue
        with open(path.join(curr_dir, f_name), 'r', encoding='utf-8') as f_obj:
            curr_catalog = pofile.read_po(f_obj)
            for msg in curr_catalog:
                if not msg.string:
                    continue
                msg: pofile.Message
                curr_catalog: pofile.Catalog = languages[lang]['catalog']
                curr_catalog.add(id=msg.id, string=msg.string, context=msg.context)


pathlib.Path(DIST_DIR).mkdir(parents=True, exist_ok=True)
for lang in languages:
    curr_catalog: catalog.Catalog = languages[lang]['catalog']
    curr_catalog.project = "ONIi18n"
    curr_catalog.version = "v1.0.0"
    with open(path.join(DIST_DIR, f'{lang}.po'), 'wb') as f_obj:
        pofile.write_po(f_obj, curr_catalog)

shutil.copyfile(CONFIG_DIR, path.join(DIST_DIR, 'languages.json'))
