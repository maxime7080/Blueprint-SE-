"""
Blueprint Viewer pour Space Engineers
Version PySide6 avec interface moderne
Convertie depuis la version Tkinter originale
"""

import os
import sys
import xml.etree.ElementTree as ET
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTabWidget, QListWidget, 
    QTreeWidget, QTreeWidgetItem, QFrame, QScrollArea, QSplitter,
    QHeaderView, QStackedLayout
)
from PySide6.QtGui import QPixmap, QIcon, QImage, QPalette, QBrush, QPainter
from PySide6.QtCore import Qt, QSize

# Dictionnaire des noms d'affichage des composants
component_displaynames = {
    'Construction': 'DisplayName_Item_ConstructionComponent', 
    'MetalGrid': 'DisplayName_Item_MetalGrid', 
    'InteriorPlate': 'DisplayName_Item_InteriorPlate', 
    'SteelPlate': 'DisplayName_Item_SteelPlate', 
    'Girder': 'DisplayName_Item_Girder', 
    'SmallTube': 'DisplayName_Item_SmallSteelTube', 
    'LargeTube': 'DisplayName_Item_LargeSteelTube', 
    'Motor': 'DisplayName_Item_Motor', 
    'Display': 'DisplayName_Item_Display', 
    'BulletproofGlass': 'DisplayName_Item_BulletproofGlass', 
    'Superconductor': 'DisplayName_Item_Superconductor', 
    'Computer': 'DisplayName_Item_Computer', 
    'Reactor': 'DisplayName_Item_ReactorComponents', 
    'Thrust': 'DisplayName_Item_ThrustComponents', 
    'GravityGenerator': 'DisplayName_Item_GravityGeneratorComponents', 
    'Medical': 'DisplayName_Item_MedicalComponents', 
    'RadioCommunication': 'DisplayName_Item_RadioCommunicationComponents', 
    'Detector': 'DisplayName_Item_DetectorComponents', 
    'Explosives': 'DisplayName_Item_Explosives', 
    'SolarCell': 'DisplayName_Item_SolarCell', 
    'PowerCell': 'DisplayName_Item_PowerCell', 
    'Canvas': 'DisplayName_Item_CanvasCartridge',
    'EngineerPlushie': 'DisplayName_Block_EngineerPlushie', 
    'SabiroidPlushie': 'DisplayName_Block_SabiroidPlushie',
    'PrototechFrame': 'DisplayName_Item_PrototechFrame',
    'PrototechPanel': 'DisplayName_Item_PrototechPanel',
    'PrototechCapacitor': 'DisplayName_Item_PrototechCapacitor',
    'PrototechPropulsionUnit': 'DisplayName_Item_PrototechPropulsionUnit',
    'PrototechMachinery': 'DisplayName_Item_PrototechMachinery',
    'PrototechCircuitry': 'DisplayName_Item_PrototechCircuitry',
    'PrototechCoolingUnit': 'DisplayName_Item_PrototechCoolingUnit',
    'PrototechScrap': 'DisplayName_Item_PrototechScrap',
    'LgParachute': 'DisplayName_Item_LgParachute'
}

# Noms de composants alternatifs (pour compatibilité)
fallback_component_displaynames = {
    "Reactor": "DisplayName_Item_ReactorComponent",
    "Detector": "DisplayName_Item_DetectorComponent",
    "Medical": "DisplayName_Item_MedicalComponent",
    "Thrust": "DisplayName_Item_ThrustComponent",
    "RadioCommunication": "DisplayName_Item_RadioCommunicationComponent",
    "GravityGenerator": "DisplayName_Item_GravityGeneratorComponent",
    "SolarCell": "DisplayName_Item_SolarCellComponent"
}

# Définition des chemins
DATA_DIR = "data"
TEXTURES_DIR = "Textures"
COMPONENT_ICONS_DIR = os.path.join(TEXTURES_DIR, "GUI", "Icons", "component")
INGOT_ICONS_DIR = os.path.join(TEXTURES_DIR, "GUI", "Icons", "ingot")
CUBES_ICONS_DIR = os.path.join(TEXTURES_DIR, "GUI", "Icons", "Cubes")

# Fichiers de localisation
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

# Variables globales
translations = {}
displayname_map = {}
component_to_ingot_ratios = {}
component_icons = {}
ingot_icons = {}
block_icons = {}
block_icons_paths = {}
selected_lang = "en"  # langue par défaut

# Traductions pour les éléments d'interface
ui_translations = {
    "en": {
        "open_file_button": "Open blueprint file...",
        "language_button": "Language",
        "refresh_data_button": "Refresh data",
        "select_blueprint": "Select a blueprint",
        "no_preview": "No preview available"
    },
    "fr": {
        "open_file_button": "Ouvrir un fichier blueprint...",
        "language_button": "Langue",
        "refresh_data_button": "Rafraîchir les données",
        "select_blueprint": "Sélectionnez un blueprint",
        "no_preview": "Pas d'aperçu disponible"
    }
}

# Fonctions utilitaires
def load_translations(lang):
    """Charge les traductions depuis les fichiers de localisation"""
    translations = {}
    for fname in LOCALIZATION_FILES.get(lang, []):
        try:
            tree = ET.parse(fname)
            root = tree.getroot()
            for data in root.findall(".//data"):
                name = data.get("name")
                if name:
                    value = data.find("value")
                    if value is not None and value.text:
                        translations[name] = value.text
        except Exception as e:
            print(f"Erreur traduction {fname}: {e}")
    return translations

def trad(subtype_id, category="block"):
    """Traduit un ID en nom localisé"""
    # Exceptions manuelles
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
        
        if not label and subtype_id in fallback_component_displaynames:
            key = fallback_component_displaynames[subtype_id]
            label = translations.get(key)
            
    elif category == "block":
        key = displayname_map.get(subtype_id)
        label = translations.get(key) if key else None
    
    elif category == "ingot":
        if subtype_id == "Stone":
            key = "DisplayName_Item_Gravel"
        else:
            key = f"DisplayName_Item_{subtype_id}Ingot"
        label = translations.get(key)
    
    if not label:
        return subtype_id
    return label

def parse_blueprint(file_path):
    """Parse un fichier blueprint et retourne la liste des blocs"""
    blocks = []
    try:
        tree = ET.parse(file_path)
        for block in tree.findall(".//MyObjectBuilder_CubeBlock"):
            subtype = block.findtext("SubtypeName")
            if subtype:
                blocks.append(subtype)
    except Exception as e:
        print(f"Erreur parsing {file_path}: {e}")
    return blocks

