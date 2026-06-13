---
name: import-workout-csv
description: Use when converting a cycling workout from a CSV, pasted spreadsheet table, or a Google Sheets / Google Drive URL into this repo's interval workout JSON schema. Triggers on "import this workout", a pasted CSV of intervals (power zone, cadence, duration columns), or a Google Sheets link to a workout. Not for ride-tracking data.
---

# Import Workout from CSV or Google Sheet

Convert a structured cycling workout (power zones, cadence, durations, optional repeating sets) from a CSV / spreadsheet / Google Sheets URL into the interval workout JSON schema used by this repo and consumed by cyclesync-coach.

## Source Format Detection

| Source | How to read it |
|--------|----------------|
| Pasted CSV / table | Use the text directly |
| Local `.csv` file | `Read` the file |
| **Google Sheets / Drive URL** | **Prefer `download_file_content` with `exportMimeType: "text/csv"`** (it returns base64 — decode it) over `read_file_content`. The natural-language `read_file_content` view **silently drops rows** (e.g. an opening warm-up) and merges cells — do not trust it for the workout table. If you only have the NL view, durations appear as `<span type="duration" hours=.. minutes=.. seconds=..>H:MM:SS</span>` — parse the `H:MM:SS` text inside the span. |

**Cross-check against the Cumulative column.** Most of these sheets carry a `Cumulative` column whose last data row is the true total (e.g. `1:00:00`). After parsing, confirm your summed `totalDuration` equals that final cumulative value. If it's short, you dropped a row — re-read from the CSV export.

**Google Sheets URL → file ID:** `https://docs.google.com/spreadsheets/d/<FILE_ID>/edit?...` — the `<FILE_ID>` is the long token after `/d/`. Also grab the sheet `title` via `get_file_metadata` for naming.

Spreadsheets often contain **a workout table plus unrelated planning columns** (e.g. a Spotify song/timing list, cumulative-time helper columns). Use only the workout table (Name, Power zone, Cadence, Duration). Ignore song lists and cumulative/diff helper columns — call out in your summary that you did.

## Process

### 1. Analyze structure
- Header row contains: Name, Power zone (or Zone), Cadence, Duration, Notes.
- Section-header rows have a Name but no duration (e.g. "Ramps", "Steady TT") — they label the rows beneath them.
- Blank rows are visual separators — skip them.
- Watch for zone-range notation in one cell: `Z2 -> 3 -> 5` or `Z1-Z2`.

### 2. Parse power zones
- **Simple zone** → use directly: `"powerZone": "Z2+"`. Accept `Z1`–`Z7` with optional `+`/`-`, or bare integers `1`–`7`.
- **Zone range** (`Z2 -> 3 -> 5`, `Z1-Z2`) → `"powerZoneRange": { "start": "Z2", "end": "Z5" }` (first zone → last zone). An interval has **either** `powerZone` **or** `powerZoneRange`, never both.

### 3. Parse duration to seconds
- `H:MM:SS` → hours×3600 + minutes×60 + seconds (`0:03:00` = 180, `1:30:00` = 5400).
- `MM:SS` → minutes×60 + seconds.

### 4. Name intervals (priority order)
1. Row's own Name value.
2. Last section header above the row.
3. Notes column if descriptive.
4. Power zone as last resort.

Unnamed recovery rows (a bare `Z1` between efforts) → name them `Recover`.

### 5. Build sequence items
Standalone interval:
```json
{ "type": "interval", "id": "i001", "name": "Warmup", "duration": 180, "powerZone": "Z2" }
```
Add `"cadence": <rpm>` only when the Cadence column has a value (40–150).

### 6. Repeating sets → block (only when truly identical)
If the same interval pattern repeats with **identical** durations/zones (often flagged by a `reps` value > 1), collapse it into a block. If the "repeat" varies (durations shrink, cadence added), keep it as flat intervals — do not force a block.
```json
{
  "type": "block", "id": "wave-intervals", "name": "Wave Intervals", "repetitions": 2,
  "intervals": [
    { "id": "wave-z2", "name": "Wave Z2", "duration": 90, "powerZone": "Z2", "cadence": 80 },
    { "id": "wave-z3", "name": "Wave Z3", "duration": 60, "powerZone": "Z3", "cadence": 90 }
  ]
}
```
**Intervals inside a block have NO `type` field.** Only top-level `sequence` items get `type`.

### 7. Assemble the workout
```json
{
  "id": "workout-name-duration",
  "name": "Workout Name",
  "description": "Brief description of the workout focus",
  "totalDuration": <sum of all interval-seconds, expanding blocks ×repetitions>,
  "sequence": [ /* intervals and blocks in order */ ],
  "isSample": false
}
```
`totalDuration` must equal the real sum, **counting each block's intervals × its repetitions**. It must also match the sheet's final `Cumulative` value (see the cross-check above).

**Naming convention (repo standard):**
- **`name` omits the duration** — `"Strong Style"`, not `"Strong Style (60)"`. Source sheets often title themselves `"... (60)"`; strip the `(NN)` suffix from the display name.
- **`id`** is kebab-case `<workout-name>-<duration-minutes>` (e.g. `strong-style-60`). A leading `YYYY-MM-DD-` date prefix is optional (some newer files use it); the trailing `-<minutes>` is always present.

### 8. Choose file location
Round total minutes to the nearest category — 30, 45, 50, 60, 90 — and save kebab-case:
`workouts/<duration>min/<workout-name>.json`

### 9. Validate (required)
```bash
python3 utils/validate_workout.py workouts/<duration>min/<filename>.json
```
Fix every error before reporting success.

## Validation Checklist
- ✓ Every top-level `sequence` item has `type` (`interval` or `block`).
- ✓ Intervals **inside blocks** have **no** `type` field.
- ✓ Each interval has `id`, `name`, `duration`, and exactly one of `powerZone` / `powerZoneRange`.
- ✓ Field is `powerZone`, not `zone`.
- ✓ Power zones are 1–7 / Z1–Z7 with optional `+`/`-`.
- ✓ Cadence (if present) is 40–150.
- ✓ All IDs unique, none missing.
- ✓ `totalDuration` equals the expanded sum.

## Common Mistakes
| Mistake | Fix |
|---------|-----|
| `zone` instead of `powerZone` | Rename the field. |
| Missing `type` on standalone interval | Add `"type": "interval"`. |
| Added `type` to a block's child interval | Remove it — only top-level items get `type`. |
| Forced a block on a non-identical repeat | Keep it flat when durations/cadence differ. |
| `totalDuration` ignores repetitions | Multiply block intervals by `repetitions`. |
| Imported the song/cumulative columns | Use only the workout table; note what you ignored. |

## Output
Report: `✓ Imported '<name>' — X intervals, Y min total → workouts/<duration>min/<file>.json (validator passed)`. Note any columns/rows you ignored and any zone-range or block interpretations you made.

## Optional: Add Videos After Import
To sync YouTube/Vimeo playback with intervals, see [VIDEOS.md](../../VIDEOS.md) (block expansion + timing rules) and the `create-interval-workout` skill's video step.
