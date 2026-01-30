# cycling-workouts

A repository for storing and managing cycling workout data using standardized JSON schemas.

## Overview

This repository provides:
- **JSON schemas** for structured cycling workout data
- **Interval workout format** for power-based training with zones, cadence, and repeating blocks
- **Utility scripts** to validate workout data
- **Example files** demonstrating the workout format

## Documentation

- **[Interval Workouts](INTERVAL_WORKOUTS.md)** - Complete guide to the interval workout schema
- **[Import Guide](IMPORT_GUIDE.md)** - Quick reference for converting CSV to JSON

## Directory Structure

```
cycling-workouts/
├── schema/                      # JSON schema definitions
│   └── workout-schema.json      # Interval workout schema
├── workouts/                    # Structured interval workouts (JSON)
│   ├── power-endurance-50.json
│   ├── pyramid-power.json
│   ├── tabata-power.json
│   └── ...
├── utils/                       # Utility scripts
│   └── validate_workout.py     # Validate workout JSON
├── INTERVAL_WORKOUTS.md        # Interval workout documentation
└── IMPORT_GUIDE.md             # CSV to JSON import guide
```

## Quick Start

### Creating a New Interval Workout

1. **Copy an existing workout** from `workouts/` as a template
2. **Update the workout fields**:
   - `id`: Unique kebab-case identifier
   - `name`: Display name
   - `description`: Brief description
   - `totalDuration`: Total seconds
3. **Build the sequence** with intervals and blocks
4. **Validate** by importing into cyclesync-coach

See [INTERVAL_WORKOUTS.md](INTERVAL_WORKOUTS.md) for complete format documentation.

### Validating Interval Workouts

Use the interval workout validator to check your workout files:

```bash
# Validate a single workout
python3 utils/validate_workout.py workouts/60min/my-workout.json

# Validate all workouts in a directory
python3 utils/validate_workout.py workouts/90min/*.json

# Validate all workouts
python3 utils/validate_workout.py workouts/**/*.json
```

The validator checks:
- Required fields (id, name, sequence)
- Power zone formats (1-7 or Z1-Z7 with optional +/-)
- Duration values are positive integers
- Cadence values are between 40-150
- Block repetitions are positive integers
- Proper interval/block structure

### Sequence Format Example

```json
{
  "id": "my-workout",
  "name": "My Custom Workout",
  "description": "A great workout",
  "totalDuration": 1800,
  "sequence": [
    {
      "type": "interval",
      "id": "warmup",
      "name": "Warm-up",
      "powerZone": 2,
      "duration": 300
    },
    {
      "type": "block",
      "id": "main-set",
      "name": "Main Set",
      "repetitions": 3,
      "intervals": [
        {
          "id": "work",
          "name": "Work",
          "powerZone": 4,
          "duration": 180
        },
        {
          "id": "recover",
          "name": "Recover",
          "powerZone": 2,
          "duration": 120
        }
      ]
    }
  ]
}
```

---

## JSON Schema

The workout schema (`schema/workout-schema.json`) defines the structure for interval workout data. See [INTERVAL_WORKOUTS.md](INTERVAL_WORKOUTS.md) for complete documentation on:

- Required fields (id, name, sequence)
- Interval structure with power zones and durations
- Repeating blocks for patterns
- Power zone formats (1-7 or Z1-Z7 with +/-)
- Optional fields (cadence, theme, description)

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/akarl16/cycling-workouts.git
   cd cycling-workouts
   ```

2. **Convert your CSV workout data:**
   ```bash
   python utils/csv_to_json.py your-workouts.csv
   ```

3. **Your workout data will be saved in the `workouts/` directory as JSON files**

## Contributing

Feel free to submit issues or pull requests to improve the schema or utilities.

## License

This project is open source and available under the MIT License.