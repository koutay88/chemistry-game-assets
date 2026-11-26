# World Chemistry Collection assets

This repository stores replaceable illustration files for the game. The game mechanics and save data are not stored here.

## Branches

- `main`: public/released asset manifest. Changes here can affect the public game; update only when the owner explicitly asks for a public release.
- `development`: development-only asset manifest used by the private development game.

## Registering images

Use the `development` branch for routine illustration additions and replacements. Add an optimized WebP/PNG under one of:

- `materials/<slug>/v001.webp`
- `mission-materials/<slug>/v001.webp`
- `experiments/<category>/<name>-v001.webp`

Then add or update a stable ID/key in the matching `materials`, `missionMaterials`, or `experiments` map in that branch's `manifest.json`. Keep the public `main` branch unchanged unless the owner explicitly requests a public update.

See the private Google Drive folder `世界化学コレクション素材/05_素材管理` for the Chat-mode procedure and full ID mapping.
