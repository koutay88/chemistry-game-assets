# World Chemistry Collection assets

This repository stores replaceable illustration files. The game mechanics and save data are not stored here.

## Branches

- `main`: public/released asset manifest. Only updated when the owner explicitly asks to update the public game.
- `development`: development-only manifest and art. The private development game reads this branch.

## Manifest schema

`manifest.json` supports:
- `materials`: element/material ID to specimen illustration (for example `Cu`, `S`)
- `missionMaterials`: mission-only specimen names (for example `copperOre`, `sulfurCrystal`)
- `experiments`: illustration keys used in mission scenes

Store optimized WebP/PNG under the corresponding `materials/`, `mission-materials/`, or `experiments/` path. Keep IDs and existing save data unchanged. Use a new version suffix for replacements; update only the development manifest until public release is explicitly requested.

## Development workflow

1. Add WebP image files in the matching directory on `development`.
2. Update `manifest.json` on `development` with the stable illustration key and relative path.
3. Confirm the private development game loads the image.
4. Never merge `development` into `main` or edit the public manifest unless the owner explicitly instructs it.

## Current development mappings

| Kind | ID/key | Path | Illustration |
|---|---|---|---|
| Material | S | materials/natural-sulfur/v001.webp | Natural sulfur (existing) |
| Material | Cu | materials/copper/v001.webp | Extracted copper |
| Mission material | copperOre | mission-materials/copper-ore/v001.webp | Malachite ore |
| Mission material | sulfurCrystal | mission-materials/sulfur/v001.webp | Sulfur crystals |
| Experiment | copperPowder | experiments/copper/powder-v001.webp | Ground malachite |
| Experiment | copperOxide | experiments/copper/oxide-v001.webp | Heated ore / black oxide |
| Experiment | copperExtraction | experiments/copper/extraction-v001.webp | Copper extraction |
| Experiment | saltWaterElectrolysis | experiments/chlorine/salt-water-electrolysis-v001.webp | Brine electrolysis |
| Experiment | sulfurCrystalAnalysis | experiments/sulfur/crystal-analysis-v001.webp | Sulfur lab illustration |
