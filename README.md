# World Chemistry Collection assets

This repository stores replaceable illustration files. The game mechanics and save data are not stored here. This repository is public, so files committed here are publicly accessible.

## Branches

- `main`: public/released asset manifest. Only updated when the owner explicitly asks to update the public game.
- `development`: development-only manifest and art. The private development game reads this branch.

## Manifest schema

`manifest.json` supports:
- `materials`: element/material ID to specimen illustration (for example `Cu`, `S`)
- `missionMaterials`: mission-only specimen names (for example `copperOre`, `sulfurCrystal`)
- `experiments`: illustration keys used in mission scenes

Store optimized WebP/PNG under the corresponding `materials/`, `mission-materials/`, or `experiments/` path. Keep IDs and existing save data unchanged. Use a new version suffix for replacements; update only the development manifest until public release is explicitly requested.

## Chat mode batch workflow

1. Save Chat-generated PNG originals and optimized WebP files to the private Google Drive materials folder.
2. For each image, provide its Drive file URL, stable game ID/key, category, and new GitHub path.
3. Read the current `development/manifest.json` and latest development commit. Fetch each WebP from Drive as raw bytes/base64.
4. Create one Git blob per image, merge all new ID/path entries into the existing manifest, then create one manifest blob.
5. Create a single tree based on the latest development tree with every new image and `manifest.json`; create one commit with the previous development head as parent.
6. Update the `development` ref using `expected_sha` and `force=false`. If the head changed, reread and retry; do not force-push.
7. Confirm the `Validate development illustrations` Actions run passes and reload the development game.

This batches multiple images and all manifest mappings into one atomic development commit. It does not edit `main` or deploy the game source. The development game reads its asset manifest when opened/reloaded.

## Current development mappings

| Kind | ID/key | Path | Illustration |
|---|---|---|---|
| Material | S | materials/natural-sulfur/v001.webp | Natural sulfur (existing) |
| Material | Cu | materials/copper/v001.webp | Extracted copper |
| Material | sample-master-012 | materials/amethyst/v001.webp | Amethyst quartz specimen |
| Mission material | copperOre | mission-materials/copper-ore/v001.webp | Malachite ore |
| Mission material | sulfurCrystal | mission-materials/sulfur/v001.webp | Sulfur crystals |
| Experiment | copperPowder | experiments/copper/powder-v001.webp | Ground malachite |
| Experiment | copperOxide | experiments/copper/oxide-v001.webp | Heated ore / black oxide |
| Experiment | copperExtraction | experiments/copper/extraction-v001.webp | Copper extraction |
| Experiment | saltWaterElectrolysis | experiments/chlorine/salt-water-electrolysis-v001.webp | Brine electrolysis |
| Experiment | sulfurCrystalAnalysis | experiments/sulfur/crystal-analysis-v001.webp | Sulfur lab illustration |


## Chat mode data workflow

See [`docs/CHAT-MODE.md`](docs/CHAT-MODE.md) for the edit, image registration, validation, verified publication, and rollback procedure. Development edits go to `development`; only a successful Actions validation advances the immutable snapshot pointer on `verified-development`. The game client must read that pointer and fetch files by its pinned commit SHA. Do not edit `main` for development changes.
