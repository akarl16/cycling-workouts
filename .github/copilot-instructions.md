# Copilot Instructions for cycling-workouts

This repository contains structured interval workout templates for cycling training.

## Interval Workout Format
**Location**: `workouts/` directory organized by duration (30min/, 45min/, 50min/, 60min/, 90min/)
**Schema**: `schema/workout-schema.json`
**Purpose**: Structured workout templates with power zones and intervals for training

### Key Fields:
- `id`: Unique identifier (kebab-case)
- `name`: Display name
- `description`: Optional description
- `totalDuration`: Total seconds
- `sequence`: Array of intervals and blocks
- `theme`: Optional theme (default, halloween, christmas, etc.)

### Power Zones:
- Can be integers (1-7) or strings ("Z1", "Z2+", "Z3-", etc.)
- Use `powerZone` for single zone or `powerZoneRange` for gradual progression
- Example range: `{"start": "Z2", "end": "Z5"}`

### Intervals:
```json
{
  "type": "interval",
  "id": "i001",
  "name": "Warmup",
  "duration": 180,
  "powerZone": "Z2",
  "cadence": 90  // Optional
}
```

### Blocks (Repeating):
```json
{
  "type": "block",
  "id": "b001",
  "name": "Main Set",
  "repetitions": 3,
  "intervals": [
    { "id": "work", "name": "Work", "duration": 120, "powerZone": "Z4" },
    { "id": "rest", "name": "Rest", "duration": 60, "powerZone": "Z2" }
  ]
}
```

### Validation:
Use `python3 utils/validate_workout.py workouts/**/*.json` to validate workouts.

## CSV Import Guidelines

### CSV Format

The standard workout CSV has these columns (only the first 5 are used):

```
Name, Power zone, Cadence, Duration, Notes, Cumulative, (ignored columns...)
```

- **Name**: Section name — only appears on the **first row** of a section; subsequent rows in the same section have an empty Name cell
- **Power zone**: e.g. `Z1`, `Z3+`, `Z4-`, `Z5`
- **Cadence**: Optional RPM integer
- **Duration**: `H:MM:SS` format (e.g. `0:00:20`, `0:03:00`, `1:00:00`)
- **Notes**: Optional coaching cue (e.g. "Out of the saddle", "Cadence up") — map to the `notes` field on the interval

**Blank rows** (all five key columns empty) are separators — skip them entirely.

### Step-by-Step Import Process

#### 1. Parse sections
Scan the CSV top to bottom. Carry the last non-empty Name forward as the current section label. When you hit a blank row, the section ends. Build an ordered list of sections, each containing its rows:

```
Warmup         → [Z1/180s, Z2/180s, Z3/120s, Z2@95/60s]
Tabata warm-up → [Z3+@95/20s, Z1/10s, Z3+@95/20s, Z1/10s, ...]
Recover        → [Z1/120s]
Breakaway      → [Z6/15s, Z5/30s, Z4-/135s, Z2/60s]
Breakaway      → [Z6/15s, Z5/30s, Z4-/135s, Z2/60s]
...
```

#### 2. Detect repeating blocks
After parsing, scan for **consecutive sections with the same name AND identical interval structure** (same sequence of powerZone + duration + cadence). These become a single `block` with `repetitions` = count. Non-consecutive repetitions or sections with different internal intervals are kept as separate entries.

Example: Two back-to-back `Breakaway` sections with the same 4 intervals → one block with `"repetitions": 2`.

#### 3. Parse duration to seconds
- `H:MM:SS` → `hours*3600 + minutes*60 + seconds`
- `0:00:20` → 20, `0:03:00` → 180, `0:02:15` → 135

#### 4. Parse power zones
- Use as-is: `"Z1"`, `"Z3+"`, `"Z4-"`, `"Z5"`
- Ramp ranges (e.g. `"Z2 -> Z5"`): use `"powerZoneRange": {"start": "Z2", "end": "Z5"}`

#### 5. Build interval names
- Single-interval section: use the section name directly (e.g. `"Recover"`)
- Multi-interval section: prefix with section name and append the zone
  - e.g. `"Tabata warm-up Z3+"`, `"Tabata warm-up Z1"`, `"Breakaway Z6"`
- If the Notes cell is non-empty, add it as a separate `"notes"` field on the interval — do **not** append it to the name
  - e.g. `{ "name": "Tabata Break Z4", "notes": "Out of the saddle", ... }`

#### 6. Assign IDs
- Top-level `sequence` items: `i001`, `i002`... for standalone intervals; `b001`, `b002`... for blocks
- Intervals inside blocks: use block-name prefix + index, e.g. `breakaway-1`, `breakaway-2`

#### 7. Validate and save
- Run `python3 utils/validate_workout.py workouts/<duration>min/<name>.json`
- Confirm `totalDuration` equals the sum of all interval durations (accounting for block repetitions)
- Save to `workouts/<duration>min/<kebab-case-name>.json` (include duration in filename)

