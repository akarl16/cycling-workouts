# Workout Import Quick Reference

## Converting CSV to Workout JSON Format

When importing workouts from CSV (like TrainerRoad exports), follow this process:

### 1. CSV Format Expected

```csv
name,zone,duration,cadence,reps
Warm-up,1,240,,
Build,2,120,,
Build,3,60,,
Wave Intervals,2,90,80,2
Wave Intervals,3,60,90,2
Wave Intervals,4,30,100,2
Recover,1,120,,
...
```

### 2. Identifying Blocks

Blocks are identified by:
- Multiple consecutive rows with the same name
- A `reps` value > 1 in the CSV

### 3. JSON Conversion Rules

#### Standalone Intervals
```json
{
  "type": "interval",
  "id": "warmup",
  "name": "Warm-up",
  "powerZone": 1,
  "duration": 240
}
```

#### Repeating Blocks
```json
{
  "type": "block",
  "id": "wave-intervals-block",
  "name": "Wave Intervals",
  "repetitions": 2,
  "intervals": [
    {
      "id": "wave-z2",
      "name": "Wave Z2",
      "powerZone": 2,
      "cadence": 80,
      "duration": 90
    },
    {
      "id": "wave-z3",
      "name": "Wave Z3",
      "powerZone": 3,
      "cadence": 90,
      "duration": 60
    }
  ]
}
```

### 4. Required Fields Checklist

**For the workout:**
- [ ] `id` - kebab-case workout identifier
- [ ] `name` - Display name
- [ ] `description` - Brief description
- [ ] `totalDuration` - Total seconds
- [ ] `sequence` - Array of intervals and blocks

**For each interval (standalone):**
- [ ] `type: "interval"`
- [ ] `id` - unique identifier
- [ ] `name` - display name
- [ ] `powerZone` - number (1-7) or string ("4-", "3+")
- [ ] `duration` - seconds
- [ ] `cadence` - (optional) RPM

**For each block:**
- [ ] `type: "block"`
- [ ] `id` - unique identifier
- [ ] `name` - display name
- [ ] `repetitions` - number of times to repeat
- [ ] `intervals` - array of intervals (no type field needed)

**For intervals inside blocks:**
- [ ] `id` - unique identifier
- [ ] `name` - display name
- [ ] `powerZone` - number or string
- [ ] `duration` - seconds
- [ ] `cadence` - (optional) RPM
- [ ] **NO** `type` field

### 5. Zone Modifiers

Power zones can include modifiers:
- `"4-"` - Lower end of zone 4
- `"4+"` - Upper end of zone 4
- `4` - Middle of zone 4 (no modifier)

### 6. Common Mistakes

❌ **Missing `type` field on standalone intervals**
```json
{
  "name": "Warm-up",  // Missing type!
  "powerZone": 1,
  "duration": 240
}
```

✅ **Correct**
```json
{
  "type": "interval",
  "id": "warmup",
  "name": "Warm-up",
  "powerZone": 1,
  "duration": 240
}
```

---

❌ **Missing `id` fields**
```json
{
  "type": "interval",
  "name": "Warm-up",  // Missing id!
  "powerZone": 1,
  "duration": 240
}
```

✅ **Correct**
```json
{
  "type": "interval",
  "id": "warmup",
  "name": "Warm-up",
  "powerZone": 1,
  "duration": 240
}
```

---

❌ **Using `zone` instead of `powerZone`**
```json
{
  "type": "interval",
  "id": "warmup",
  "name": "Warm-up",
  "zone": 1,  // Should be powerZone!
  "duration": 240
}
```

✅ **Correct**
```json
{
  "type": "interval",
  "id": "warmup",
  "name": "Warm-up",
  "powerZone": 1,
  "duration": 240
}
```

---

❌ **Adding `type` to intervals inside blocks**
```json
{
  "type": "block",
  "id": "build",
  "name": "Build",
  "repetitions": 1,
  "intervals": [
    {
      "type": "interval",  // Don't add type here!
      "id": "build-z2",
      "name": "Build Z2",
      "powerZone": 2,
      "duration": 120
    }
  ]
}
```

✅ **Correct**
```json
{
  "type": "block",
  "id": "build",
  "name": "Build",
  "repetitions": 1,
  "intervals": [
    {
      "id": "build-z2",
      "name": "Build Z2",
      "powerZone": 2,
      "duration": 120
    }
  ]
}
```

### 7. Validation

After creating the JSON, validate using:

```bash
python3 utils/validate_workout.py workouts/<duration>/<filename>.json
```

The validator checks:
1. All required fields are present
2. `type` field on all sequence items
3. NO `type` field on intervals inside blocks
4. `powerZone` not `zone`
5. All IDs are unique
6. Power zones valid (1-7 or Z1-Z7 with +/-)
7. Total duration matches sum of intervals

### 8. Example Complete Workout

See `workouts/power-endurance-50.json` for a complete example with:
- Standalone intervals (warmup, recovery, cooldown)
- Multiple blocks with different repetitions
- Mixed cadence targets
- Zone modifiers ("4-")
- Proper ID conventions
