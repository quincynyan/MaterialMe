import os
import re
import shutil
import xml.etree.ElementTree as ET

def find_drawable_file(base_dir, name):
    res_dir = os.path.join(base_dir, "res")
    for folder in os.listdir(res_dir):
        if folder.startswith("drawable"):
            for ext in (".png", ".webp", ".xml"):
                candidate = os.path.join(res_dir, folder, name + ext)
                if os.path.isfile(candidate):
                    return candidate, ext
    return None, None

def parse_items(xml_path):
    tree = ET.parse(xml_path)
    return tree, tree.getroot()

# Load base and over appfilters
base_appfilter_path = os.path.join("base", "assets", "appfilter.xml")
base_raw_appfilter_path = os.path.join("base", "res", "raw", "appfilter.xml")
base_drawable_xml_path = os.path.join("base", "assets", "drawable.xml")
over_appfilter_path = os.path.join("over", "assets", "appfilter.xml")

base_tree, base_root = parse_items(base_appfilter_path)
over_tree, over_root = parse_items(over_appfilter_path)
draw_tree, draw_root = parse_items(base_drawable_xml_path)

# Map existing components in base -> drawable name
comp_to_drawable = {}
drawable_usage_count = {}
max_ic_num = 0

for item in base_root.findall("item"):
    comp = item.get("component")
    drw = item.get("drawable")
    if comp and drw:
        comp_to_drawable[comp] = drw
        drawable_usage_count[drw] = drawable_usage_count.get(drw, 0) + 1
    if drw and re.match(r"^ic_(\d+)$", drw):
        max_ic_num = max(max_ic_num, int(drw.split("_")[1]))

replaced = 0
added = 0
dest_nodpi = os.path.join("base", "res", "drawable-nodpi")

for item in over_root.findall("item"):
    comp = item.get("component")
    over_drw = item.get("drawable")
    if not comp or not over_drw:
        continue

    src_file, src_ext = find_drawable_file("over", over_drw)
    if not src_file:
        continue

    if comp in comp_to_drawable and drawable_usage_count.get(comp_to_drawable[comp], 0) == 1:
        # Overwrite the existing base icon PNG with the older A70 icon
        target_drw = comp_to_drawable[comp]
        dst_file, _ = find_drawable_file("base", target_drw)
        if dst_file:
            os.remove(dst_file)
        shutil.copy2(src_file, os.path.join(dest_nodpi, target_drw + src_ext))
        replaced += 1
    else:
        # Component wasn't in base (or was shared): add a new sequential icon entry
        max_ic_num += 1
        new_drw = f"ic_{max_ic_num:04d}"
        shutil.copy2(src_file, os.path.join(dest_nodpi, new_drw + src_ext))

        if comp in comp_to_drawable:
            for existing in base_root.findall("item"):
                if existing.get("component") == comp:
                    existing.set("drawable", new_drw)
        else:
            new_item = ET.Element("item", {"component": comp, "drawable": new_drw})
            base_root.append(new_item)

        draw_root.append(ET.Element("item", {"drawable": new_drw}))
        comp_to_drawable[comp] = new_drw
        added += 1

# Write updated XMLs to both assets and res/raw
base_tree.write(base_appfilter_path, encoding="utf-8", xml_declaration=True)
shutil.copy2(base_appfilter_path, base_raw_appfilter_path)
draw_tree.write(base_drawable_xml_path, encoding="utf-8", xml_declaration=True)

print(f"Done! Replaced {replaced} icons with A70 versions, added {added} extra mappings.")