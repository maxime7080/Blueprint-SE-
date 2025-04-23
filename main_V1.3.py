component_displaynames = {'Construction': 'DisplayName_Item_ConstructionComponent', 'MetalGrid': 'DisplayName_Item_MetalGrid', 'InteriorPlate': 'DisplayName_Item_InteriorPlate', 'SteelPlate': 'DisplayName_Item_SteelPlate', 'Girder': 'DisplayName_Item_Girder', 'SmallTube': 'DisplayName_Item_SmallSteelTube', 'LargeTube': 'DisplayName_Item_LargeSteelTube', 'Motor': 'DisplayName_Item_Motor', 'Display': 'DisplayName_Item_Display', 'BulletproofGlass': 'DisplayName_Item_BulletproofGlass', 'Superconductor': 'DisplayName_Item_Superconductor', 'Computer': 'DisplayName_Item_Computer', 'Reactor': 'DisplayName_Item_ReactorComponents', 'Thrust': 'DisplayName_Item_ThrustComponents', 'GravityGenerator': 'DisplayName_Item_GravityGeneratorComponents', 'Medical': 'DisplayName_Item_MedicalComponents', 'RadioCommunication': 'DisplayName_Item_RadioCommunicationComponents', 'Detector': 'DisplayName_Item_DetectorComponents', 'Explosives': 'DisplayName_Item_Explosives', 'SolarCell': 'DisplayName_Item_SolarCell', 'PowerCell': 'DisplayName_Item_PowerCell', 'Canvas': 'DisplayName_Item_CanvasCartridge', 'EngineerPlushie': 'DisplayName_Block_EngineerPlushie', 'SabiroidPlushie': 'DisplayName_Block_SabiroidPlushie', 'PrototechFrame': 'DisplayName_Item_PrototechFrame', 'PrototechPanel': 'DisplayName_Item_PrototechPanel', 'PrototechCapacitor': 'DisplayName_Item_PrototechCapacitor', 'PrototechPropulsionUnit': 'DisplayName_Item_PrototechPropulsionUnit', 'PrototechMachinery': 'DisplayName_Item_PrototechMachinery', 'PrototechCircuitry': 'DisplayName_Item_PrototechCircuitry', 'PrototechCoolingUnit': 'DisplayName_Item_PrototechCoolingUnit'}


fallback_component_displaynames = {
    "Reactor": "DisplayName_Item_ReactorComponent",
    "Detector": "DisplayName_Item_DetectorComponent",
    "Medical": "DisplayName_Item_MedicalComponent",
    "Thrust": "DisplayName_Item_ThrustComponent",
    "RadioCommunication": "DisplayName_Item_RadioCommunicationComponent",
    "GravityGenerator": "DisplayName_Item_GravityGeneratorComponent",
    "SolarCell": "DisplayName_Item_SolarCellComponent"
}



import os
import tkinter as tk
from tkinter import ttk, filedialog
import xml.etree.ElementTree as ET

DATA_DIR = "data"
LOCALIZATION_FILES = {
    "en": [
        "Data/Localization/MyTexts.resx",
        "Data/Localization/Common/MyCommonTexts.resx",
        "Data/Localization/CoreTexts/MyCoreTexts.resx"
    ],
    "fr": [
        "Data/Localization/MyTexts.fr.resx",
        "Data/Localization/Common/MyCommonTexts.fr.resx",
        "Data/Localization/CoreTexts/MyCoreTexts.fr.resx"
    ]
}

