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

### 9. Validate

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
