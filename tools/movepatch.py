"""Move-table "best version" patcher (cheap tier: power / accuracy / PP / secondary chance / priority / type; medium tier
2026-11-23: the whole flags byte and the target in the g3 / cfru / gen4 layouts, from medium/MEDIUM_MANIFEST.json).

Source of the edits: game_plans/move_ability_best_2026-11-22/APPLY_MANIFEST.json (user rulings 2026-11-22/23: raise every
move to its best value in every hack). Each hack repo keeps its own slice as tools/character_mode/move_changes.json so the
build doesn't depend on the unversioned workspace folder; this file is copied into each kit/repo next to its build script.

apply(rom, slice, table_off, layout, **geom) -> report.  Every edit asserts the value it replaces equals the manifest's
"from" value, so a wrong table address or a stale manifest fails the build instead of writing garbage.
Rows the layout can't express as data are skipped and reported (deferred), never written:
  - accuracy -> never-miss (101) in engines where never-miss is the move's EFFECT (Gen III vanilla: accuracy 0 always misses,
    pokeemerald Cmd_accuracycheck; checked 2026-11-23). Those are the medium tier.
  - a type the engine doesn't have (e.g. Fairy in a 17-type engine).
Layout "exp" (pokeemerald-expansion MoveInfo) needs geom: stride, pri=(byte, high_nibble), effptr=offset of the
additionalEffects pointer, neff=(byte, bit) of numAdditionalEffects (bit differs per expansion version), alloc=(rom address, capacity) for new effect arrays. A secondary-chance edit never writes into
an existing array (the compiler shares identical arrays between moves): the move is repointed at an existing array that
already holds the new bytes, else at a new array in the alloc block.
"""
import struct