# Injected from XML parsing
component_displaynames = {'Construction': 'DisplayName_Item_ConstructionComponent', 'MetalGrid': 'DisplayName_Item_MetalGrid', 'InteriorPlate': 'DisplayName_Item_InteriorPlate', 'SteelPlate': 'DisplayName_Item_SteelPlate', 'Girder': 'DisplayName_Item_Girder', 'SmallTube': 'DisplayName_Item_SmallSteelTube', 'LargeTube': 'DisplayName_Item_LargeSteelTube', 'Motor': 'DisplayName_Item_Motor', 'Display': 'DisplayName_Item_Display', 'BulletproofGlass': 'DisplayName_Item_BulletproofGlass', 'Superconductor': 'DisplayName_Item_Superconductor', 'Computer': 'DisplayName_Item_Computer', 'Reactor': 'DisplayName_Item_ReactorComponents', 'Thrust': 'DisplayName_Item_ThrustComponents', 'GravityGenerator': 'DisplayName_Item_GravityGeneratorComponents', 'Medical': 'DisplayName_Item_MedicalComponents', 'RadioCommunication': 'DisplayName_Item_RadioCommunicationComponents', 'Detector': 'DisplayName_Item_DetectorComponents', 'Explosives': 'DisplayName_Item_Explosives', 'SolarCell': 'DisplayName_Item_SolarCell', 'PowerCell': 'DisplayName_Item_PowerCell', 'Canvas': 'DisplayName_Item_CanvasCartridge', 'EngineerPlushie': 'DisplayName_Block_EngineerPlushie', 'SabiroidPlushie': 'DisplayName_Block_SabiroidPlushie', 'PrototechFrame': 'DisplayName_Item_PrototechFrame', 'PrototechPanel': 'DisplayName_Item_PrototechPanel', 'PrototechCapacitor': 'DisplayName_Item_PrototechCapacitor', 'PrototechPropulsionUnit': 'DisplayName_Item_PrototechPropulsionUnit', 'PrototechMachinery': 'DisplayName_Item_PrototechMachinery', 'PrototechCircuitry': 'DisplayName_Item_PrototechCircuitry', 'PrototechCoolingUnit': 'DisplayName_Item_PrototechCoolingUnit'}
ingot_displaynames = {'Stone': 'DisplayName_Item_Gravel', 'Iron': 'DisplayName_Item_IronIngot', 'Nickel': 'DisplayName_Item_NickelIngot', 'Cobalt': 'DisplayName_Item_CobaltIngot', 'Magnesium': 'DisplayName_Item_MagnesiumPowder', 'Silicon': 'DisplayName_Item_SiliconWafer', 'Silver': 'DisplayName_Item_SilverIngot', 'Gold': 'DisplayName_Item_GoldIngot', 'Platinum': 'DisplayName_Item_PlatinumIngot', 'Uranium': 'DisplayName_Item_UraniumIngot', 'Scrap': 'DisplayName_Item_ScrapIngot', 'PrototechScrap': 'DisplayName_Item_PrototechScrap'}

translations = {}
displayname_map = {}
component_to_ingot_ratios = {}

def load_translations(lang):
    translations = {}
    for fname in LOCALIZATION_FILES[lang]:
        try:
            tree = ET.parse(fname)
            root = tree.getroot()
            for data in root.findall(".//data"):
                name = data.attrib.get("name")
                value = data.findtext("value", default="")
                if name and value:
                    translations[name] = value
        except Exception as e:
            print(f"Erreur traduction {fname}: {e}")
    return translations



selected_lang = "fr"  # valeur par défaut, sera mise à jour dynamiquement




def trad(subtype_id, category="block"):
    # Exceptions manuelles traduites selon la langue choisie
    if category == "ingot":
        if subtype_id == "Stone":
            return "Gravier (Stone)" if selected_lang == "fr" else "Gravel (Stone)"
        elif subtype_id == "Silicon":
            return "Plaquette de silicium (Silicon)" if selected_lang == "fr" else "Silicon Wafer (Silicon)"

    key = None
    label = None
    if category == "component":
        key = component_displaynames.get(subtype_id)
        label = translations.get(key) if key else None
    elif category == "ingot":
        key = ingot_displaynames.get(subtype_id)
        label = translations.get(key) if key else None
    else:
        key = displayname_map.get(subtype_id)
        label = translations.get(key) if key else None

    if label:
        return f"{label} ({subtype_id})"
    elif key:
        return f"{key} ({subtype_id})"
    return subtype_id




    # Exceptions manuelles pour deux lingots non traduits
    if category == "ingot":
        if subtype_id == "Stone":
            return "Gravier (Stone)"
        elif subtype_id == "Silicon":
            return "Plaquette de silicium (Silicon)"
    key = displayname_map.get(subtype_id)
    if category == "component":
        key = f"DisplayName_Item_{subtype_id}"
    elif category == "ingot":
        key = f"DisplayName_Item_{subtype_id}Ingot"
    label = translations.get(key) if key else None
    if label:
        return f"{label} ({subtype_id})"
    elif key:
        return f"{key} ({subtype_id})"
    return subtype_id


