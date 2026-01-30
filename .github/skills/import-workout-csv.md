# Import Workout from CSV

Convert a cycling workout from CSV format to the interval workout JSON schema.

## Context
This skill helps import structured workout data (power zones, intervals, duration) from CSV spreadsheets into the standardized JSON format used by cyclesync-coach.

## Process

### 1. Analyze CSV Structure
- Identify the header row (contains: Name, Power zone, Cadence, Duration, Notes)
- Look for section headers (rows with Name but no Notes - like "Ramps", "Steady TT")
- Note cumulative time tracking columns (if present)
- Check for power zone range notation (e.g., "Z2 -> 3 -> 5")

### 2. Parse Power Zones
For each row with a power zone:
- **Simple zones**: "Z1", "Z2+", "Z3-" → Use directly as `"powerZone": "Z2+"`
- **Zone ranges**: "Z2 -> 3 -> 5" → Create `powerZoneRange`:
  ```json
  "powerZoneRange": {
    "start": "Z2",   // First zone
    "end": "Z5"      // Last zone
  }
  ```
- Extract the starting zone (first) and ending zone (last) from arrows

### 3. Parse Duration
Convert time format to seconds:
- `H:MM:SS` → hours×3600 + minutes×60 + seconds
- `MM:SS` → minutes×60 + seconds
- Examples: "0:03:00" = 180, "1:30:00" = 5400

### 4. Create Intervals
For each row with duration and power zone:
```json
{
  "type": "interval",
  "id": "i###",           // Sequential: i001, i002, i003...
  "name": "<section>",     // From Name column or section header
  "duration": <seconds>,   // Parsed duration
  "powerZone": "Z#",       // Or powerZoneRange object
  "cadence": <rpm>         // Optional, if Cadence column has value
}
```

### 5. Name Intervals
Priority for interval names:
1. Use Name column value if present and specific to this row
2. Use the last section header (like "Ramps", "Team Time Trial")
3. Use Notes column if descriptive
4. Use power zone as fallback

### 6. Build Workout Object
```json
{
  "id": "YYYY-MM-DD-workout-name-duration",
  "name": "Workout Name",
  "description": "Brief description of workout",
  "totalDuration": <sum of all interval durations>,
  "sequence": [
    // All intervals in order
  ],
  "isSample": false
}
```

### 7. Determine File Location
- Calculate total duration in minutes
- Round to nearest duration category: 30, 45, 50, 60, 90
- Save to: `workouts/<duration>min/<workout-name>.json`
- Use kebab-case for filename

### 8. Validate
Run validator:
```bash
python3 utils/validate_workout.py workouts/<duration>min/<filename>.json
```

## Examples

### Simple Interval
CSV: `,,Z2,,0:03:00,,`
→ `{"type": "interval", "id": "i001", "name": "Warmup", "duration": 180, "powerZone": "Z2"}`

### With Cadence
CSV: `,,Z3,100,0:02:00,,`
→ `{"type": "interval", "id": "i002", "name": "Tempo", "duration": 120, "powerZone": "Z3", "cadence": 100}`

### Zone Range
CSV: `Ramps,Z2 -> 3 -> 5,- + ++,0:01:30,,`
→ `{"type": "interval", "id": "i003", "name": "Ramps", "duration": 90, "powerZoneRange": {"start": "Z2", "end": "Z5"}}`

## Common Patterns

### Repeating Sets
If you see the same pattern repeated (e.g., 4x: Z5 60s, Z3 60s):
Consider using a block:
```json
{
  "type": "block",
  "id": "b001",
  "name": "Team Time Trial",
  "repetitions": 4,
  "intervals": [
    {"id": "work", "name": "Pull", "duration": 60, "powerZone": "Z5"},
    {"id": "rest", "name": "Recovery", "duration": 60, "powerZone": "Z3"}
  ]
}
```

## Validation Checks
- ✓ All intervals have: type, id, name, duration
- ✓ All intervals have powerZone OR powerZoneRange (not both)
- ✓ Power zones are 1-7 or Z1-Z7 with optional +/-
- ✓ Cadence (if present) is 40-150
- ✓ totalDuration equals sum of all interval durations
- ✓ No missing or duplicate IDs

## Output
After successful import:
1. JSON file created in correct directory
2. Validation passed
3. Summary: "✓ Imported '<name>' with X intervals, Y minutes total"