GBA = 0x08000000
# byte layouts: field -> (offset, struct fmt)
LAYOUTS = {
    # Gen III BattleMove (vanilla FR/EM/RS): effect, power, type, acc, pp, chance, target, priority s8, flags, pad x3
    "g3": dict(stride=12, fields={"power": (1, "B"), "type": (2, "B"), "accuracy": (3, "B"), "pp": (4, "B"),
                                  "chance": (5, "B"), "priority": (7, "b"),
                                  "target": (6, "B"), "flags": (8, "B")}, never=None),
    # CFRU (Radical Red, Unbound): same record; accuracy 0 = always hits (CFRU src/accuracy_calc.c AccuracyCalcHelper)
    "cfru": dict(stride=12, fields={"power": (1, "B"), "type": (2, "B"), "accuracy": (3, "B"), "pp": (4, "B"),
                                    "chance": (5, "B"), "priority": (7, "b"),
                                    "target": (6, "B"), "flags": (8, "B")}, never=0),
    # R.O.W.E. 2.1.9.1, 56-byte record: effect u16, power, type, acc, pp, chance, target, priority s8, ...
    # accuracy 0 = always hits (Aerial Ace is acc 0 with the plain-hit effect; old ROWE source AccuracyCalcHelper)
    "rowe": dict(stride=56, fields={"power": (2, "B"), "type": (3, "B"), "accuracy": (4, "B"), "pp": (5, "B"),
                                    "chance": (6, "B"), "priority": (8, "b")}, never=0),
    # Gen IV 16-byte move record (Platinum pl_waza_tbl, HGSS a/0/1/1, hg-engine): effect u16, category, power, type, acc,
    # pp, chance, target u16, priority s8, flags, contest x2, pad. accuracy 0 = can't miss (pokeheartgold
    # BattleSystem_CheckMoveHit and hg-engine other_battle_calculators.c both return before the miss flag).
    "gen4": dict(stride=16, fields={"power": (3, "B"), "type": (4, "B"), "accuracy": (5, "B"), "pp": (6, "B"),
                                    "chance": (7, "B"), "priority": (10, "b"),
                                    "target": (8, "<H"), "flags": (11, "B")}, never=0),
    # Origin HG extra/new_move_data.narc, 40 bytes: type, ?, category, power, acc (101 = never misses), pp, priority s8, ...,
    # status chance +10, flinch +15, stat changes: stat ids +21..23, chances +27..29 (intake/originhg_upstream_docs romdata.py)
    "origin40": dict(stride=40, fields={"power": (3, "B"), "type": (0, "B"), "accuracy": (4, "B"), "pp": (5, "B"),
                                        "priority": (6, "b"), "chance": "multi"}, never=101,
                     chance_slots=dict(status=[10], flinch=15, stats=[(21, 27), (22, 28), (23, 29)])),
    # Gen V a/0/2/1, 36 bytes: type, effect category, category, power, acc (101 = never misses), pp, priority s8, hits,
    # condition u16 +8, status chance +10, flinch +15, effect u16 +16, stat ids +21..23, stages +24..26, chances +27..29
    # (read off the records 2026-11-23: Bite flinch 0x1E at +15, Steel Wing Def/+1/10% at +21/+24/+27)
    "gen5": dict(stride=36, fields={"power": (3, "B"), "type": (0, "B"), "accuracy": (4, "B"), "pp": (5, "B"),
                                    "priority": (6, "b"), "chance": "multi"}, never=101,
                 chance_slots=dict(status=[10], flinch=15, stats=[(21, 27), (22, 28), (23, 29)])),
    # Elite Redux 24-byte BattleMove: u32 flags, effect u16 +4, target, argument, ..., power +10, type +11, type2 +12,
    # acc +13, pp +14, chance +15, priority s8 +16, split +17. accuracy 0 = hits (battle_script_commands.c: moveAcc == 0 ->
    # ACCURACY_HITS_IF_POSSIBLE). Only the primary type is edited.
    "er": dict(stride=24, fields={"power": (10, "B"), "type": (11, "B"), "accuracy": (13, "B"), "pp": (14, "B"),
                                  "chance": (15, "B"), "priority": (16, "b")}, never=0),
    # pokecrystal / Prism, 7 bytes: anim, effect, power, type, acc (percent in Prism), pp, chance (percent). Never-miss and
    # priority are the move's EFFECT here (deferred / not a field).
    # The type byte's top 2 bits are the category (Prism's split: Swords Dance 0x81 = status | Fighting): mask 0x3F.
    "gbc7": dict(stride=7, fields={"power": (2, "B"), "type": (3, "B", 0x3F), "accuracy": (4, "B"), "pp": (5, "B"),
                                   "chance": (6, "B")}, never=None),
    # Polished Crystal / Crystal Inheritance, 8 bytes: anim, effect, power, type, acc (percent), pp, chance (percent),
    # category. Never-miss is the EFFECT here (Aerial Ace = EFFECT_ALWAYS_HIT, acc 100): deferred. Priority is not in the
    # record (MovePriorities list; the CI tool edits it).
    "gbc8": dict(stride=8, fields={"power": (2, "B"), "type": (3, "B"), "accuracy": (4, "B"), "pp": (5, "B"),
                                   "chance": (6, "B")}, never=None),
    # pokeemerald-expansion MoveInfo: +10 u16 type:5/category:2/power:9, +12 u16 accuracy:7/target:9, +14 pp, priority:4
    # in a nibble found per ROM (geom pri), chance in the additionalEffects arrays (geom effptr). accuracy 0 = always hits
    # (expansion battle_util.c: GetMoveAccuracy(move) == 0 -> effect = TRUE).
    "exp": dict(stride=None, fields={"power": None, "type": None, "accuracy": None, "pp": None, "chance": None,
                                     "priority": None}, never=0),
}


def type_ids(type_map):
    """manifest type_map is {hack type id: type name} by vote; invert, lowest id wins (vanilla '???' id 9 votes Normal)."""
    inv = {}
    for k, v in sorted(type_map.items(), key=lambda kv: int(kv[0])):
        inv.setdefault(v, int(k))
    return inv


