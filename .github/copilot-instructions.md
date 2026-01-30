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
When importing a workout CSV with power zones and intervals:

1. **Analyze the structure**:
   - Look for columns: Name, Power zone, Cadence, Duration, Notes
   - Identify section headers (like "Ramps", "Steady TT", "Over-unders")
   - Check for power zone ranges (e.g., "Z2 -> 3 -> 5")

2. **Create JSON directly**:
   - Don't use scripts - manually create the JSON for clarity
   - Parse duration (HH:MM:SS or MM:SS to seconds)
   - Parse power zones (handle ranges with "->" separator)
   - Use section names for interval names when available
   - Group repeated patterns into blocks when appropriate

3. **Power Zone Parsing**:
   - Simple: "Z1", "Z2+", "Z3-" → Use as is
   - Ranges: "Z2 -> 3 -> 5" → `{"powerZoneRange": {"start": "Z2", "end": "Z5"}}`
   - Extract final zone from ranges (the "end" value)

4. **Validate**:
   - Run `python3 utils/validate_workout.py workouts/<duration>/<name>.json`
   - Check total duration matches (sum all interval durations)

5. **File naming**:
   - Save to: `workouts/<duration>min/<workout-name>.json`
   - Use kebab-case for filename
   - Include duration in filename (e.g., `wind-up-90.json`)

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

## Error Prevention

- Don't mix `powerZone` and `powerZoneRange` in same interval
- Ensure all required fields are present (id, name, duration)
- Validate power zone format (1-7 or Z1-Z7 with optional +/-)
- Check cadence is between 40-150 if specified
- Verify block repetitions are positive integers
- Ensure interval durations are positive integers
