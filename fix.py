import os
import xml.etree.ElementTree as ET

nodpi_dir = os.path.join("base", "res", "drawable-nodpi")
existing_pngs = {
    os.path.splitext(f)[0]
    for f in os.listdir(nodpi_dir)
    if f.endswith((".png", ".webp", ".xml"))
}

values_drawables = os.path.join("base", "res", "values-nodpi", "drawables.xml")
if os.path.exists(values_drawables):
    tree = ET.parse(values_drawables)
    root = tree.getroot()
    removed = 0
    for elem in list(root):
        if elem.get("name") in existing_pngs:
            root.remove(elem)
            removed += 1
    tree.write(values_drawables, encoding="utf-8", xml_declaration=True)
    print(f"Removed {removed} conflicting entries from values-nodpi/drawables.xml")