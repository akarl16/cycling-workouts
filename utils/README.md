# Utilities README

This directory contains scripts for managing cycling workout data.

## Workout Validator

### `validate_workout.py`
Validates interval workout JSON files against the workout schema.

```bash
# Validate a single workout
python3 validate_workout.py workouts/90min/wind-up-90.json

# Validate all workouts in a directory
python3 validate_workout.py workouts/90min/*.json

# Validate all workouts
python3 validate_workout.py workouts/**/*.json
```

**Checks:**
- Required fields (id, name, sequence or intervals)
- Power zone formats (1-7 or Z1-Z7 with +/-)
- Duration values are positive integers
- Cadence values between 40-150
- Block repetitions are positive integers
- Proper interval/block structure

---

## Workout Format
```json
{
  "id": "my-workout-60",
  "name": "My Workout",
  "totalDuration": 3600,
  "sequence": [
    {
      "type": "interval",
      "id": "i001",
      "name": "Warmup",
      "duration": 300,
      "powerZone": "Z2"
    }
  ]
}
```

**Validate:** `python3 validate_workout.py workouts/60min/my-workout-60.json`

---

## See Also

- [INTERVAL_WORKOUTS.md](../INTERVAL_WORKOUTS.md) - Complete interval workout format documentation
- [IMPORT_GUIDE.md](../IMPORT_GUIDE.md) - Quick import reference
- [.github/skills/](../.github/skills/) - Copilot skills for importing and creating workouts
