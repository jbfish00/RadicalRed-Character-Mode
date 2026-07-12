# Provenance

`data.js` is the species database snapshot from the community Radical Red Pokedex:

- Live site: https://dex.radicalred.net/
- Source repo: https://github.com/JwowSquared/Radical-Red-Pokedex
- Snapshot date: ~2025-06-30 (Radical Red v4.1-era, matches this project's target ROM version)

Format: a Python-literal-parseable (`ast.literal_eval`) dict: `{'species': {id: {name, key, stats, type, abilities, evolutions, ancestor, ...}, ...}, 'moves': {...}, ...}`. `ancestor` is a precomputed evolution-family base-stage species id — exactly the "roster stores base-stage species only" semantics this project's Character Mode needs (see `../map_species.py`).

Cross-validated byte-exact against this project's own ROM extraction (`docs/ROUTINE_MAP.md`, base-stats table at file offset `0x17B98EC`) for all 82 species in the originally-suspected "Gen 9 range" (indices 1294-1375) before being adopted as the primary species-ID/name source for the whole roster pipeline.

Not redistributed as a standalone product — used internally by this project's own tooling (`map_species.py`) to resolve Bulbapedia-scraped character rosters to real in-ROM species ids. If distributing this project's patch/tooling publicly, credit JwowSquared's Radical Red Pokedex project for this data.
