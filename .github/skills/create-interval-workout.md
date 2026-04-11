# Create New Interval Workout

Create a structured cycling workout from scratch using the interval workout schema.

## Context
This skill helps create new workout templates with power zones, intervals, and optional repeating blocks for use in cyclesync-coach.

## Quick Start Template

```json
{
  "id": "workout-name-duration",
  "name": "Workout Name",
  "description": "Brief description of the workout focus",
  "totalDuration": 3000,
  "sequence": [
    {
      "type": "interval",
      "id": "i001",
      "name": "Warmup",
      "duration": 300,
      "powerZone": "Z2"
    }
  ],
  "isSample": false
}
```

## Step-by-Step Process

### 1. Define Workout Structure
Plan the workout phases:
- Warmup (Z1-Z2, 5-10 minutes)
- Main set (varies by workout type)
- Cooldown (Z1-Z2, 3-5 minutes)

### 2. Choose Power Zones

**Zone Reference:**
- Z1: Active recovery (< 55% FTP)
- Z2: Endurance (56-75% FTP)
- Z3: Tempo (76-90% FTP)
- Z4: Threshold (91-105% FTP)
- Z5: VO2 Max (106-120% FTP)
- Z6: Anaerobic (121-150% FTP)
- Z7: Neuromuscular (> 150% FTP)

**Modifiers:**
- `Z2+`: Upper Z2
- `Z3-`: Lower Z3
- Plain: Middle of zone

### 3. Create Intervals

**Simple interval:**
```json
{
  "type": "interval",
  "id": "i001",
  "name": "Steady State",
  "duration": 600,
  "powerZone": "Z3"
}
```

**With cadence target:**
```json
{
  "type": "interval",
  "id": "i002",
  "name": "High Cadence",
  "duration": 300,
  "powerZone": "Z2",
  "cadence": 100
}
```

**Progressive (ramp):**
```json
{
  "type": "interval",
  "id": "i003",
  "name": "Build",
  "duration": 180,
  "powerZoneRange": {
    "start": "Z2",
    "end": "Z5"
  }
}
```

### 4. Create Repeating Blocks

For patterns that repeat (e.g., 5x [4min work, 2min rest]):

```json
{
  "type": "block",
  "id": "b001",
  "name": "Main Set",
  "repetitions": 5,
  "intervals": [
    {
      "id": "work",
      "name": "Work",
      "duration": 240,
      "powerZone": "Z4"
    },
    {
      "id": "rest",
      "name": "Rest",
      "duration": 120,
      "powerZone": "Z2"
    }
  ]
}
```

### 5. ID Conventions

**Intervals:** Sequential with 3-digit padding
- `i001`, `i002`, `i003`, ...

**Blocks:** Sequential with 3-digit padding
- `b001`, `b002`, `b003`, ...

**Within blocks:** Descriptive, short
- `work`, `rest`, `sprint`, `recovery`

### 6. Calculate Total Duration

Sum all interval durations:
- For simple intervals: add duration
- For blocks: add (sum of block intervals × repetitions)
- Verify totalDuration matches calculated sum

### 7. Choose File Location

Based on total duration:
- 30 min (1800s) → `workouts/30min/`
- 45 min (2700s) → `workouts/45min/`
- 50 min (3000s) → `workouts/50min/`
- 60 min (3600s) → `workouts/60min/`
- 90 min (5400s) → `workouts/90min/`

Filename: `<workout-name>.json` (kebab-case)

### 8. Optional: Add Theme

```json
{
  "theme": "criterium"
}
```

Valid themes: `default`, `halloween`, `christmas`, `wintry`, `valentines`, `holyhill`, `criterium`, `custom`

### 9. Optional: Add Videos

Workouts can include an optional `videos` array for interval-synced playback. Only YouTube and Vimeo are supported (not DRM-protected services like Peacock).

```json
"videos": [
  {
    "id": "video-warmup",
    "name": "Warmup",
    "youtubeUrl": "https://www.youtube.com/watch?v=XXXXX",
    "startTime": 0,
    "triggerIntervalId": "i001",
    "endIntervalId": "i010"
  }
]
```

**Block expansion rules** — block IDs (e.g. `b001`) are never in the expanded interval list and cannot be used as `triggerIntervalId` or `endIntervalId`. Blocks expand to:
```
{intervalId}-block-{blockId}-rep-{repNumber}
```
Example: interval `foo-2` in block `b001` rep 3 → `foo-2-block-b001-rep-3`