def parse_blueprint(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [b.text for b in root.findall(".//CubeBlocks/MyObjectBuilder_CubeBlock/SubtypeName") if b is not None]

def extract_block_components():
    block_components = {}
    for dirpath, _, files in os.walk(DATA_DIR):
        for fname in files:
            if fname.endswith(".sbc"):
                try:
                    tree = ET.parse(os.path.join(dirpath, fname))
                    root = tree.getroot()
                    for defn in root.findall(".//Definition"):
                        subtype = defn.findtext("Id/SubtypeId")
                        comps = defn.find("Components")
                        if subtype and comps is not None:
                            block_components[subtype] = {}
                            for c in comps.findall("Component"):
                                typ = c.attrib.get("Subtype")
                                qty = int(c.attrib.get("Count", 1))
                                block_components[subtype][typ] = block_components[subtype].get(typ, 0) + qty
                except:
                    continue
    return block_components

def extract_blueprint_ratios():
    ratio_map = {}
    try:
        tree = ET.parse(os.path.join(DATA_DIR, "Blueprints.sbc"))
        root = tree.getroot()
        for bp in root.findall(".//Blueprint"):
            result = bp.find("Result")
            if result is None:
                continue
            if result.attrib.get("TypeId") != "Component":
                continue
            component = result.attrib.get("SubtypeId")
            result_amt = float(result.attrib.get("Amount", 1))
            prereq = bp.find("Prerequisites")
            if prereq is None:
                continue
            for item in prereq.findall("Item"):
                if item.attrib.get("TypeId") == "Ingot":
                    ingot = item.attrib.get("SubtypeId")
                    ingot_amt = float(item.attrib.get("Amount", 1))
                    ratio = ingot_amt / result_amt
                    ratio_map.setdefault(component, []).append((ingot, ratio))
    except Exception as e:
        print("Erreur parsing Blueprints.sbc:", e)
    return ratio_map

def summarize_components(blocks, block_data):
    total = {}
    for b in blocks:
        for c, q in block_data.get(b, {}).items():
            total[c] = total.get(c, 0) + q
    return total

def calculate_ingots(components, blueprint_map):
    total = {}
    for c, q in components.items():
        if c in blueprint_map:
            for ingot, ratio in blueprint_map[c]:
                total[ingot] = total.get(ingot, 0) + (ratio * q) / 3
    return {k: float(f'{v:.2f}') for k, v in total.items()}

def start_interface(lang):
    global selected_lang
    selected_lang = lang
    global translations, displayname_map, component_to_ingot_ratios
    translations = load_translations(lang)
    component_to_ingot_ratios = extract_blueprint_ratios()

    # Load displayname map
    displayname_map = {}
    for dirpath, _, files in os.walk(DATA_DIR):
        for fname in files:
            if fname.endswith(".sbc"):
                try:
                    tree = ET.parse(os.path.join(dirpath, fname))
                    root = tree.getroot()
                    for defn in root.findall(".//Definition"):
                        subtype = defn.findtext("Id/SubtypeId")
                        display = defn.findtext("DisplayName")
                        if subtype and display:
                            displayname_map[subtype] = display
                except:
                    continue

    root = tk.Tk()
    root.title("Blueprint Viewer")
    root.geometry("1200x700")
    root.configure(bg="#2e2e2e")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#3e3e3e", foreground="white", fieldbackground="#3e3e3e", rowheight=25)
    style.configure("Treeview.Heading", background="#1e1e1e", foreground="white", font=('Helvetica', 10, 'bold'))

    btn_frame = tk.Frame(root, bg="#2e2e2e")
    btn_frame.pack(fill="x", pady=10)
    name_label = tk.Label(root, text="", bg="#2e2e2e", fg="white", font=("Arial", 12, "italic"))
    name_label.pack(pady=(0, 10))

    tk.Button(btn_frame, text="Importer blueprint", command=lambda: browse_file(), bg="#444", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Quitter", command=root.destroy, bg="#444", fg="white").pack(side="right", padx=10)

    
    # Ajout : Colonne gauche pour exploration local/workshop
    explorer_frame = tk.Frame(root, bg="#2e2e2e", width=220)
    explorer_frame.pack(side="left", fill="y", padx=(10, 5))

    explorer_tabs = ttk.Notebook(explorer_frame)
    local_tab = tk.Frame(explorer_tabs, bg="#2e2e2e")
    workshop_tab = tk.Frame(explorer_tabs, bg="#2e2e2e")
    explorer_tabs.add(local_tab, text="Local")
    explorer_tabs.add(workshop_tab, text="Workshop")
    explorer_tabs.pack(fill="both", expand=True)

    def create_listbox(tab, path):
        lb = tk.Listbox(tab, bg="#2e2e2e", fg="white", selectbackground="#007acc", font=("Segoe UI", 9))
        lb.pack(fill="both", expand=True)
        if os.path.exists(path):
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    lb.insert("end", item)

        def on_select(event):
            if not lb.curselection():
                return
            name = lb.get(lb.curselection()[0])
            file_path = os.path.join(path, name, "bp.sbc")
            if os.path.exists(file_path):
                tree = ET.parse(file_path)
                root_xml = tree.getroot()
                blueprint_id = root_xml.find(".//Id")
                blueprint_name = blueprint_id.attrib.get("Subtype", "Blueprint") if blueprint_id is not None else "Blueprint"
                owner = root_xml.findtext(".//DisplayName")
                if not owner or "DisplayName" in owner:
                    owner = "prefab"
                name_label.config(text=f"{blueprint_name} - par {owner}")
                blocks = parse_blueprint(file_path)
                block_data = extract_block_components()
                comps = summarize_components(blocks, block_data)
                ingots = calculate_ingots(comps, component_to_ingot_ratios)
                show_result(comps, blocks, ingots)

        lb.bind("<<ListboxSelect>>", on_select)
        return lb

    create_listbox(local_tab, os.path.join(os.getenv("APPDATA"), "SpaceEngineers", "Blueprints", "local"))
    create_listbox(workshop_tab, os.path.join(os.getenv("APPDATA"), "SpaceEngineers", "Blueprints", "workshop"))


    tree_frame = tk.Frame(root, bg="#2e2e2e")
    tree_frame.pack(fill="both", expand=True)

    def create_tree(parent, title):
        frame = tk.Frame(parent, bg="#2e2e2e")
        tk.Label(frame, text=title, bg="#2e2e2e", fg="white").pack()
        tree = ttk.Treeview(frame, columns=("Nom", "Quantité"), show="headings", height=25)
        tree.heading("Nom", text="Nom")
        tree.heading("Quantité", text="Quantité")
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        return tree

    comp_tree = create_tree(tree_frame, "Composants")
    ingot_tree = create_tree(tree_frame, "Lingots")
    block_tree = create_tree(tree_frame, "Blocs")


    def show_result(components, blocks, ingots):
        comp_tree.delete(*comp_tree.get_children())
        for c, q in components.items():
            comp_tree.insert("", "end", values=(trad(c, "component"), q))
        block_tree.delete(*block_tree.get_children())
        count = {}
        for b in blocks:
            count[b] = count.get(b, 0) + 1
        for b, q in count.items():
            block_tree.insert("", "end", values=(trad(b, "block"), q))
        ingot_tree.delete(*ingot_tree.get_children())
        for i, q in ingots.items():
            ingot_tree.insert("", "end", values=(trad(i, "ingot"), q))

    def browse_file():
        file = filedialog.askopenfilename(filetypes=[("SBC Files", "*.sbc")])
        if not file:
            return
        # Ajout : nom du blueprint et du propriétaire
        try:
            tree = ET.parse(file)
            root_xml = tree.getroot()
            blueprint_id = root_xml.find(".//Id")
            blueprint_name = blueprint_id.attrib.get("Subtype", "Blueprint") if blueprint_id is not None else "Blueprint"
            owner = root_xml.findtext(".//DisplayName")
            if not owner or "DisplayName" in owner:
                owner = "prefab"
            name_label.config(text=f"{blueprint_name} - par {owner}")
        except Exception as e:
            name_label.config(text="Nom non trouvé")

        blocks = parse_blueprint(file)
        block_data = extract_block_components()
        comps = summarize_components(blocks, block_data)
        ingots = calculate_ingots(comps, component_to_ingot_ratios)
        show_result(comps, blocks, ingots)

    root.mainloop()

# Choix langue au lancement
lang = tk.Tk()
lang.title("Langue")
lang.geometry("300x150")
lang.configure(bg="#2e2e2e")
tk.Label(lang, text="Choisissez une langue :", bg="#2e2e2e", fg="white", font=("Arial", 12)).pack(pady=20)
tk.Button(lang, text="Français", width=10, command=lambda: start_interface("fr"), bg="#444", fg="white").pack(pady=5)
tk.Button(lang, text="English", width=10, command=lambda: start_interface("en"), bg="#444", fg="white").pack(pady=5)
lang.mainloop()