def plan(slice_, layout):
    """Split the slice's changes into (to_apply, deferred, type ids, never-miss encoding)."""
    L = LAYOUTS[layout]
    never = L["never"]
    tids = type_ids(slice_["type_map"])
    apply_, deferred = [], []
    for c in slice_["changes"]:
        f = c["field"]
        if f not in L["fields"]:
            deferred.append(dict(c, reason="field not in layout")); continue
        if f == "accuracy" and c["to"] == 101 and never is None:
            deferred.append(dict(c, reason="never-miss is effect-bound here (medium tier)")); continue
        if f == "type" and c["to"] not in tids:
            deferred.append(dict(c, reason="engine has no %s type" % c["to"])); continue
        apply_.append(c)
    return apply_, deferred, tids, never


def enc(c, tids, never, which):
    v = c[which]
    if c["field"] == "type":
        return tids[v]
    if c["field"] == "accuracy" and v == 101:
        return never
    return v


def _stride(layout, geom):
    return LAYOUTS[layout]["stride"] or geom["stride"]


def _bits(rom, o, lo, n):
    return (struct.unpack_from("<H", rom, o)[0] >> lo) & ((1 << n) - 1)


def _putbits(rom, o, lo, n, v):
    w = struct.unpack_from("<H", rom, o)[0]
    assert 0 <= v < (1 << n), "value %r does not fit %d bits" % (v, n)
    struct.pack_into("<H", rom, o, (w & ~(((1 << n) - 1) << lo)) | (v << lo))


def _eff(rom, r, geom):
    """(array file offset, count, index of the edited effect) for an expansion record at file offset r, or None."""
    p = struct.unpack_from("<I", rom, r + geom["effptr"])[0]
    if not GBA <= p < GBA + len(rom):
        return None
    a = p - GBA
    b, bit = geom["neff"]          # numAdditionalEffects:2 (arrays sit back to back, so the record's count is the only bound)
    n = (struct.unpack_from("<I", rom, r + b)[0] >> bit) & 3
    # the edited effect: the first non-self one with a chance (Fangs: the status, not the flinch that follows)
    idx = next((k for k in range(n) if not rom[a + 4 * k + 2] & 1 and rom[a + 4 * k + 3]), None)
    return a, n, idx


def _slots(layout, rom, r):
    """Chance byte offsets in use: status, flinch, and each stat change that names a stat."""
    cs = LAYOUTS[layout]["chance_slots"]
    return cs["status"] + [cs["flinch"]] + [c for st, c in cs["stats"] if rom[r + st]]


def _chance_targets(layout, rom, r):
    """Which chance bytes a raise edits: the non-flinch slots holding the current max (Fangs: the status, not the
    flinch; ruling Q3 2026-11-23), or the flinch alone when it is the move's only chance."""
    cs = LAYOUTS[layout]["chance_slots"]
    cur = max([rom[r + o] for o in _slots(layout, rom, r)] or [0])
    t = [o for o in cs["status"] + [c for st, c in cs["stats"] if rom[r + st]] if rom[r + o] == cur and cur]
    return t or ([cs["flinch"]] if rom[r + cs["flinch"]] == cur and cur else [])


def get(rom, layout, table_off, mid, field, geom):
    r = table_off + _stride(layout, geom) * mid
    if layout != "exp":
        if LAYOUTS[layout]["fields"][field] == "multi":
            ch = [rom[r + o] for o in _slots(layout, rom, r)]
            ch = [c for c in ch if c]
            return max(ch) if ch else None
        off, fmt = LAYOUTS[layout]["fields"][field][:2]
        v = struct.unpack_from(fmt, rom, r + off)[0]
        return v & LAYOUTS[layout]["fields"][field][2] if len(LAYOUTS[layout]["fields"][field]) > 2 else v
    if field == "power":
        return _bits(rom, r + 10, 7, 9)
    if field == "type":
        return _bits(rom, r + 10, 0, 5)
    if field == "accuracy":
        return _bits(rom, r + 12, 0, 7)
    if field == "pp":
        return rom[r + 14]
    if field == "priority":
        b, hi = geom["pri"]
        v = (rom[r + b] >> 4) if hi else (rom[r + b] & 15)
        return v - 16 if v > 7 else v
    if field == "chance":
        e = _eff(rom, r, geom)
        return None if e is None or e[2] is None else rom[e[0] + 4 * e[2] + 3]
    raise KeyError(field)