**Matching shorthand** — a bare interval ID like `"foo-1"` prefix-matches all expanded IDs starting with `"foo-1-block-"`, so it triggers at rep 1 without needing the full expanded form. Use full expanded IDs for `endIntervalId` to avoid overlap with adjacent videos:
```json
"endIntervalId": "shift-mode-1-2-block-b001-rep-3"
```

**Timing calculation** — to align a video timestamp with a specific workout moment:
1. `videoTimestamp` = target video time in seconds (e.g. `6:44:11` → `24251`)
2. `elapsedFromTrigger` = sum of interval durations from trigger interval to target moment
3. `startTime = videoTimestamp - elapsedFromTrigger`

See [VIDEOS.md](../../VIDEOS.md) for full reference.

### 10. Validate

```bash
python3 utils/validate_workout.py workouts/<duration>/<filename>.json
```

## Common Workout Patterns

### Sweet Spot Training
```json
{
  "sequence": [
    {"type": "interval", "id": "i001", "name": "Warmup", "duration": 600, "powerZone": "Z2"},
    {"type": "interval", "id": "i002", "name": "Sweet Spot", "duration": 1200, "powerZone": "Z3+"},
    {"type": "interval", "id": "i003", "name": "Recovery", "duration": 300, "powerZone": "Z1"},
    {"type": "interval", "id": "i004", "name": "Sweet Spot", "duration": 1200, "powerZone": "Z3+"},
    {"type": "interval", "id": "i005", "name": "Cooldown", "duration": 300, "powerZone": "Z1"}
  ]
}
```

### VO2 Max Intervals
```json
{
  "sequence": [
    {"type": "interval", "id": "i001", "name": "Warmup", "duration": 600, "powerZone": "Z2"},
    {
      "type": "block",
      "id": "b001",
      "name": "VO2 Max",
      "repetitions": 5,
      "intervals": [
        {"id": "on", "name": "On", "duration": 180, "powerZone": "Z5"},
        {"id": "off", "name": "Off", "duration": 180, "powerZone": "Z2"}
      ]
    },
    {"type": "interval", "id": "i002", "name": "Cooldown", "duration": 300, "powerZone": "Z1"}
  ]
}
```

### Pyramid
```json
{
  "sequence": [
    {"type": "interval", "id": "i001", "name": "Warmup", "duration": 300, "powerZone": "Z2"},
    {"type": "interval", "id": "i002", "name": "Build", "duration": 60, "powerZone": "Z4"},
    {"type": "interval", "id": "i003", "name": "Recovery", "duration": 60, "powerZone": "Z2"},
    {"type": "interval", "id": "i004", "name": "Build", "duration": 120, "powerZone": "Z4"},
    {"type": "interval", "id": "i005", "name": "Recovery", "duration": 120, "powerZone": "Z2"},
    {"type": "interval", "id": "i006", "name": "Build", "duration": 180, "powerZone": "Z4"},
    {"type": "interval", "id": "i007", "name": "Recovery", "duration": 120, "powerZone": "Z2"},
    {"type": "interval", "id": "i008", "name": "Build", "duration": 120, "powerZone": "Z4"},
    {"type": "interval", "id": "i009", "name": "Recovery", "duration": 60, "powerZone": "Z2"},
    {"type": "interval", "id": "i010", "name": "Build", "duration": 60, "powerZone": "Z4"},
    {"type": "interval", "id": "i011", "name": "Cooldown", "duration": 300, "powerZone": "Z1"}
  ]
}
```

## Validation Checklist

- [ ] Unique workout ID
- [ ] Descriptive name
- [ ] totalDuration matches sum of intervals
- [ ] All intervals have required fields (type, id, name, duration)
- [ ] Power zones valid (1-7 or Z1-Z7 with +/-)
- [ ] Cadence values between 40-150 (if specified)
- [ ] No duplicate interval IDs
- [ ] Passes `validate_workout.py` with no errors

## Tips

1. **Start with existing workouts**: Copy a similar workout as a template
2. **Test duration math**: Use a calculator to ensure totalDuration is correct
3. **Be consistent with naming**: Use a clear naming pattern within the workout
4. **Add descriptions**: Help users understand the workout purpose
5. **Consider progressions**: Group related workouts (V1, V2, V3) for difficulty levels