def extract_block_components():
    """Extrait les composants nécessaires pour chaque bloc depuis les fichiers SBC"""
    block_data = {}
    for dirpath, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.endswith(".sbc"):
                try:
                    tree = ET.parse(os.path.join(dirpath, filename))
                    root = tree.getroot()
                    for definition in root.findall(".//Definition"):
                        id_elem = definition.find("Id")
                        if id_elem is not None:
                            subtype = id_elem.findtext("SubtypeId")
                            if subtype:
                                components = {}
                                for component in definition.findall(".//Component"):
                                    comp_subtype = component.get("Subtype")
                                    count = component.get("Count")
                                    if comp_subtype and count and count.isdigit():
                                        components[comp_subtype] = components.get(comp_subtype, 0) + int(count)
                                if components:
                                    block_data[subtype] = components
                except Exception as e:
                    print(f"Erreur extraction {os.path.join(dirpath, filename)}: {e}")
    return block_data

def extract_blueprint_ratios():
    """Extrait les ratios de conversion composants -> lingots"""
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
    """Résume les composants nécessaires pour tous les blocs"""
    components = {}
    for block in blocks:
        if block in block_data:
            for comp, count in block_data[block].items():
                components[comp] = components.get(comp, 0) + count
    return components

def calculate_ingots(components, blueprint_map):
    """Calcule les lingots nécessaires pour les composants"""
    total = {}
    for c, q in components.items():
        if c in blueprint_map:
            for ingot, ratio in blueprint_map[c]:
                total[ingot] = total.get(ingot, 0) + (ratio * q) / 3
    return {k: float(f'{v:.2f}') for k, v in total.items()}

def extract_pcu_values():
    """Extrait les valeurs PCU pour chaque bloc"""
    pcu_data = {}
    for dirpath, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.endswith(".sbc"):
                try:
                    tree = ET.parse(os.path.join(dirpath, filename))
                    root = tree.getroot()
                    for defn in root.findall(".//Definition"):
                        subtype = defn.findtext("Id/SubtypeId")
                        pcu = defn.findtext("PCU")
                        if subtype and pcu and pcu.isdigit():
                            pcu_data[subtype] = int(pcu)
                except Exception as e:
                    continue
    return pcu_data

def load_icons():
    """Charge les icônes depuis les dossiers de textures"""
    global component_icons, ingot_icons, block_icons
    
    # Fonction pour rechercher récursivement dans tous les sous-dossiers
    def search_icons_recursive(base_dir, icon_dict):
        if not os.path.exists(base_dir):
            return
            
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.png'):
                    try:
                        img_path = os.path.join(root, file)
                        # Extraire le nom sans extension
                        icon_name = os.path.splitext(file)[0]
                        
                        # Nettoyer le nom (enlever les suffixes comme _component)
                        for suffix in ["_component", "Component", "_Icon", "Component_", "Icon_", "Icon"]:
                            icon_name = icon_name.replace(suffix, "")
                        
                        # Normaliser le nom
                        icon_name = icon_name.lower()
                        
                        # Ajouter au dictionnaire
                        icon_dict[icon_name] = img_path
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'icône {file}: {e}")
    
    # Rechercher les icônes des composants
    search_icons_recursive(COMPONENT_ICONS_DIR, component_icons)
    
    # Rechercher les icônes des lingots
    search_icons_recursive(INGOT_ICONS_DIR, ingot_icons)
    
    # Rechercher les icônes des blocs
    search_icons_recursive(CUBES_ICONS_DIR, block_icons)
    
    # Essayer de trouver les icônes dans d'autres dossiers si nécessaire
    # Parfois les icônes des composants peuvent être dans d'autres sous-dossiers
    additional_dirs = [
        "Textures/GUI/Icons/Components",
        "Textures/GUI/Icons/Ingots",
        "Textures/GUI/Icons/Cubes",
        "Textures/GUI/Icons/Materials",
        "Textures/GUI/Icons/Items"
    ]
    
    for dir_path in additional_dirs:
        full_path = os.path.join(DATA_DIR, dir_path)
        if os.path.exists(full_path):
            search_icons_recursive(full_path, component_icons)
            search_icons_recursive(full_path, ingot_icons)
            search_icons_recursive(full_path, block_icons)

