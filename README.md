# chemistry-game-assets

Public image repository for **collection specimen illustrations** used by World Chemistry Collection. Experiment illustrations are kept out until explicitly approved.

## Register an image

1. Add an optimized PNG or WebP under `materials/<slug>/v001.webp`.
2. Update `manifest.json` with the game's material ID as the key and that relative path as the value.
3. Keep file names lowercase ASCII with hyphens. The manifest supports only `materials/<slug>/v<number>.(webp|png)`.
4. Commit the file and manifest to `main`.

The development game reads the public manifest from this repository when opened. The development deployment is private; only this repository's images and manifest are public.

## Current mapping

- `S` — natural sulfur specimen, `materials/natural-sulfur/v001.webp`
- `Cu` — copper collection entry, illustrated with the malachite ore sample, `materials/malachite/v001.webp`
