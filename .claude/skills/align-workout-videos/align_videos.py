#!/usr/bin/env python3
"""Schedule a Spotify playlist's YouTube videos against a workout's intervals.

Usage:
  align_videos.py WORKOUT.json TRACKS.json [--crossfade 10] [--snap 15]
                  [--min-tail 30] [--write [--replace]]

TRACKS.json: [{"name": "...", "videoId": "...", "duration": <seconds>}, ...]
(playlist order; `duration` is the Spotify track length in seconds).

Model: Spotify crossfade makes track n start at sum(duration[k] - crossfade, k<n).
Each video is pinned to the nearest interval boundary within --snap seconds so
drift cannot accumulate; only when no boundary is that close does it fall back to
a mid-interval triggerOffset. Prints a plan table; writes only with --write.
"""
import argparse, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("workout"); ap.add_argument("tracks")
ap.add_argument("--crossfade", type=float, default=10)
ap.add_argument("--snap", type=float, default=15)
ap.add_argument("--min-tail", type=float, default=30,
                help="drop tracks that would start within this many seconds of the end")
ap.add_argument("--write", action="store_true")
ap.add_argument("--replace", action="store_true", help="overwrite an existing videos array")
a = ap.parse_args()

d = json.load(open(a.workout))
ex, t = [], 0  # (expanded id, start, end)
for it in d["sequence"]:
    if it["type"] == "interval":
        ex.append((it["id"], t, t + it["duration"])); t += it["duration"]
    else:
        for r in range(1, it["repetitions"] + 1):
            for x in it["intervals"]:
                ex.append((f"{x['id']}-block-{it['id']}-rep-{r}", t, t + x["duration"])); t += x["duration"]
total = t
if "totalDuration" in d and d["totalDuration"] != total:
    sys.exit(f"totalDuration {d['totalDuration']} != expanded sequence {total}")

tracks = json.load(open(a.tracks))
planned, pos = [], 0.0
for tr in tracks:
    if pos > total - a.min_tail: break
    planned.append((tr, pos)); pos += tr["duration"] - a.crossfade

# trigger point per track: (interval index, offset)
def locate(s):
    i = next(i for i, x in enumerate(ex) if x[1] <= s < x[2])
    nearest = min(range(len(ex) + 1), key=lambda j: abs((ex[j][1] if j < len(ex) else total) - s))
    b = ex[nearest][1] if nearest < len(ex) else total
    if abs(b - s) <= a.snap and nearest < len(ex):
        return nearest, 0, b      # pinned to an interval start
    return i, round(s - ex[i][1]), round(s)  # no boundary close: mid-interval offset

trig = [locate(s) for _, s in planned]
vids, used, rows = [], set(), []
for n, ((tr, s), (ti, toff, actual)) in enumerate(zip(planned, trig)):
    if n + 1 < len(trig):
        ni, noff, _ = trig[n + 1]
        # end where the next video begins: just before its interval, or inside it at its offset
        if noff: ei, eoff = ni, noff
        else: ei, eoff = max(ni - 1, ti), None
    else:
        ei, eoff = len(ex) - 1, None
    base = re.sub(r"[^a-z0-9]+", "-", tr["name"].lower()).strip("-")
    vid_id, k = "video-" + base, 2
    while vid_id in used: vid_id, k = f"video-{base}-{k}", k + 1
    used.add(vid_id)
    v = {"id": vid_id, "name": tr["name"],
         "youtubeUrl": "https://www.youtube.com/watch?v=" + tr["videoId"],
         "startTime": 0, "triggerIntervalId": ex[ti][0]}
    if toff: v["triggerOffset"] = toff
    v["endIntervalId"] = ex[ei][0]
    if eoff: v["endOffset"] = eoff
    vids.append(v)
    rows.append((n + 1, tr["name"], s, actual, "pin" if not toff else f"+{toff}s", ex[ti][0]))

print(f"workout {total}s, crossfade {a.crossfade:g}s, snap {a.snap:g}s, {len(vids)}/{len(tracks)} tracks fit")
print(f"{'#':>2} {'track':<34}{'planned':>8}{'actual':>8}  {'mode':<6} trigger")
for n, name, s, act, mode, tid in rows:
    print(f"{n:>2} {name[:33]:<34}{s:>8.0f}{act:>8}  {mode:<6} {tid}")
print("dropped (no room):", [x["name"] for x in tracks[len(vids):]] or "none")

if a.write:
    txt = open(a.workout).read()
    block = '  "videos": ' + json.dumps(vids, indent=2, ensure_ascii=False).replace("\n", "\n  ") + ",\n"
    m = re.search(r'\n  "videos": \[.*?\n  \],\n(?=  "sequence")', txt, re.S)
    if m:
        if not a.replace: sys.exit("workout already has videos; pass --replace")
        txt = txt[:m.start() + 1] + block + txt[m.end():]
    else:
        if '  "sequence": [' not in txt: sys.exit("could not find top-level sequence")
        txt = txt.replace('  "sequence": [', block + '  "sequence": [', 1)
    json.loads(txt)
    open(a.workout, "w").write(txt)
    print("wrote", a.workout)