def put(rom, layout, table_off, mid, field, v, geom, arrays=None):
    r = table_off + _stride(layout, geom) * mid
    if layout != "exp":
        if LAYOUTS[layout]["fields"][field] == "multi":
            for o in _chance_targets(layout, rom, r):
                rom[r + o] = v
            return
        spec = LAYOUTS[layout]["fields"][field]
        off, fmt = spec[:2]
        if len(spec) > 2:
            assert v & ~spec[2] == 0, "value %r does not fit mask %#x" % (v, spec[2])
            v |= rom[r + off] & ~spec[2] & 0xFF
        struct.pack_into(fmt, rom, r + off, v)
    elif field == "power":
        _putbits(rom, r + 10, 7, 9, v)
    elif field == "type":
        _putbits(rom, r + 10, 0, 5, v)
    elif field == "accuracy":
        _putbits(rom, r + 12, 0, 7, v)
    elif field == "pp":
        rom[r + 14] = v
    elif field == "priority":
        b, hi = geom["pri"]
        assert -8 <= v <= 7
        n = v & 15
        rom[r + b] = ((rom[r + b] & 0x0F) | (n << 4)) if hi else ((rom[r + b] & 0xF0) | n)
    elif field == "chance":
        a, n, idx = _eff(rom, r, geom)
        new = bytearray(rom[a:a + 4 * n])
        new[4 * idx + 3] = v
        struct.pack_into("<I", rom, r + geom["effptr"], arrays(bytes(new)))
    else:
        raise KeyError(field)


def _array_pool(rom, table_off, n_moves, geom):
    """Repoint target for a new additionalEffects array: an existing array some move already points at with the same
    bytes, else a new one in geom['alloc'] (deduplicated). Returns (lookup fn, state with the new arrays)."""
    S = geom["stride"]
    known = set()
    for i in range(1, n_moves + 1):
        p = struct.unpack_from("<I", rom, table_off + S * i + geom["effptr"])[0]
        if GBA <= p < GBA + len(rom):
            known.add(p)
    start, cap = geom["alloc"]
    state = dict(next=start, made={})

    def lookup(b):
        for p in sorted(known):
            if rom[p - GBA:p - GBA + len(b)] == b:
                return p
        if b in state["made"]:
            return state["made"][b]
        a = state["next"]
        assert a + len(b) <= start + cap, "effect-array block full"
        o = a - GBA
        assert set(rom[o:o + len(b)]) == {0xFF}, "effect-array block %#x not blank" % a
        rom[o:o + len(b)] = b
        state["made"][b] = a
        state["next"] = (a + len(b) + 3) & ~3
        return a
    return lookup, state


def apply(rom, slice_, table_off, layout, **geom):
    todo, deferred, tids, never = plan(slice_, layout)
    n_moves = max(c["hack_move_id"] for c in slice_["changes"])
    arrays, state = _array_pool(rom, table_off, n_moves, geom) if layout == "exp" else (None, {})
    for c in todo:
        cur = get(rom, layout, table_off, c["hack_move_id"], c["field"], geom)
        old, new = enc(c, tids, never, "from"), enc(c, tids, never, "to")
        if c["field"] == "type" and slice_["type_map"].get(str(cur)) == c["from"]:
            old = cur          # a hack-custom type id voted to the same name (Prism's extra types)
        assert cur == old, "move %d %s %s: ROM has %r, manifest says %r (wrong table or stale manifest)" % (
            c["hack_move_id"], c["move"], c["field"], cur, old)
        put(rom, layout, table_off, c["hack_move_id"], c["field"], new, geom, arrays)
        assert get(rom, layout, table_off, c["hack_move_id"], c["field"], geom) == new
    rep = dict(applied=len(todo), deferred=len(deferred),
               deferred_rows=[{k: d[k] for k in ("hack_move_id", "move", "field", "from", "to", "reason")} for d in deferred])
    if layout == "exp":
        rep["new_effect_arrays"] = {"%#x" % a: b.hex() for b, a in state["made"].items()}
    return rep


