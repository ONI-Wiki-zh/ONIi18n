import copy
import os.path as path
import babel.messages.pofile as pofile


def load_po(file_dir):
    with open(file_dir, 'r', encoding='utf-8') as f_obj:
        while (f_obj.readline()) != '\n':  # skip metadata
            pass
        return pofile.read_po(f_obj)


def subtract(f_dir_1, f_dir_2):
    pofile1 = load_po(f_dir_1)
    to_sub = set(msg.context for msg in load_po(f_dir_2))

    result = copy.copy(pofile1)
    for msg in list(pofile1):
        if msg.context in to_sub:
            result.delete(msg.id, msg.context)
    return result


def main(base_template=r"C:\Program Files (x86)\Steam\steamapps\common\OxygenNotIncluded\OxygenNotIncluded_Data"
                       r"\StreamingAssets\strings\strings_template.pot",
         mod_template_dir=path.join(path.expanduser("~"), "Documents", "Klei", "OxygenNotIncluded", "mods",
                                    "strings_templates"),
         minuend="curr_mods_template.pot",
         output_file="curr_mods.pot"):
    generated_template = path.join(mod_template_dir, minuend)
    with open(path.join(mod_template_dir, output_file), 'wb') as f_obj:
        pofile.write_po(f_obj, subtract(generated_template, base_template))


if __name__ == '__main__':
    main()
