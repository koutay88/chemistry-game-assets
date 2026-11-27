# Chat mode operation for World Chemistry Collection

## Development only

Editable candidates are committed to the `development` branch of `koutay88/chemistry-game-assets`. A green `Validate and publish development data` run promotes the exact checked snapshot to `verified-development`. The game client reads the release pointer and then fetches `game-config.json`, `chapter-master.json`, and `manifest.json` by the immutable commit SHA in that pointer. The client caches the last valid bundle; a failed or invalid request leaves the cached or bundled version in use.

The public game's source branch and the asset repository's `main` branch are separate. Do not edit either for a development change. Public release requires a separate, explicit request and review.

## Which file to edit

- `game-config.json`: supported UI rules/text, facility unlock levels, collection material display/availability overrides, route and experiment text/conditions, reaction entries, study explanations, chapter-one event dialogue, and rare material success probability.
- `chapter-master.json`: the 30 level thresholds/caps and all 118 elements' chapter, release level, raw material, collection facility, and research class.
- `manifest.json`: maps stable material IDs, mission IDs, and experiment IDs to image files.
- Image files: add a new version under `materials/<slug>/vNNN.webp` (or the corresponding `mission-materials/` or `experiments/` directory); do not overwrite an existing version.

For a new image, first add the binary file to the `development` branch, then add or change its stable ID in `manifest.json` in the same candidate commit. Use PNG or WebP, with the manifest path format checked by CI. Preserve existing IDs and leave unrelated mappings untouched.

## Chat mode request template

> In `koutay88/chemistry-game-assets`, edit only the `development` branch. Change `<file/path>` as follows: `<precise change>`. Keep game rules and save schema unchanged. Run the development validation workflow and report the commit and Actions result. Do not edit `main` or the public game.

For an image:

> Add the attached image as `materials/<slug>/vNNN.webp`, map ID `<stable-id>` to that path in `manifest.json`, and commit both changes together to `development`. Do not replace other mappings. Run validation and wait for the green result.

## Applying and checking

After the one-time runtime bootstrap is reflected to the private Sites development app, a successful Actions run updates data without a Sites redeploy. Refresh the development game after the action succeeds. The runtime bundle is version-pinned and cached per browser.

## Rollback

On GitHub, open the bad candidate commit on `development` and use **Revert** to create a new revert commit on `development`. The same validator runs. If it passes, the reverted data is promoted as a new verified snapshot. Do not force-push or edit `verified-development` directly.

## Checks and limits

The workflow checks manifest paths/files, JSON schema, all 118 element IDs, 30 level rows, chapter totals and ranges, unlock caps, facility availability, material and route references, reaction balance where formula data exists, UI allowlists, and content lengths. Invalid candidates do not move the verified pointer. `game-index.json` is generated from the game's data; refresh it when a source-code change adds or removes IDs.

The current runtime bootstrap supports data/config edits described above. Changes to game algorithms, screen structure, save format, or any data category not exposed in `game-config.json` still require a reviewed game-source change and a Sites development update. Never include credentials in repository files.