## Common Patterns

### Team Time Trial Pattern:
Alternating high (Z5) and recovery (Z3) efforts:
```json
{ "id": "ttt1", "name": "Team Time Trial", "duration": 60, "powerZone": "Z5" },
{ "id": "ttt2", "name": "Team Time Trial", "duration": 60, "powerZone": "Z3" },
// Repeat...
```

### Over-Under Pattern:
Short efforts above threshold with recovery at threshold:
```json
{ "id": "ou1", "name": "Over-unders", "duration": 30, "powerZone": "Z5" },
{ "id": "ou2", "name": "Over-unders", "duration": 120, "powerZone": "Z3" },
{ "id": "ou3", "name": "Over-unders", "duration": 60, "powerZone": "Z1" },
// Repeat...
```

### Progressive Ramps:
Use powerZoneRange for smooth progressions:
```json
{ 
  "id": "ramp1", 
  "name": "Ramps", 
  "duration": 90, 
  "powerZoneRange": {"start": "Z2", "end": "Z5"} 
}
```

## Best Practices

1. **ID Generation**: Use sequential IDs (i001, i002, i003...) for intervals
2. **Naming**: Use descriptive names that indicate the purpose
3. **Duration**: Always in seconds, ensure totalDuration matches sum
4. **Validation**: Always validate after creating/modifying workouts
5. **Consistency**: Follow existing patterns in the workouts/ directory
6. **Documentation**: Update workout description with key features

## Video Configuration

Workouts can have an optional `videos` array at the top level for interval-synced video playback.

### VideoConfig Fields:
- `id`: Unique identifier (kebab-case)
- `name`: Display name
- `youtubeUrl`: Full YouTube URL (also accepts Vimeo URLs via `vimeoUrl`)
- `startTime`: Seconds into the video to seek to when triggered (default 0)
- `triggerIntervalId`: Interval ID that starts the video
- `endIntervalId`: Interval ID at which the video stops (inclusive)

### Block Expansion
The app expands blocks into individual intervals before matching video IDs. A block with `id: "b001"` containing intervals `["foo-1", "foo-2"]` and 3 repetitions expands to:

```
foo-1-block-b001-rep-1
foo-2-block-b001-rep-1
foo-1-block-b001-rep-2
foo-2-block-b001-rep-2
foo-1-block-b001-rep-3
foo-2-block-b001-rep-3
```

**Block IDs cannot be used** as `triggerIntervalId` or `endIntervalId` — they never appear in the expanded list.

### Matching Rules
The app uses a prefix match: a target ID of `"foo-1"` matches any expanded ID that starts with `"foo-1-block-"`. This means:
- `"triggerIntervalId": "foo-1"` → triggers at rep 1 of the first matching interval
- `"endIntervalId": "foo-2-block-b001-rep-3"` → ends at the last rep specifically (no overlap bleed)

For clean video handoffs at block boundaries, always use the **fully expanded ID** for `endIntervalId`:
```
"endIntervalId": "{intervalId}-block-{blockId}-rep-{repNumber}"
```

Example: last rep of block b001 → `"shift-mode-1-2-block-b001-rep-3"`

### Timing Calculation
To align a video timestamp with a specific workout moment:

1. Calculate the **workout elapsed time** at the target moment (sum of all interval durations up to and including that point)
2. Calculate the **video timestamp** in seconds (e.g. `6:44:11` = `6*3600 + 44*60 + 11` = `24251`)
3. Calculate elapsed time from the **trigger interval** to the target moment
4. `startTime = videoTimestamp - elapsedFromTriggerToTarget`

Example: video should hit 24251s at end of i025; trigger is at `shift-mode-6-1` (1575s before end of i025):
`startTime = 24251 - 1575 = 22676`

### Example:
```json
"videos": [
  {
    "id": "video-warmup",
    "name": "Warmup",
    "youtubeUrl": "https://www.youtube.com/watch?v=XXXXX",
    "startTime": 0,
    "triggerIntervalId": "i001",
    "endIntervalId": "shift-mode-1-2-block-b001-rep-3"
  },
  {
    "id": "video-main",
    "name": "Main Set",
    "youtubeUrl": "https://www.youtube.com/watch?v=YYYYY",
    "startTime": 22676,
    "triggerIntervalId": "shift-mode-6-1",
    "endIntervalId": "i026"
  }
]
```

## Error Prevention

- Don't mix `powerZone` and `powerZoneRange` in same interval
- Ensure all required fields are present (id, name, duration)
- Validate power zone format (1-7 or Z1-Z7 with optional +/-)
- Check cadence is between 40-150 if specified
- Verify block repetitions are positive integers
- Ensure interval durations are positive integers
