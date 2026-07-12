# Free space audit

Run against `rom/radicalred 4.1.gba` (SHA1 `964f951a0fdaf209e4ea1344883ef0d557bb3a80`) via `tools/scan_free_space.py`.

## 0xFF-padded runs (trustworthy signal — standard GBA linker padding)

- 77 runs >= 0x400 bytes.
- **Total: 5,659,422 bytes (5.40 MiB) free.**
- Top blocks (primary injection targets):

| ROM offset | Length | Length (hex) |
|---|---|---|
| 0x00B71D04 | 1,632,211 | 0x18E7D3 |
| 0x0085032B | 1,047,765 | 0xFFCD5 |
| 0x00951E14 | 713,196 | 0xAE1EC |
| 0x007568A0 | 694,112 | 0xA9760 |
| 0x01351620 | 453,088 | 0x6E9E0 |
| 0x0080A210 | 286,192 | 0x45DF0 |
| 0x00FBAF9C | 279,588 | 0x44424 |
| 0x01FC6548 | 236,216 | 0x39AB8 |

(remaining 69 runs are smaller, see raw scan output — re-run `python3 tools/scan_free_space.py "rom/radicalred 4.1.gba" --byte 0xFF --min 0x400 --top 100` for the full table)

## 0x00-padded runs (weaker signal — zeroed data can be legitimate empty table slots, not just padding)

- 56 runs >= 0x400 bytes, total 227,983 bytes (0.22 MiB). Not counted toward the trustworthy free-space total; individual runs would need verification before use.

## Conclusion

**Free space is not a bottleneck for this project.** 5.40 MiB of confirmed 0xFF-padding free space is over 3.5x what Unbound-Character-Mode had (~1.46 MiB), despite Radical Red having considerably denser game content (full Gen 1-9 species/moves, Mega Evolution, Z-Moves, Dynamax/Gigantamax, physical-special split). The two largest blocks alone (0x00B71D04, 1.63 MiB and 0x0085032B, ~1.02 MiB) comfortably exceed all of Unbound's combined free space and are the primary candidates for the roster data tables and injected enforcement code once Phase 1's hook-site RE is further along.

This resolves the plan's open risk #1 ("free space unmeasured for Radical Red — could be tighter than Unbound's") favorably.