def touched_bytes(layout, table_off, mid, field, geom):
    r = table_off + _stride(layout, geom) * mid
    if layout != "exp":
        if LAYOUTS[layout]["fields"][field] == "multi":
            cs = LAYOUTS[layout]["chance_slots"]
            return [r + o for o in cs["status"] + [cs["flinch"]] + [c for _, c in cs["stats"]]]
        off, fmt = LAYOUTS[layout]["fields"][field][:2]
        return range(r + off, r + off + struct.calcsize(fmt))
    pb = geom.get("pri", (0, 0))[0]
    ep = geom.get("effptr", 0)
    return {"power": range(r + 10, r + 12), "type": range(r + 10, r + 12), "accuracy": range(r + 12, r + 14),
            "pp": range(r + 14, r + 15), "priority": range(r + pb, r + pb + 1), "chance": range(r + ep, r + ep + 4)}[field]


def verify(base, built, slice_, table_off, layout, n_moves, **geom):
    """Static check of a built ROM: every applied row reads its new value, every deferred row still reads its old value,
    an edited effect array differs from the base one only in that chance, and no other byte of the move table changed
    (bit-packed fields: the other bits of a touched halfword are checked by reading the neighbouring fields too).
    Returns a list of failures (empty = pass)."""
    S = _stride(layout, geom)
    todo, deferred, tids, never = plan(slice_, layout)
    bad = []
    touched = set()
    edited = {}
    for c, want in [(c, "to") for c in todo] + [(c, "from") for c in deferred if c["field"] in LAYOUTS[layout]["fields"]]:
        if want == "from" and ((c["field"] == "type" and c["from"] not in tids) or (c["field"] == "accuracy" and c["from"] == 101)):
            continue
        exp = enc(c, tids, never, want)
        got = get(built, layout, table_off, c["hack_move_id"], c["field"], geom)
        if c["field"] == "type" and want == "from" and slice_["type_map"].get(str(got)) == c["from"]:
            exp = got
        if got != exp:
            bad.append("move %d %s %s: %r, want %r (%s)" % (c["hack_move_id"], c["move"], c["field"], got, exp, want))
        touched.update(touched_bytes(layout, table_off, c["hack_move_id"], c["field"], geom))
        edited.setdefault(c["hack_move_id"], set()).add(c["field"])
    if layout == "exp":
        for mid, fs in edited.items():
            r = table_off + S * mid
            for f in ("power", "type", "accuracy", "pp", "priority"):     # untouched fields sharing a touched byte
                if f not in fs and get(built, layout, table_off, mid, f, geom) != get(base, layout, table_off, mid, f, geom):
                    bad.append("move %d: %s changed without a manifest row" % (mid, f))
            for o, lo, n, what in ((r + 10, 5, 2, "category"), (r + 12, 7, 9, "target")):
                if _bits(built, o, lo, n) != _bits(base, o, lo, n):
                    bad.append("move %d: %s bits changed" % (mid, what))
            pb, hi = geom["pri"]
            if (built[r + pb] & (0x0F if hi else 0xF0)) != (base[r + pb] & (0x0F if hi else 0xF0)):
                bad.append("move %d: the other nibble of the priority byte changed" % mid)
            if "chance" in fs:
                a0, n0, i0 = _eff(base, r, geom)
                a1, n1, i1 = _eff(built, r, geom)
                b0, b1 = bytearray(base[a0:a0 + 4 * n0]), bytearray(built[a1:a1 + 4 * n1])
                b0[4 * i0 + 3] = 0
                if i1 is not None:
                    b1[4 * i1 + 3] = 0
                if (n0, i0, bytes(b0)) != (n1, i1, bytes(b1)):
                    bad.append("move %d: effect array changed beyond its chance" % mid)
    for o in range(table_off, table_off + S * (n_moves + 1)):
        if o not in touched and base[o] != built[o]:
            bad.append("untouched move-table byte %#x changed %02x -> %02x" % (o, base[o], built[o]))
    return bad
