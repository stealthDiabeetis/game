from pathlib import Path
import copy, glob, hashlib, json

PATH = Path("index.html")
EXPECTED_BASE_SHA256 = "1bcfc78db8cc0ce5716f1df9db8bd8521b079cc867336ac8c18451073a247449"
EXPECTED_FINAL_SHA256 = "9df969a8b168dc0193bf4b36d370d92f821b5591991b358580e37ce69c1a4d21"
DEFAULTS = {
    "createsLocation": False,
    "aliases": [],
    "unit": "each",
    "defaultQuantity": 1,
    "specs": "",
    "availability": "Common",
}
ULTRASONIC_COMMENT = """  /* INTERNAL ULTRASONIC JEWELRY CLEANER PASS — NOT USER-FACING (v547)
     - Added a common household ultrasonic jewelry cleaner benchmarked to a 600 mL / 42 kHz / 35 W unit at about 2.2 lb and $40.
     - Added search aliases for Ultrasonic Cleaner, Jewelry Cleaning Machine, and Ultrasonic Cleaning Bath.
  */
"""
NORMALIZER = """;
  // Restore catalog defaults omitted above to keep this single-file app compact.
  for (const item of GEAR_CATALOG) {
    if (item.createsLocation === undefined) item.createsLocation = false;
    if (item.aliases === undefined) item.aliases = [];
    if (item.unit === undefined) item.unit = 'each';
    if (item.defaultQuantity === undefined) item.defaultQuantity = 1;
    if (item.specs === undefined) item.specs = '';
    if (item.availability === undefined) item.availability = 'Common';
  }"""

data = PATH.read_bytes()
actual_base = hashlib.sha256(data).hexdigest()
if actual_base != EXPECTED_BASE_SHA256:
    raise SystemExit(f"Refusing to transform unexpected index.html: {actual_base}")
new_items = []
for filename in sorted(glob.glob(".chatgpt-v548-items-*.json")):
    new_items.extend(json.loads(Path(filename).read_text(encoding="utf-8")))
if [item["id"] for item in new_items] != [f"gc{i}" for i in range(2372, 2410)]:
    raise SystemExit("Unexpected v548 transfer item set")
insert_item = new_items[0]
append_items = new_items[1:]

s = data.decode("utf-8")
s = s.replace("Character Sheet v545", "Character Sheet v548", 1)
marker = "  const GEAR_CATALOG = "
marker_pos = s.index(marker)
s = s[:marker_pos] + ULTRASONIC_COMMENT + s[marker_pos:]
start = s.index(marker) + len(marker)
end = s.index(";\n  // Color audit:", start)
base_catalog = json.loads(s[start:end])
if len(base_catalog) != 2307 or any(item["id"] == "gc2372" for item in base_catalog):
    raise SystemExit("Unexpected base catalog")

catalog = []
inserted = False
for item in base_catalog:
    if item["id"] == "gc1236":
        catalog.append(copy.deepcopy(insert_item))
        inserted = True
    catalog.append(item)
if not inserted:
    raise SystemExit("Insertion anchor gc1236 not found")
catalog.extend(copy.deepcopy(append_items))
if len(catalog) != 2345:
    raise SystemExit(f"Unexpected final catalog size: {len(catalog)}")
for item in catalog:
    for key, value in DEFAULTS.items():
        if key in item and item[key] == value:
            del item[key]
compact = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
s = s[:start] + compact + NORMALIZER + s[end + 1:]
PATH.write_text(s, encoding="utf-8")
final_sha = hashlib.sha256(PATH.read_bytes()).hexdigest()
if final_sha != EXPECTED_FINAL_SHA256:
    raise SystemExit(f"Final SHA mismatch: {final_sha}")
print(f"Verified v548 SHA-256: {final_sha}")