def create_default_icon(size=(24, 24), color='#aaaaaa'):
    """Crée une icône par défaut pour les éléments sans icône"""
    from PIL import Image, ImageDraw
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Dessiner un carré avec un ? au milieu
    draw.rectangle([(2, 2), (size[0]-2, size[1]-2)], outline=color, width=1)
    draw.line([(size[0]//2, 5), (size[0]//2, size[1]-8)], fill=color, width=2)
    draw.ellipse([(size[0]//2-2, size[1]-7), (size[0]//2+2, size[1]-3)], fill=color)
    # Convertir en QPixmap
    img_data = img.convert("RGBA").tobytes("raw", "RGBA")
    qimg = QImage(img_data, img.width, img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)

def get_component_icon(component_name):
    """Recherche l'icône d'un composant dans le dictionnaire des icônes"""
    # Essayer avec le nom exact (normalisé)
    comp_name_lower = component_name.lower()
    if comp_name_lower in component_icons:
        return pixmap_from_path(component_icons[comp_name_lower])
    
    # Cas spécial pour PrototechScrap
    if "prototech" in comp_name_lower or "scrap" in comp_name_lower or "protoc" in comp_name_lower:
        # Rechercher dans tous les dossiers d'images
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and any(keyword in file.lower() for keyword in ["proto", "prototech", "scrap"]):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Cas spécial pour LgParachute
    if "lgparachute" in comp_name_lower or "parachute" in comp_name_lower:
        # Rechercher dans tous les dossiers d'images
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and any(keyword in file.lower() for keyword in ["lgparachute", "parachute"]):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Traductions et mappings manuels
    special_cases = {
        "steelplate": ["steel", "plate", "steelplate"],
        "interiorplate": ["interior", "plate", "interiorplate"],
        "constructioncomponent": ["construction", "constructioncomponent", "construction_component"],
        "metalgrid": ["metal", "grid", "metalgrid"],
        "smalltube": ["small", "tube", "smalltube", "small_tube", "smallsteeltube"],
        "largetube": ["large", "tube", "largetube", "large_tube", "largesteeltube"],
        "motor": ["motor", "motors", "motorcomponent"],
        "display": ["display", "displays", "displaycomponent"],
        "computercmponent": ["computer", "computers", "computercomponent"],
        "detector": ["detector", "detectorcomponent"],
        "girder": ["girder", "component", "girdercomponent"],
        "gravitycomponent": ["gravity", "gravitygenerator", "gravitygeneratorcomponent"],
        "medical": ["medical", "medicalcomponent"],
        "powercell": ["power", "cell", "powercell", "battery"],
        "radiocommunication": ["radio", "communication", "radiocommunication"],
        "reactor": ["reactor", "reactorcomponent"],
        "solarcell": ["solar", "cell", "solarcell"],
        "superconductor": ["super", "conductor", "superconductor"],
        "thruster": ["thrust", "thruster", "thrustcomponent"],
        "bulletproofglass": ["bullet", "bulletproof", "glass", "bulletproofglass"],
        "energyweaponcomponent": ["energy", "weapon", "energyweaponcomponent"],
        "explosives": ["explosive", "explosives"],
        "prototechframe": ["prototech", "proto", "frame", "circuit", "protoc"],
        "prototechcapacitor": ["capacitor", "prototech", "protoc"],
        "prototechtank": ["tank", "prototech", "protoc"],
        "prototechtube": ["tube", "prototech", "protoc"],
        "prototypecircuit": ["circuit", "prototype", "protoc", "proto"],
        "prototechpanel": ["panel", "prototech", "proto"]
    }
    
    # Rechercher dans tous les cas spéciaux
    for base, variations in special_cases.items():
        if any(v in comp_name_lower for v in variations):
            for key in component_icons:
                if any(v in key for v in variations):
                    return pixmap_from_path(component_icons[key])
                    
    # Cas particulier pour Stone/Gravel
    if "stone" in comp_name_lower or "gravel" in comp_name_lower:
        # Rechercher dans tous les dossiers d'images
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and ('stone' in file.lower() or 'gravel' in file.lower()):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Essayer avec différentes variations du nom
    for key in component_icons.keys():
        if comp_name_lower in key or key in comp_name_lower:
            return pixmap_from_path(component_icons[key])
    
    # Si toujours pas trouvé, rechercher partiellement
    for part in comp_name_lower.split():
        if len(part) > 3:  # Éviter les mots trop courts
            for key in component_icons:
                if part in key or key in part:
                    return pixmap_from_path(component_icons[key])
    
    # Si aucune correspondance n'est trouvée, retourner une icône par défaut
    print(f"Icône non trouvée pour le composant: {component_name}")
    return create_default_icon()

def get_ingot_icon(ingot_name):
    """Recherche l'icône d'un lingot dans le dictionnaire des icônes"""
    # Essayer avec le nom exact (normalisé)
    ingot_name_lower = ingot_name.lower()
    if ingot_name_lower in ingot_icons:
        return pixmap_from_path(ingot_icons[ingot_name_lower])
    
    # Cas spéciaux pour les lingots
    special_cases = {
        "iron": ["iron", "ironingot", "iron_ingot", "feingot"],
        "nickel": ["nickel", "nickelingot", "nickel_ingot"],
        "cobalt": ["cobalt", "cobaltingot", "cobalt_ingot"],
        "silicon": ["silicon", "siliconingot", "siliconwafer", "silicon_wafer"],
        "silver": ["silver", "silveringot", "silver_ingot"],
        "gold": ["gold", "goldingot", "gold_ingot"],
        "platinum": ["platinum", "platinumingot", "platinum_ingot"],
        "uranium": ["uranium", "uraniumingot", "uranium_ingot"],
        "magnesium": ["magnesium", "magnesiumingot", "magnesium_powder", "magnesiumpowder"],
        "stone": ["stone", "gravel", "stonedust", "rock", "pebble", "ore"]
    }
    
    # Rechercher dans tous les cas spéciaux
    for base, variations in special_cases.items():
        if any(v in ingot_name_lower for v in variations):
            for key in ingot_icons:
                if any(v in key for v in variations):
                    return pixmap_from_path(ingot_icons[key])
                    
    # Cas particulier pour Stone/Gravel
    if "stone" in ingot_name_lower or "gravel" in ingot_name_lower:
        # Rechercher dans tous les dossiers d'images
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and ('stone' in file.lower() or 'gravel' in file.lower()):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Essayer avec différentes variations du nom
    for key in ingot_icons.keys():
        if ingot_name_lower in key or key in ingot_name_lower:
            return pixmap_from_path(ingot_icons[key])
    
    # Si aucune correspondance n'est trouvée, retourner une icône par défaut
    print(f"Icône non trouvée pour le lingot: {ingot_name}")
    return create_default_icon()

def get_block_icon(block_name):
    """Recherche l'icône d'un bloc dans le dictionnaire des icônes"""
    # Essayer avec le nom exact (normalisé)
    block_name_lower = block_name.lower()
    if block_name_lower in block_icons:
        return pixmap_from_path(block_icons[block_name_lower])
    
    # Si le bloc a un chemin d'icône défini dans les fichiers SBC
    if block_name in block_icons_paths:
        icon_path = block_icons_paths[block_name]
        base_path = os.path.join(DATA_DIR, icon_path)
        if os.path.exists(base_path):
            return pixmap_from_path(base_path)
    
    # Cas spécial pour LgParachute
    if "lgparachute" in block_name_lower or "parachute" in block_name_lower:
        # Rechercher dans tous les dossiers d'images
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and any(keyword in file.lower() for keyword in ["parachute", "chute"]):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Traductions et mappings manuels pour les blocs
    special_cases = {
        "largeblock": ["large", "block", "bigblock"],
        "smallblock": ["small", "block", "smallblock"],
        "reactor": ["reactor", "reactorblock", "nuclearreactor"],
        "assembler": ["assembler", "assemblerblock", "crafter"],
        "refinery": ["refinery", "refineryblock", "smelter"],
        "cargotainer": ["cargo", "container", "storage"],
        "thruster": ["thruster", "thrust", "propulsion"],
        "gyroscope": ["gyro", "gyroscope", "stabilizer"],
        "cockpit": ["cockpit", "control", "seat"],
        "turret": ["turret", "gun", "cannon", "weapon"],
        "gatlinggun": ["gatling", "gun", "minigun"],
        "missileturret": ["missile", "rocket", "launcher"],
        "antenna": ["antenna", "communication", "radio"],
        "medical": ["medical", "medicalroom", "healthstation"],
        "gravity": ["gravity", "gravitygenerator", "antigrav"],
        "conveyor": ["conveyor", "conveyortube", "transporter"],
        "solarpanel": ["solar", "panel", "solarenergy"],
        "batteryblock": ["battery", "accumulator", "power"],
        "drill": ["drill", "miner", "excavator"],
        "grinder": ["grinder", "cutter", "salvager"],
        "welder": ["welder", "repair", "builder"],
        "piston": ["piston", "actuator", "extender"],
        "rotor": ["rotor", "motor", "rotator"],
        "hinge": ["hinge", "joint", "connector"],
        "door": ["door", "gate", "entrance"],
        "window": ["window", "glass", "porthole"],
        "lightblock": ["light", "lamp", "illumination"],
        "wheel": ["wheel", "tire", "suspension"]
    }
    
    # Cas spécial pour les blocs avec des noms similaires
    if any(keyword in block_name_lower for keyword in ["armor", "lightarmor", "heavyarmor", "plate", "block"]):
        # Rechercher dans tous les dossiers d'images pour les blocs d'armure
        texture_dir = os.path.join(DATA_DIR, "Textures")
        for root, dirs, files in os.walk(texture_dir):
            for file in files:
                if file.lower().endswith('.png') and any(keyword in file.lower() for keyword in ["armor", "lightarmor", "heavyarmor", "plate", "block"]):
                    return pixmap_from_path(os.path.join(root, file))
    
    # Rechercher dans les cas spéciaux
    for base, variations in special_cases.items():
        if any(v in block_name_lower for v in variations):
            for key in block_icons:
                if any(v in key for v in variations):
                    return pixmap_from_path(block_icons[key])
    
    # Essayer avec différentes variations du nom
    for key in block_icons.keys():
        if block_name_lower in key or key in block_name_lower:
            return pixmap_from_path(block_icons[key])
            
    # Rechercher partiellement si toujours pas trouvé
    for part in block_name_lower.split():
        if len(part) > 3:  # Éviter les mots trop courts
            for key in block_icons:
                if part in key or key in part:
                    return pixmap_from_path(block_icons[key])
    
    # Si aucune correspondance n'est trouvée, retourner une icône par défaut
    print(f"Icône non trouvée pour le bloc: {block_name}")
    return create_default_icon()

def pixmap_from_path(path, size=(24, 24)):
    """Charge une image depuis un chemin et la convertit en QPixmap"""
    try:
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize(size)
            img_data = img.convert("RGBA").tobytes("raw", "RGBA")
            qimg = QImage(img_data, img.width, img.height, QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimg)
        else:
            # Essayer avec d'autres séparateurs de chemin
            alt_path = path.replace("\\", "/")
            full_path = os.path.join(os.getcwd(), alt_path)
            if os.path.exists(full_path):
                img = Image.open(full_path)
                img = img.resize(size)
                img_data = img.convert("RGBA").tobytes("raw", "RGBA")
                qimg = QImage(img_data, img.width, img.height, QImage.Format_RGBA8888)
                return QPixmap.fromImage(qimg)
    except Exception as e:
        print(f"Erreur lors du chargement de l'image {path}: {e}")
    return create_default_icon()

def extract_block_icons():
    """Extrait les chemins d'icônes des blocs depuis les fichiers SBC"""
    global block_icons_paths
    
    cubeblock_path = os.path.join(DATA_DIR, "cubeblock")
    if not os.path.exists(cubeblock_path):
        print(f"Dossier cubeblock non trouvé: {cubeblock_path}")
        return {}
    
    for dirpath, _, files in os.walk(cubeblock_path):
        for filename in files:
            if filename.endswith(".sbc"):
                try:
                    tree = ET.parse(os.path.join(dirpath, filename))
                    root = tree.getroot()
                    
                    for definition in root.findall(".//Definition"):
                        # Extraire l'ID du bloc
                        id_elem = definition.find("Id/SubtypeId")
                        if id_elem is not None and id_elem.text:
                            block_id = id_elem.text
                            
                            # Extraire le chemin de l'icône
                            icon = definition.find("Icon")
                            if icon is not None and icon.text:
                                # Convertir le chemin .dds en .png
                                icon_path = icon.text.replace(".dds", ".png")
                                block_icons_paths[block_id] = icon_path
                except Exception as e:
                    print(f"Erreur lors de l'extraction des icônes de bloc depuis {filename}: {e}")
    
    return block_icons_paths

def refresh_data():
    """Recharge toutes les données depuis les fichiers SBC
    Utilisez cette fonction après une mise à jour des fichiers de jeu"""
    global translations, displayname_map, component_to_ingot_ratios, block_icons_paths
    
    # Vider les dictionnaires existants
    component_icons.clear()
    ingot_icons.clear()
    block_icons.clear()
    block_icons_paths.clear()
    
    # Recharger les icônes
    load_icons()
    
    # Recharger les mappings
    extract_block_icons()
    
    # Recharger les noms d'affichage
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
    
    # Recharger les traductions
    global translations
    translations.update(load_translations(selected_lang))
    
    # Recharger les ratios composants/lingots
    component_to_ingot_ratios = extract_blueprint_ratios()
    
    print("Données rechargées avec succès!")
    return True

class BlueprintViewer(QMainWindow):
    """Classe principale pour l'application de visualisation de blueprints"""
    
    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        global selected_lang
        selected_lang = language
        
        # Extraire les valeurs PCU si non déjà fait
        self.pcu_map = extract_pcu_values()
        
        # Charger les traductions
        global translations
        translations = load_translations(language)
        
        # Initialiser le dictionnaire displayname_map pour les blocs
        global displayname_map
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
        
        # Extraire les composants pour les blocs
        self.block_components = extract_block_components()
        
        # Extraire les icônes des blocs
        extract_block_icons()
        
        # Extraire les ratios composants-lingots
        global component_to_ingot_ratios
        if not component_to_ingot_ratios:
            component_to_ingot_ratios = extract_blueprint_ratios()
        
        # Charger les icônes
        load_icons()
        
        # Initialiser l'interface
        self.init_ui()
        
        # Charger le fond d'écran s'il existe
        #self.set_background_image()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Configuration de la fenêtre principale
        self.setWindowTitle("Space Engineers Blueprint Viewer - Modern UI")
        self.setMinimumSize(1200, 800)
        
        # Créer un widget central pour contenir tout le contenu
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Déterminer le chemin de base pour les ressources (compatible avec PyInstaller)
        if getattr(sys, 'frozen', False):
            # Si l'application est exécutée comme un exécutable PyInstaller
            base_path = sys._MEIPASS
        else:
            # Si l'application est exécutée comme un script Python normal
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Vérifier si le fond d'écran existe (d'abord en JPG, puis en PNG)
        background_path = None
        background_jpg_path = os.path.join(base_path, "Textures", "fond.jpg")
        background_png_path = os.path.join(base_path, "Textures", "fond.png")
        
        # Vérifier les chemins alternatifs si nous sommes dans un .exe
        if getattr(sys, 'frozen', False):
            # Chercher aussi dans le répertoire de l'exécutable lui-même
            exe_dir = os.path.dirname(sys.executable)
            alt_jpg_path = os.path.join(exe_dir, "Textures", "fond.jpg")
            alt_png_path = os.path.join(exe_dir, "Textures", "fond.png")
            
            # Vérifier ces chemins alternatifs
            if os.path.exists(alt_jpg_path):
                background_jpg_path = alt_jpg_path
            if os.path.exists(alt_png_path):
                background_png_path = alt_png_path
        
        # Vérifier JPG en priorité
        if os.path.exists(background_jpg_path):
            background_path = background_jpg_path
            print(f"Fond d'écran JPG trouvé: {background_path}")
        # Si pas de JPG, vérifier PNG
        elif os.path.exists(background_png_path):
            background_path = background_png_path
            print(f"Fond d'écran PNG trouvé: {background_path}")
        else:
            print(f"Aucun fond d'écran trouvé (ni JPG ni PNG)")
            print(f"Chemins recherchés: {background_jpg_path}, {background_png_path}")
            if getattr(sys, 'frozen', False):
                print(f"Chemins alternatifs: {alt_jpg_path}, {alt_png_path}")
        
        # Si un fond d'écran a été trouvé (peu importe le format)
        if background_path:
            # Créer une approche personnalisée pour ajuster l'image de fond
            # comme le mode "remplissage" de Windows
            try:
                # Charger l'image avec PIL pour obtenir ses dimensions
                img = Image.open(background_path)
                img_width, img_height = img.size
                img_ratio = img_width / img_height
                
                # Classe pour le widget central avec peinture personnalisée
                class CentralWidget(QWidget):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.background = QPixmap(background_path)
                        self.img_ratio = img_ratio
                    
                    def paintEvent(self, event):
                        # Dessiner l'arrière-plan de base
                        painter = QPainter(self)
                        painter.fillRect(self.rect(), Qt.black)
                        
                        # Calculer les dimensions pour remplir correctement
                        widget_width = self.width()
                        widget_height = self.height()
                        widget_ratio = widget_width / widget_height
                        
                        if widget_ratio > self.img_ratio:
                            # Widget plus large que l'image
                            target_width = widget_width
                            target_height = int(target_width / self.img_ratio)
                            x = 0
                            y = (widget_height - target_height) // 2
                        else:
                            # Widget plus étroit que l'image
                            target_height = widget_height
                            target_width = int(target_height * self.img_ratio)
                            x = (widget_width - target_width) // 2
                            y = 0
                        
                        # Dessiner l'image redimensionnée
                        scaled_bg = self.background.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        painter.drawPixmap(x, y, scaled_bg)
                
                # Remplacer le widget central par notre widget personnalisé
                self.setCentralWidget(None)  # Supprimer le widget central actuel
                custom_widget = CentralWidget()
                self.setCentralWidget(custom_widget)
                central_widget = custom_widget
            except Exception as e:
                print(f"Erreur lors de l'adaptation du fond d'écran: {e}")
                # En cas d'erreur, revenir à l'approche CSS
                css_path = background_path.replace("\\", "/")
                central_widget.setStyleSheet(f"""
                    #centralWidget {{
                        background-image: url('{css_path}');
                        background-position: center;
                        background-repeat: no-repeat;
                        background-size: cover;
                        background-color: #1a1a1a;
                    }}
                """)
                central_widget.setObjectName("centralWidget")
        else:
            print(f"Aucun fond d'écran trouvé")
            central_widget.setStyleSheet("background-color: #1a1a1a;")
        
        # Créer le layout principal
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Ajouter l'icône de l'application
        logo_paths = [
            "data/Textures/logo.png",
            "data/Textures/Icons/logo.png",
            "data/Textures/GUI/logo.png",
            "Textures/logo.png",
            "logo.png"
        ]
        
        # Variable pour stocker le chemin du logo si trouvé
        found_logo_path = None
        
        for path in logo_paths:
            if os.path.exists(path):
                app_icon = QIcon(path)
                self.setWindowIcon(app_icon)
                found_logo_path = path
                break
        
        self.setStyleSheet("""
            QMainWindow {
                color: white;
            }
            QWidget {
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
                background-color: transparent;
            }
            QPushButton {
                background-color: rgba(20, 20, 20, 0.85);
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(0, 122, 204, 0.9);
            }
            QTabWidget::pane {
                border: 1px solid rgba(85, 85, 85, 0.7);
                background-color: rgba(15, 15, 15, 0.8);
            }
            QTabBar::tab {
                background-color: rgba(20, 20, 20, 0.85);
                color: white;
                padding: 6px 12px;
                border: 1px solid rgba(85, 85, 85, 0.7);
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: rgba(0, 122, 204, 0.85);
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(40, 40, 40, 0.85);
            }
            QListWidget, QTreeWidget {
                background-color: rgba(10, 10, 10, 0.8);
                alternate-background-color: rgba(15, 15, 15, 0.8);
                color: white;
                border: 1px solid rgba(40, 40, 40, 0.8);
                border-radius: 4px;
            }
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: rgba(0, 122, 204, 0.85);
            }
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: rgba(30, 30, 30, 0.8);
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: rgba(10, 10, 10, 0.85);
                color: white;
                padding: 4px;
                border: 1px solid rgba(40, 40, 40, 0.7);
            }
            QScrollBar:vertical {
                background-color: rgba(10, 10, 10, 0.7);
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(60, 60, 60, 0.8);
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(90, 90, 90, 0.9);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QSplitter::handle {
                background-color: rgba(60, 60, 60, 0.7);
                height: 2px;
            }
        """)
        
        # Widget central et layout principal
        # Barre supérieure avec le logo
        top_bar = QHBoxLayout()
        
        # Logo à gauche
        self.logo_label = QLabel()
        if found_logo_path:
            logo_pixmap = QPixmap(found_logo_path)
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setFixedSize(40, 40)
        top_bar.addWidget(self.logo_label)
        
        # Barre de boutons à côté du logo
        button_bar = QHBoxLayout()
        
        # Bouton pour ouvrir un fichier
        browse_button = QPushButton(ui_translations[selected_lang]["open_file_button"])
        browse_button.setObjectName("browse_button")
        browse_button.clicked.connect(self.browse_file)
        button_bar.addWidget(browse_button)
        
        # Bouton pour changer de langue
        self.lang_button = QPushButton(ui_translations[selected_lang]["language_button"] + ": " + self.language.upper())
        self.lang_button.setObjectName("lang_button")
        self.lang_button.clicked.connect(self.switch_language)
        button_bar.addWidget(self.lang_button)
        
        # Bouton pour rafraîchir les données
        refresh_button = QPushButton(ui_translations[selected_lang]["refresh_data_button"])
        refresh_button.setObjectName("refresh_button")
        refresh_button.setToolTip("Recharger toutes les données des fichiers SBC (après une mise à jour)")
        refresh_button.clicked.connect(self.refresh_data_ui)
        button_bar.addWidget(refresh_button)
        
        # Ajouter un espace élastique pour pousser les labels vers la droite
        button_bar.addStretch(1)
        
        # Label pour le nom du blueprint
        self.name_label = QLabel(ui_translations[selected_lang]["select_blueprint"])
        self.name_label.setAlignment(Qt.AlignRight)
        button_bar.addWidget(self.name_label)
        
        # Label pour le PCU
        self.pcu_label = QLabel("Total PCU: 0")
        self.pcu_label.setAlignment(Qt.AlignRight)
        button_bar.addWidget(self.pcu_label)
        
        # Ajouter les barres au layout principal
        top_bar.addLayout(button_bar)
        self.main_layout.addLayout(top_bar)
        
        # Widget pour contenir les onglets et les listes
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer un QTabWidget pour les onglets de blueprints
        tabs = QTabWidget()
        
        # Créer des onglets pour les différents dossiers de blueprints
        locaux_tab = QWidget()
        locaux_layout = QHBoxLayout(locaux_tab)  # Changé en QHBoxLayout pour avoir les aperçus à côté
        
        # Création d'un layout pour la liste et les labels
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(5, 5, 5, 5)
        
        # Ajouter une liste de blueprints locaux
        list_layout.addWidget(QLabel("Blueprints Locaux"))
        blueprint_list = self.create_listbox(os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "SpaceEngineers", "Blueprints"))
        list_layout.addWidget(blueprint_list)
        
        # Ajouter le layout de liste au layout principal de l'onglet
        locaux_layout.addLayout(list_layout, 3)  # Rapport 3:1 pour la largeur
        
        # Création d'un layout pour l'aperçu à droite
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(5, 5, 5, 5)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        # Ajout du label d'aperçu dans ce layout
        self.image_label_local = QLabel("Pas d'aperçu disponible")
        self.image_label_local.setAlignment(Qt.AlignCenter)
        self.image_label_local.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); padding: 5px; border-radius: 3px;")
        self.image_label_local.setMinimumHeight(200)
        self.image_label_local.setMinimumWidth(300)
        preview_layout.addWidget(self.image_label_local)
        
        # Ajouter des informations supplémentaires sous l'aperçu
        self.bp_info_label = QLabel("")
        self.bp_info_label.setAlignment(Qt.AlignCenter)
        self.bp_info_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); padding: 5px; border-radius: 3px;")
        preview_layout.addWidget(self.bp_info_label)
        
        # Ajouter un espace élastique en bas
        preview_layout.addStretch(1)
        
        # Ajouter le layout d'aperçu au layout principal de l'onglet
        locaux_layout.addLayout(preview_layout, 1)
        
        # Créer un onglet pour les blueprints de workshop avec la même structure
        workshop_tab = QWidget()
        workshop_layout = QHBoxLayout(workshop_tab)
        
        # Layout pour la liste des blueprints workshop
        workshop_list_layout = QVBoxLayout()
        workshop_list_layout.setContentsMargins(5, 5, 5, 5)
        
        # Ajouter une liste de blueprints du workshop (si dossier existe)
        workshop_list_layout.addWidget(QLabel("Blueprints Workshop"))
        workshop_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "SpaceEngineers", "Blueprints", "Workshop")
        workshop_list = self.create_listbox(workshop_path)
        workshop_list_layout.addWidget(workshop_list)
        
        # Ajouter le layout de liste au layout principal
        workshop_layout.addLayout(workshop_list_layout, 3)
        
        # Layout pour l'aperçu des blueprints workshop
        workshop_preview_layout = QVBoxLayout()
        workshop_preview_layout.setContentsMargins(5, 5, 5, 5)
        workshop_preview_layout.setAlignment(Qt.AlignCenter)
        
        # Label d'aperçu pour l'onglet workshop
        self.image_label_workshop = QLabel("Pas d'aperçu disponible")
        self.image_label_workshop.setAlignment(Qt.AlignCenter)
        self.image_label_workshop.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); padding: 5px; border-radius: 3px;")
        self.image_label_workshop.setMinimumHeight(200)
        self.image_label_workshop.setMinimumWidth(300)
        workshop_preview_layout.addWidget(self.image_label_workshop)
        
        # Informations supplémentaires pour l'onglet workshop
        self.workshop_bp_info_label = QLabel("")
        self.workshop_bp_info_label.setAlignment(Qt.AlignCenter)
        self.workshop_bp_info_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); padding: 5px; border-radius: 3px;")
        workshop_preview_layout.addWidget(self.workshop_bp_info_label)
        
        # Ajouter un espace élastique en bas
        workshop_preview_layout.addStretch(1)
        
        # Ajouter le layout d'aperçu au layout principal
        workshop_layout.addLayout(workshop_preview_layout, 1)
        
        # Ajouter les onglets
        tabs.addTab(locaux_tab, "Blueprints Locaux")
        tabs.addTab(workshop_tab, "Blueprints Workshop")
        
        # Ajouter le tabwidget au layout
        content_layout.addWidget(tabs)
        
        # Ajouter le widget de contenu au layout principal
        self.main_layout.addWidget(content_widget)
        
        # Widget pour les TreeView (composants, lingots, blocs)
        trees_widget = QWidget()
        trees_widget.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.6); border-radius: 5px; padding: 5px; }")
        trees_layout = QHBoxLayout(trees_widget)
        trees_layout.setContentsMargins(10, 10, 10, 10)
        trees_layout.setSpacing(10)
        
        # Créer les TreeWidgets
        self.comp_tree = self.create_tree("Composants")
        trees_layout.addWidget(self.comp_tree)
        
        self.ingot_tree = self.create_tree("Lingots")
        trees_layout.addWidget(self.ingot_tree)
        
        self.block_tree = self.create_tree("Blocs")
        trees_layout.addWidget(self.block_tree)
        
        self.main_layout.addWidget(trees_widget, 1)  # Stretch
    
    def create_listbox(self, path):
        """Crée une QListWidget pour afficher les blueprints d'un dossier"""
        listbox = QListWidget()
        
        # Charger les blueprints si le dossier existe
        if os.path.exists(path):
            blueprint_files = []
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(".sbc"):
                        blueprint_files.append(os.path.join(dirpath, filename))
            
            # Trier alphabétiquement
            blueprint_files.sort()
            
            # Ajouter à la liste
            for file_path in blueprint_files:
                blueprint_name = os.path.basename(os.path.dirname(file_path))
                listbox.addItem(blueprint_name)
                # Stocker le chemin complet dans les données de l'élément
                item = listbox.item(listbox.count() - 1)
                item.setData(Qt.UserRole, file_path)
                
                # Charger l'image d'aperçu si elle existe
                thumb_dir = os.path.dirname(file_path)
                thumb_path = os.path.join(thumb_dir, "thumb.png")
                if os.path.exists(thumb_path):
                    item.setIcon(QIcon(thumb_path))
        
        # Connecter le signal de sélection
        listbox.itemClicked.connect(self.on_blueprint_selected)
        
        return listbox
    
    def create_tree(self, title):
        """Crée un QTreeWidget pour afficher les composants, lingots ou blocs"""
        tree = QTreeWidget()
        tree.setHeaderLabels(["Nom", "Quantité"])
        tree.setColumnWidth(0, 220)
        tree.setAlternatingRowColors(True)
        tree.setUniformRowHeights(True)
        
        # Configurer l'en-tête
        header = tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        return tree
    
    def on_blueprint_selected(self, item):
        """Gère la sélection d'un blueprint dans la liste"""
        file_path = item.data(Qt.UserRole)
        if not file_path:
            return
        
        # Déterminer quel onglet est actif pour mettre à jour le bon label d'aperçu
        active_tab_index = self.findChild(QTabWidget).currentIndex()
        # 0 = onglet local, 1 = onglet workshop
        if active_tab_index == 0:
            image_label = self.image_label_local
            info_label = self.bp_info_label
        else:
            image_label = self.image_label_workshop
            info_label = self.workshop_bp_info_label
        
        # Charger l'image d'aperçu
        thumb_dir = os.path.dirname(file_path)
        thumb_path = os.path.join(thumb_dir, "thumb.png")
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            # Redimensionner tout en conservant le ratio mais plus grand qu'avant
            pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.clear()
            image_label.setText(ui_translations[selected_lang]["no_preview"])
        
        # Charger les données du blueprint
        try:
            tree = ET.parse(file_path)
            root_xml = tree.getroot()
            blueprint_id = root_xml.find(".//Id")
            blueprint_name = blueprint_id.attrib.get("Subtype", "Blueprint") if blueprint_id is not None else "Blueprint"
            owner = root_xml.findtext(".//DisplayName")
            if not owner or "DisplayName" in owner:
                owner = "prefab"
            self.name_label.setText(f"{blueprint_name} - par {owner}")
            
            # Mettre à jour le label d'informations supplémentaires
            info_label.setText(f"{blueprint_name}\nPar: {owner}")
        except Exception as e:
            self.name_label.setText("Nom non trouvé")
            info_label.setText("Informations non disponibles")
        
        # Analyser le blueprint
        blocks = parse_blueprint(file_path)
        block_data = extract_block_components()
        comps = summarize_components(blocks, block_data)
        ingots = calculate_ingots(comps, component_to_ingot_ratios)
        
        # Afficher les résultats
        self.show_result(comps, blocks, ingots)
    
    def browse_file(self):
        """Ouvre une boîte de dialogue pour charger un fichier blueprint"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            ui_translations[selected_lang]["open_file_button"],
            "",
            "SBC Files (*.sbc)"
        )
        
        if not file_path:
            return
        
        # Déterminer quel onglet est actif pour mettre à jour le bon label d'aperçu
        active_tab_index = self.findChild(QTabWidget).currentIndex()
        # 0 = onglet local, 1 = onglet workshop
        if active_tab_index == 0:
            image_label = self.image_label_local
            info_label = self.bp_info_label
        else:
            image_label = self.image_label_workshop
            info_label = self.workshop_bp_info_label
        
        # Charger les données du blueprint
        try:
            tree = ET.parse(file_path)
            root_xml = tree.getroot()
            blueprint_id = root_xml.find(".//Id")
            blueprint_name = blueprint_id.attrib.get("Subtype", "Blueprint") if blueprint_id is not None else "Blueprint"
            owner = root_xml.findtext(".//DisplayName")
            if not owner or "DisplayName" in owner:
                owner = "prefab"
            self.name_label.setText(f"{blueprint_name} - par {owner}")
            
            # Mettre à jour le label d'informations supplémentaires
            info_label.setText(f"{blueprint_name}\nPar: {owner}")
        except Exception as e:
            self.name_label.setText("Nom non trouvé")
            info_label.setText("Informations non disponibles")
        
        # Charger l'image d'aperçu si disponible
        thumb_dir = os.path.dirname(file_path)
        thumb_path = os.path.join(thumb_dir, "thumb.png")
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            # Redimensionner tout en conservant le ratio
            pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.clear()
            image_label.setText(ui_translations[selected_lang]["no_preview"])
        
        # Analyser le blueprint
        blocks = parse_blueprint(file_path)
        block_data = extract_block_components()
        comps = summarize_components(blocks, block_data)
        ingots = calculate_ingots(comps, component_to_ingot_ratios)
        
        # Afficher les résultats
        self.show_result(comps, blocks, ingots)
    
    def show_result(self, components, blocks, ingots):
        """Affiche les résultats dans les TreeWidgets"""
        # Calculer le PCU total
        total_pcu = sum(self.pcu_map.get(b, 0) for b in blocks)
        self.pcu_label.setText(f"PCU Total: {total_pcu}")
        
        # Afficher les composants
        self.comp_tree.clear()
        for c, q in components.items():
            component_name = trad(c, "component")
            item = QTreeWidgetItem([component_name, str(q)])
            
            # Chercher l'icône correspondante
            icon_path = get_component_icon(c)
            if icon_path:
                pixmap = QPixmap(icon_path)
                item.setIcon(0, QIcon(pixmap))
            
            self.comp_tree.addTopLevelItem(item)
        
        # Afficher les blocs
        self.block_tree.clear()
        count = {}
        for b in blocks:
            count[b] = count.get(b, 0) + 1
        
        for b, q in count.items():
            block_name = trad(b, "block")
            item = QTreeWidgetItem([block_name, str(q)])
            
            # Utiliser le chemin d'icône du SBC
            icon_path = block_icons_paths.get(b)
            if icon_path:
                pixmap = QPixmap(icon_path)
                item.setIcon(0, QIcon(pixmap))
            else:
                # Essayer avec le dictionnaire de blocs
                icon_path = get_block_icon(b)
                if icon_path:
                    pixmap = QPixmap(icon_path)
                    item.setIcon(0, QIcon(pixmap))
            
            self.block_tree.addTopLevelItem(item)
        
        # Afficher les lingots
        self.ingot_tree.clear()
        for i, q in ingots.items():
            ingot_name = trad(i, "ingot")
            item = QTreeWidgetItem([ingot_name, str(round(q, 2))])
            
            # Chercher l'icône
            icon_path = get_ingot_icon(i)
            if icon_path:
                pixmap = QPixmap(icon_path)
                item.setIcon(0, QIcon(pixmap))
            
            self.ingot_tree.addTopLevelItem(item)
    
    def switch_language(self):
        """Change la langue de l'application"""
        global selected_lang
        if selected_lang == "en":
            selected_lang = "fr"
        else:
            selected_lang = "en"
            
        print(f"Changement de langue vers: {selected_lang}")
        
        # Mettre à jour les textes des boutons
        # 1. Bouton de navigation
        browse_button = self.findChild(QPushButton, "browse_button")
        if browse_button:
            browse_button.setText(ui_translations[selected_lang]["open_file_button"])
            print(f"Bouton de navigation mis à jour: {ui_translations[selected_lang]['open_file_button']}")
        
        # 2. Bouton de langue (this)
        self.lang_button.setText(f"{ui_translations[selected_lang]['language_button']}: {selected_lang.upper()}")
        print(f"Bouton de langue mis à jour: {ui_translations[selected_lang]['language_button']}: {selected_lang.upper()}")
        
        # 3. Bouton de rafraîchissement
        refresh_button = self.findChild(QPushButton, "refresh_button")
        if refresh_button:
            refresh_button.setText(ui_translations[selected_lang]["refresh_data_button"])
            print(f"Bouton de rafraîchissement mis à jour: {ui_translations[selected_lang]['refresh_data_button']}")
        
        # Recharger les traductions
        global translations
        translations = load_translations(selected_lang)
        
        # Rafraîchir l'interface
        self.refresh_ui()
    
    def refresh_ui(self):
        """Rafraîchit l'interface après un changement de langue"""
        # Mettre à jour les textes des boutons avec la nouvelle langue
        browse_button = self.findChild(QPushButton, "browse_button")
        if browse_button:
            browse_button.setText(ui_translations[selected_lang]["open_file_button"])
        
        refresh_button = self.findChild(QPushButton, "refresh_button")
        if refresh_button:
            refresh_button.setText(ui_translations[selected_lang]["refresh_data_button"])
        
        # Le bouton de langue est déjà mis à jour dans switch_language()
        
        # Mettre à jour le texte du label de sélection si aucun blueprint n'est sélectionné
        if self.name_label.text().startswith("Sélectionnez") or self.name_label.text().startswith("Select"):
            self.name_label.setText(ui_translations[selected_lang]["select_blueprint"])
            
        # Mettre à jour le message d'absence d'aperçu si nécessaire
        if hasattr(self, 'image_label_local') and (self.image_label_local.text() == ui_translations["fr"]["no_preview"] or self.image_label_local.text() == ui_translations["en"]["no_preview"]):
            self.image_label_local.setText(ui_translations[selected_lang]["no_preview"])
        
        # Récupérer les valeurs actuelles
        current_components = {}
        current_blocks = {}
        current_ingots = {}
        
        # Récupérer les composants
        for i in range(self.comp_tree.topLevelItemCount()):
            item = self.comp_tree.topLevelItem(i)
            name = item.text(0)
            quantity = int(item.text(1))
            # Trouver la clé originale
            for comp_key in component_displaynames:
                if trad(comp_key, "component") == name:
                    current_components[comp_key] = quantity
                    break
        
        # Récupérer les blocs
        for i in range(self.block_tree.topLevelItemCount()):
            item = self.block_tree.topLevelItem(i)
            name = item.text(0)
            quantity = int(item.text(1))
            # Trouver la clé originale (plus complexe)
            for block_key in self.pcu_map:
                if trad(block_key, "block") == name:
                    current_blocks[block_key] = quantity
                    break
        
        # Récupérer les lingots
        for i in range(self.ingot_tree.topLevelItemCount()):
            item = self.ingot_tree.topLevelItem(i)
            name = item.text(0)
            quantity = float(item.text(1))
            # Trouver la clé originale
            for ingot_key in ["Iron", "Nickel", "Silicon", "Cobalt", "Silver", "Gold", "Platinum", "Uranium", "Magnesium", "Stone"]:
                if trad(ingot_key, "ingot") == name:
                    current_ingots[ingot_key] = quantity
                    break
        
        # Recréer les blocs
        blocks_list = []
        for block, count in current_blocks.items():
            blocks_list.extend([block] * count)
        
        # Afficher avec les nouvelles traductions
        self.show_result(current_components, blocks_list, current_ingots)
    
    def refresh_data_ui(self):
        """Rafraîchit les données et l'interface"""
        refresh_data()
        self.refresh_ui()

    # def set_background_image(self):
    #     """Charge le fond d'écran depuis \Textures\fond.png s'il existe"""
    #     background_path = r"\Textures\fond.png"
        
    #     # Si le chemin commence par un backslash, le considérer comme relatif au répertoire courant
    #     if background_path.startswith("\\"):
    #         # Obtenir le répertoire courant et ajouter le chemin relatif
    #         current_dir = os.path.dirname(os.path.abspath(__file__))
    #         absolute_path = os.path.join(current_dir, background_path.lstrip("\\"))
    #     else:
    #         absolute_path = background_path
        
    #     print(f"Chemin du fond d'écran: {absolute_path}")
        
    #     if os.path.exists(absolute_path):
    #         try:
    #             # Approche plus directe avec QMainWindow et styleSheet
    #             # Cela applique le fond d'écran directement au widget central
    #             central_widget = QWidget(self)
    #             self.setCentralWidget(central_widget)
    #             central_widget.setObjectName("centralWidget")
                
    #             # Convertir le chemin en format compatible avec CSS (utiliser des slashes avant)
    #             css_path = absolute_path.replace("\\", "/")
                
    #             # Créer et configurer le style avec l'image de fond
    #             central_widget.setStyleSheet(f"""
    #                 #centralWidget {{
    #                     background-image: url('{css_path}');
    #                     background-position: center;
    #                     background-repeat: no-repeat;
    #                     background-size: cover;
    #                     background-color: #1a1a1a;
    #                 }}
    #             """)
                
    #             # Créer un layout pour le widget central
    #             self.main_layout = QVBoxLayout(central_widget)
                
    #             # Indiquer que le fond a été configuré
    #             self.background_configured = True
    #             print(f"Fond d'écran configuré: {css_path}")
    #             return True
    #         except Exception as e:
    #             print(f"Erreur lors de l'application du fond d'écran: {e}")
    #     else:
    #         print(f"Fichier de fond d'écran non trouvé: {absolute_path}")
        
    #     # Si on arrive ici, c'est que le fond n'a pas été configuré
    #     self.background_configured = False
    #     return False

# Point d'entrée de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Appliquer un style global (optionnel)
    app.setStyle("Fusion")
    
    # Ajouter l'icône de l'application au niveau global
    logo_paths = [
        "data/Textures/logo.png",
        "data/Textures/Icons/logo.png",
        "data/Textures/GUI/logo.png",
        "Textures/logo.png",
        "logo.png"
    ]
    
    for path in logo_paths:
        if os.path.exists(path):
            app_icon = QIcon(path)
            app.setWindowIcon(app_icon)
            break
    
    # Créer et afficher la fenêtre principale
    viewer = BlueprintViewer(selected_lang)
    viewer.show()
    
    # Exécuter l'application
    sys.exit(app.exec())
