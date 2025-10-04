# cycling-workouts

A repository for storing and managing cycling workout data using a standardized JSON schema.

## Overview

This repository provides:
- A JSON schema for structured cycling workout data
- A utility to convert workout data from CSV to JSON format
- Example files demonstrating the format

## Directory Structure

```
cycling-workouts/
├── schema/              # JSON schema definitions
│   └── workout-schema.json
├── workouts/           # Stored workout data (JSON files)
├── utils/              # Utility scripts
│   ├── csv_to_json.py      # Convert CSV to JSON
│   └── validate_json.py    # Validate JSON against schema
└── examples/           # Example files
    └── sample-workouts.csv
```

## JSON Schema

The workout schema (`schema/workout-schema.json`) defines the structure for cycling workout data with the following fields:

**Required fields:**
- `id` (string): Unique identifier for the workout
- `date` (string): Date and time in ISO 8601 format (e.g., "2024-01-15T08:30:00Z")
- `duration` (number): Duration in minutes
- `distance` (number): Distance in kilometers

**Optional fields:**
- `avgSpeed` (number): Average speed in km/h
- `maxSpeed` (number): Maximum speed in km/h
- `avgHeartRate` (integer): Average heart rate in bpm
- `maxHeartRate` (integer): Maximum heart rate in bpm
- `avgCadence` (integer): Average cadence in rpm
- `maxCadence` (integer): Maximum cadence in rpm
- `avgPower` (integer): Average power in watts
- `maxPower` (integer): Maximum power in watts
- `calories` (integer): Calories burned
- `elevationGain` (number): Total elevation gain in meters
- `workoutType` (string): Type of workout (recovery, endurance, tempo, threshold, interval, race, other)
- `notes` (string): Additional notes about the workout

## CSV to JSON Converter

The `csv_to_json.py` utility converts cycling workout data from CSV format to JSON format according to the schema.

### Usage

**Basic usage (creates individual JSON files for each workout):**
```bash
python utils/csv_to_json.py examples/sample-workouts.csv
```

**Save all workouts to a single JSON file:**
```bash
python utils/csv_to_json.py examples/sample-workouts.csv --single-file
```

**Specify output directory:**
```bash
python utils/csv_to_json.py examples/sample-workouts.csv --output-dir ./my-workouts
```

**View help:**
```bash
python utils/csv_to_json.py --help
```

### CSV Format

The CSV file should have a header row with field names matching the JSON schema. Example:

```csv
id,date,duration,distance,avgSpeed,maxSpeed,avgHeartRate,maxHeartRate,workoutType,notes
workout-001,2024-01-15T08:30:00Z,60,25.5,25.5,42.3,145,168,endurance,Morning ride
workout-002,2024-01-17T17:00:00Z,45,18.2,24.3,38.5,152,175,tempo,Evening session
```

See `examples/sample-workouts.csv` for a complete example.

## JSON Validator

The `validate_json.py` utility validates workout JSON files against the schema to ensure data integrity.

### Usage

**Validate a single workout file:**
```bash
python utils/validate_json.py workouts/workout-001.json
```

**Validate multiple workout files:**
```bash
python utils/validate_json.py workouts/workout-*.json
```

**Validate a file containing an array of workouts:**
```bash
python utils/validate_json.py all-workouts.json
```

**View help:**
```bash
python utils/validate_json.py --help
```

The validator checks:
- All required fields are present (id, date, duration, distance)
- Field types match the schema (strings, numbers, integers)
- Numeric values are non-negative
- workoutType is one of the valid enum values

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