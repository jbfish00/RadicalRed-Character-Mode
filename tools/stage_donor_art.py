#!/usr/bin/env python3
"""Stage harvested sprite art into every Character Mode repo's donors tree.

Takes the verified PNGs sitting in a harvest directory, runs them through
`png_to_gba.py`, and writes the result into each repo under

    sprites/donors/<source>/
        <name>.png          the original art, for eyeballing and for ROWE's build
        <name>.4bpp         raw 4bpp tiles
        <name>.gbapal       16-colour BGR555 palette
        <name>.4bpp.lz      LZ77 (BIOS type 0x10) -- what the injector places
        <name>.gbapal.lz    LZ77 palette
        manifest.json       per-file sizes, dimensions, kind, source path
        CREDITS.txt         source URL, commit/retrieval, licence wording

Why a donors directory rather than the live graphics tree: the four binary
hacks have no build step, so art only becomes real when the injector places a
blob. ROWE does compile, and keeps .png/.4bpp/.4bpp.lz side by side already --
but dropping unreferenced files into its `graphics/trainers/front_pics/` would
pollute a tree the Makefile scans. Staging uniformly keeps all five repos
looking the same and touches nothing the build reads.

Prism is deliberately NOT a target: it is a Game Boy Color hack (2bpp, GBC
palettes) and none of this GBA 4bpp art applies.

    python3 tools/stage_donor_art.py --harvest DIR --source rogue [--dry-run]
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parents[1]
ROWE = Path("/home/jbfish00/Documents/Pokemon Rowe Alteration")

TARGETS = [
    WS / "RadicalRed-Character-Mode",
    WS / "Seaglass-Character-Mode",
    WS / "Lazarus-Character-Mode",
    WS / "Unbound-Character-Mode",
    ROWE,
]


def convert(harvest: Path, workdir: Path):
    """Run png_to_gba.py over the harvest and return its manifest."""
    workdir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(HERE / "png_to_gba.py"),
           "--scan", str(harvest), "--outdir", str(workdir)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        sys.exit(f"png_to_gba failed:\n{r.stderr}")
    return json.loads((workdir / "convert_manifest.json").read_text())


def stage(workdir: Path, harvest: Path, source: str, manifest, credits_text, dry):
    ok = [m for m in manifest if m.get("ok")]
    entries = {}
    for m in ok:
        entries[m["name"]] = {
            "kind": m["kind"], "width": m["width"], "height": m["height"],
            "colours": m["colours"],
            "gfx_raw_bytes": m["gfx_raw_bytes"], "gfx_lz_bytes": m["gfx_lz_bytes"],
            "pal_raw_bytes": m["pal_raw_bytes"], "pal_lz_bytes": m["pal_lz_bytes"],
            "source_path": str(Path(m["src"]).relative_to(harvest)),
        }
    doc = {
        "source": source,
        "format": ("GBA 4bpp tiles + 16-colour BGR555 palette, plus LZ77 "
                   "(BIOS type 0x10) streams of each. gfx is 64*64/2 = 2048 B "
                   "for a front pic -- the exact size gTrainerFrontPicTable and "
                   "CFRU's MugshotTable.size declare."),
        "converted_by": "tools/png_to_gba.py (round-trip verified per file)",
        "count": len(entries),
        "entries": entries,
    }
    for repo in TARGETS:
        if not repo.exists():
            print(f"  !! missing repo {repo}")
            continue
        dest = repo / "sprites" / "donors" / source
        print(f"  {'would stage' if dry else 'staging'} {len(ok)} sprites -> "
              f"{dest.relative_to(repo.parent)}")
        if dry:
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for m in ok:
            stem = m["name"]
            for ext in (".4bpp", ".gbapal", ".4bpp.lz", ".gbapal.lz"):
                shutil.copy2(workdir / f"{stem}{ext}", dest / f"{stem}{ext}")
            shutil.copy2(Path(m["src"]), dest / f"{stem}.png")
        (dest / "manifest.json").write_text(json.dumps(doc, indent=1))
        (dest / "CREDITS.txt").write_text(credits_text)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harvest", type=Path, required=True)
    ap.add_argument("--source", required=True, help="donor directory name, e.g. rogue")
    ap.add_argument("--credits", type=Path,
                    help="CREDITS.txt from the harvest (defaults to <harvest>/CREDITS.txt)")
    ap.add_argument("--workdir", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    harvest = args.harvest.resolve()
    if not harvest.is_dir():
        sys.exit(f"no such harvest directory: {harvest}")
    credits_path = args.credits or (harvest / "CREDITS.txt")
    credits_text = (credits_path.read_text() if credits_path.is_file()
                    else f"Source: {args.source}\n(no CREDITS.txt found in harvest)\n")

    workdir = args.workdir or (harvest.parent / f"_converted_{args.source}")
    manifest = convert(harvest, workdir)
    stage(workdir, harvest, args.source, manifest, credits_text, args.dry_run)

    ok = sum(1 for m in manifest if m.get("ok"))
    print(f"\n{ok}/{len(manifest)} sprites staged as '{args.source}' "
          f"into {len(TARGETS)} repos" + (" (dry run)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
