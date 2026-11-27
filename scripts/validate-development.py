#!/usr/bin/env python3
"""Validate candidate development config and assets before they are promoted."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    raise SystemExit(f"ERROR: {message}")


def no_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_pairs)
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")


def is_int(value, low, high):
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


index = load_json(ROOT / "game-index.json")
config = load_json(ROOT / "game-config.json")
master = load_json(ROOT / "chapter-master.json")
manifest = load_json(ROOT / "manifest.json")
if index.get("schemaVersion") != 1 or index.get("version") != 1:
    fail("Unsupported game-index schema")

symbols = index.get("elementSymbols")
if not isinstance(symbols, list) or len(symbols) != 118 or len(set(symbols)) != 118:
    fail("game-index must contain 118 unique element symbols")
if master.get("version") != 1 or len(master.get("elements", [])) != 118:
    fail("chapter-master must contain all 118 elements")
if {row.get("symbol") for row in master["elements"]} != set(symbols):
    fail("chapter-master element symbols differ from the game index")
levels = master.get("levels")
if not isinstance(levels, list) or len(levels) != 30:
    fail("chapter-master must contain exactly 30 levels")
for i, row in enumerate(levels, 1):
    if row.get("level") != i or not is_int(row.get("requiredFound"), 0, 118) or not is_int(row.get("unlockCap"), 1, 118):
        fail(f"Invalid level row {i}")
    if i > 1 and (row["requiredFound"] < levels[i-2]["requiredFound"] or row["unlockCap"] < levels[i-2]["unlockCap"]):
        fail(f"Level {i} regresses from the previous level")
    if row["requiredFound"] > row["unlockCap"]:
        fail(f"Level {i} requires more discoveries than its unlock cap")
if levels[0]["requiredFound"] != 0 or levels[-1]["unlockCap"] != 118:
    fail("Level 1 must start at zero and level 30 must unlock all 118 elements")
chapters = master.get("chapters")
expected_ranges = {1: [1, 15], 2: [16, 23], 3: [24, 30]}
if not isinstance(chapters, list) or len(chapters) != 3:
    fail("chapter-master must define three chapters")
for i, chapter in enumerate(chapters, 1):
    if chapter.get("chapter") != i or chapter.get("levelRange") != expected_ranges[i]:
        fail(f"Chapter {i} has an unexpected level range")
counts = {i: 0 for i in range(1, 4)}
for row in master["elements"]:
    chapter, level, symbol = row.get("chapter"), row.get("level"), row.get("symbol")
    if chapter not in counts or not is_int(level, 1, 30):
        fail(f"Invalid chapter or level for element {symbol}")
    low, high = expected_ranges[chapter]
    if not low <= level <= high:
        fail(f"Element {symbol} is assigned outside its chapter level range")
    z = index["elementAtomicNumbers"].get(symbol)
    if not is_int(z, 1, 118):
        fail(f"Element {symbol} is missing from the game index")
    facility = row.get("collectionFacility")
    if facility not in index["facilityIds"] or not all(isinstance(row.get(k), str) and row[k] for k in ("rawMaterial", "researchClass")):
        fail(f"Element {symbol} has incomplete collection/research data")
    counts[chapter] += 1
if counts != {1: 58, 2: 30, 3: 30}:
    fail(f"Chapter element totals are not 58/30/30: {counts}")
for i, chapter in enumerate(chapters, 1):
    if chapter.get("cumulativeElements") != sum(counts[n] for n in range(1, i+1)):
        fail(f"Chapter {i} cumulative element count is inconsistent")

if config.get("schemaVersion") != 1 or config.get("gameId") != "world-chem-collection" or not is_int(config.get("revision"), 0, 2**31-1):
    fail("Unsupported game-config schema, gameId, or revision")
index_materials = set(index["materialIds"])
index_routes = set(index["routeIds"])
index_reactions = set(index["reactionIds"])
index_facilities = {str(x) for x in index["facilityNodes"]}
area_names = set(index["materialAreas"])

ui = config.get("ui", {})
selectors = {"#brand", ".dock", ".dock button", ".glass", ".primary", ".secondary", ".sheet"}
properties = {"display", "flex-direction", "justify-content", "align-items", "gap", "order", "min-width", "min-height", "padding", "margin", "font-size", "color", "background-color", "border-radius", "text-align"}
if not isinstance(ui, dict) or not isinstance(ui.get("rules", []), list):
    fail("ui.rules must be an array")
for rule in ui.get("rules", []):
    if not isinstance(rule, dict) or rule.get("selector") not in selectors or not isinstance(rule.get("styles"), dict):
        fail("UI rule uses an unsupported selector or style map")
    for prop, value in rule["styles"].items():
        if prop not in properties or not isinstance(value, str) or len(value) > 48 or re.search(r"[{};]|url\s*\(|expression", value, re.I):
            fail(f"Unsafe or unsupported UI style: {prop}")
text_keys = {"titleMap", "titleMissions", "returnHome", "bag", "atlas"}
if not isinstance(ui.get("text", {}), dict) or set(ui.get("text", {})) - text_keys:
    fail("ui.text contains an unsupported target")
if any(not isinstance(v, str) or len(v) > 64 for v in ui.get("text", {}).values()):
    fail("UI text must be a string of at most 64 characters")

balance = config.get("balance", {})
if not isinstance(balance, dict) or ("rareDropProbability" in balance and (not isinstance(balance["rareDropProbability"], (int, float)) or isinstance(balance["rareDropProbability"], bool) or not 0 <= balance["rareDropProbability"] <= 1)):
    fail("rareDropProbability must be between 0 and 1")

facilities = config.get("facilities", {})
if not isinstance(facilities, dict):
    fail("facilities must be an object keyed by map node id")
for node, level in facilities.items():
    if node not in index_facilities or not is_int(level, 1, 30):
        fail(f"Invalid facility unlock override: {node}")
facility_unlocks = {4:1, 6:1, 10:10, 12:21, 16:16, 18:6, 19:24, 20:1, 24:1}
facility_unlocks.update({int(k):v for k,v in facilities.items()})
for row in master["elements"]:
    if row["rawMaterial"] == "仮想研究試料" or row["collectionFacility"] in {"原子核研究センター", "研究所"}:
        continue
    node = index["facilityIds"][row["collectionFacility"]]
    if facility_unlocks.get(node, 1) > row["level"]:
        fail(f"Softlock: {row['symbol']} requires {row['collectionFacility']} before it opens")

material_fields = {"name", "formula", "area", "tier", "sites", "source"}
materials = config.get("materials", {})
if not isinstance(materials, dict):
    fail("materials must be an object")
for material_id, patch in materials.items():
    if material_id not in index_materials or not isinstance(patch, dict) or set(patch) - material_fields:
        fail(f"Unknown material or field in materials.{material_id}")
    if "name" in patch and (not isinstance(patch["name"], str) or not patch["name"] or len(patch["name"]) > 80): fail(f"Invalid material name: {material_id}")
    if "formula" in patch and (not isinstance(patch["formula"], str) or len(patch["formula"]) > 64): fail(f"Invalid material formula: {material_id}")
    if "area" in patch and patch["area"] not in area_names: fail(f"Unknown material area: {material_id}")
    if "tier" in patch and not is_int(patch["tier"], 0, 30): fail(f"Invalid material tier: {material_id}")
    if "sites" in patch and (not isinstance(patch["sites"], list) or not patch["sites"] or any(not is_int(x, 0, 42) for x in patch["sites"])): fail(f"Invalid material sites: {material_id}")
    if "source" in patch and (not isinstance(patch["source"], str) or len(patch["source"]) > 120): fail(f"Invalid material source: {material_id}")

route_fields = {"tier", "parts", "method", "description", "site", "lab", "researchClass"}
routes = config.get("routes", {})
if not isinstance(routes, dict): fail("routes must be an object")
rows_by_z = {index["elementAtomicNumbers"][row["symbol"]]:row for row in master["elements"]}
for route_id, patch in routes.items():
    if route_id not in index_routes or not isinstance(patch, dict) or set(patch) - route_fields: fail(f"Unknown route or field: {route_id}")
    z=index["routeElements"].get(route_id); row=rows_by_z.get(z)
    if "tier" in patch and (not is_int(patch["tier"],1,30) or (row and patch["tier"]>row["level"])): fail(f"Route tier can block {route_id}")
    if "site" in patch and not is_int(patch["site"],0,42): fail(f"Invalid route site: {route_id}")
    if "lab" in patch and not is_int(patch["lab"],1,2): fail(f"Invalid route lab: {route_id}")
    if "parts" in patch:
        if not isinstance(patch["parts"], list) or any(not isinstance(x,list) or len(x)!=2 or x[0] not in index_materials or not is_int(x[1],1,99) for x in patch["parts"]): fail(f"Invalid or missing route material: {route_id}")
        for item, _ in patch["parts"]:
            tier=materials.get(item,{}).get("tier",index.get("materialTiers",{}).get(item,0))
            route_tier=patch.get("tier",row["level"] if row else 30)
            if tier>route_tier: fail(f"Softlock: {route_id} needs {item} before it is available")
    for field in ("method","description","researchClass"):
        if field in patch and (not isinstance(patch[field],str) or len(patch[field])>500): fail(f"Invalid route text: {route_id}")
    if "researchClass" in patch and patch["researchClass"] not in index["chapterResearchClasses"]: fail(f"Unknown research class: {route_id}")

reaction_fields = {"title", "parts", "out", "equation", "conditions", "courses", "art"}
reactions = config.get("reactions", {})
if not isinstance(reactions, dict): fail("reactions must be an object")
allowed_tokens = set(index["reactionMaterialTokens"])
atom_counts = index.get("reactionAtoms", {})
for reaction_id, patch in reactions.items():
    if reaction_id not in index_reactions or not isinstance(patch,dict) or set(patch)-reaction_fields: fail(f"Unknown reaction or field: {reaction_id}")
    for side in ("parts","out"):
        if side in patch and (not isinstance(patch[side],list) or not patch[side] or any(not isinstance(x,list) or len(x)!=2 or x[0] not in allowed_tokens or not is_int(x[1],1,99) for x in patch[side])): fail(f"Invalid reaction {side}: {reaction_id}")
    parts=patch.get("parts"); products=patch.get("out")
    if parts is not None and products is not None:
        all_tokens=[x[0] for x in parts+products]
        if all(token in atom_counts for token in all_tokens):
            left={};right={}
            for side,target in ((parts,left),(products,right)):
                for token,coef in side:
                    for atom,count in atom_counts[token].items(): target[atom]=target.get(atom,0)+count*coef
            if left != right: fail(f"Unbalanced reaction equation: {reaction_id}")
        else: fail(f"Cannot verify atom balance for reaction override: {reaction_id}")
    for field in ("title","equation","conditions","art"):
        if field in patch and (not isinstance(patch[field],str) or len(patch[field])>300): fail(f"Invalid reaction text: {reaction_id}")
    if "courses" in patch and (not isinstance(patch["courses"],list) or not patch["courses"] or any(not isinstance(x,str) or len(x)>32 for x in patch["courses"])): fail(f"Invalid reaction courses: {reaction_id}")

study = config.get("study", {})
if not isinstance(study,dict): fail("study must be an object")
for key,patch in study.items():
    if key not in index["chapterResearchClasses"] or not isinstance(patch,dict) or set(patch)-{"question","correct","wrong","hint"}: fail(f"Unknown study content: {key}")
    for field in ("question","correct","hint"):
        if field in patch and (not isinstance(patch[field],str) or not patch[field] or len(patch[field])>240): fail(f"Invalid study text: {key}.{field}")
    if "wrong" in patch and (not isinstance(patch["wrong"],list) or len(patch["wrong"])!=2 or any(not isinstance(x,str) or not x or len(x)>160 for x in patch["wrong"])): fail(f"Invalid study choices: {key}")

story = config.get("story", {})
if not isinstance(story,dict) or set(story)-{"chapterOneClear"}: fail("Unsupported story key")
scenes=story.get("chapterOneClear",[])
if not isinstance(scenes,list): fail("chapterOneClear must be an array")
seen=set()
for scene in scenes:
    if not isinstance(scene,dict) or not is_int(scene.get("index"),0,6) or scene["index"] in seen: fail("Invalid or repeated chapter-one scene index")
    seen.add(scene["index"])
    if "speaker" in scene and (not isinstance(scene["speaker"],str) or len(scene["speaker"])>32): fail("Invalid scene speaker")
    if "text" in scene and (not isinstance(scene["text"],str) or not scene["text"] or len(scene["text"])>400): fail("Invalid scene text")

if manifest.get("schemaVersion") != 1:
    fail("Unsupported manifest schema")
asset_fields={"materials":"materials","missionMaterials":"mission-materials","experiments":"experiments"}
total=0
for field,directory in asset_fields.items():
    mappings=manifest.get(field)
    if not isinstance(mappings,dict): fail(f"manifest.{field} must be an object")
    for asset_id,rel in mappings.items():
        if not isinstance(asset_id,str) or not asset_id or not isinstance(rel,str): fail(f"Invalid manifest mapping in {field}")
        pattern={"materials":r"^materials/[a-z0-9-]+/v[0-9]+\.(?:png|webp)$","missionMaterials":r"^mission-materials/[a-z0-9-]+/v[0-9]+\.(?:png|webp)$","experiments":r"^experiments/[a-z0-9-]+/[a-z0-9-]+-v[0-9]+\.(?:png|webp)$"}[field]
        if not re.fullmatch(pattern,rel,re.I): fail(f"Unsafe or invalid asset path: {field}.{asset_id} -> {rel}")
        image=(ROOT/rel).resolve()
        if ROOT.resolve() not in image.parents or not image.is_file() or image.stat().st_size<100: fail(f"Missing or empty asset: {rel}")
        total+=1
if total == 0: fail("No image mappings found")
print(f"Validated 118 elements, 30 levels, 3 chapters, {total} image mappings, and runtime override consistency")
