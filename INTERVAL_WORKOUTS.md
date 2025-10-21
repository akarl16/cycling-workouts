# Interval Workout Format

This document describes the JSON schema for structured cycling interval workouts with power zones, cadence targets, and repeating blocks.

## Overview

The workout schema supports two formats:

1. **Legacy Format**: Separate `intervals` and `blocks` arrays
2. **Sequence Format** (Recommended): Single `sequence` array with mixed intervals and blocks

## Schema Location

- JSON Schema: `schema/workout-schema.json`
- TypeScript Types: `../cyclesync-coach/src/schemas/workoutSchema.ts`

## Required Workout Fields

- `id` (string): Unique identifier for the workout
- `name` (string): Display name of the workout
- Either `intervals` array (legacy) OR `sequence` array (new format)

## Optional Workout Fields

- `description` (string): Description of the workout
- `totalDuration` (integer): Total duration in seconds
- `isSample` (boolean): Whether this is a sample workout

## Interval Format

Each interval requires:

- `id` (string): Unique identifier
- `name` (string): Display name
- `duration` (integer): Duration in seconds (minimum 1)
- `powerZone`: Either a number (1-7) or string with modifier (e.g., "4-", "Z2+", "3+")

Optional interval fields:

- `cadence` (integer): Target cadence in RPM (40-150)
- `alternating` (object): Configuration for alternating between two power zones

### Power Zone Format

Power zones can be specified as:

- **Integer**: `1` through `7`
- **String with modifier**: 
  - `"4-"` - Zone 4 minus
  - `"4+"` - Zone 4 plus
  - `"Z3+"` - Zone 3 plus (with Z prefix)
  - `"Zone 2-"` - Zone 2 minus (with Zone prefix)

Pattern: `^(?:[Zz](?:one)?\s*)?[1-7][+-]?$`

### Alternating Intervals

Alternating intervals allow switching between two power zones during execution:

```json
{
  "id": "tempo-threshold-alternate",
  "name": "Tempo/Threshold Alternator",
  "duration": 600,
  "powerZone": 3,
  "cadence": 90,
  "alternating": {
    "powerZoneA": 3,
    "powerZoneB": 4,
    "cadenceA": 90,
    "cadenceB": 95,
    "startWithZone": "A"
  }
}
```

Required alternating fields:
- `powerZoneA`: First power zone
- `powerZoneB`: Second power zone

Optional alternating fields:
- `cadenceA`: Cadence for zone A
- `cadenceB`: Cadence for zone B
- `startWithZone`: "A" or "B" (default: "A")

## Block Format

Blocks allow repeating a set of intervals multiple times:

- `id` (string): Unique identifier
- `name` (string): Display name
- `repetitions` (integer): Number of times to repeat (minimum 1)
- `intervals` (array): Array of WorkoutInterval objects (minimum 1)

**Note**: Intervals inside blocks use the standard `WorkoutInterval` format without the `type` field.

## Legacy Format (intervals + blocks)

The original format uses two separate arrays:

```json
{
  "id": "pyramid-power",
  "name": "Pyramid Power",
  "description": "Classic pyramid interval workout",
  "intervals": [
    {
      "id": "warmup",
      "name": "Warm-up",
      "duration": 300,
      "powerZone": 2
    },
    {
      "id": "cooldown",
      "name": "Cool-down",
      "duration": 300,
      "powerZone": 1
    }
  ],
  "blocks": [
    {
      "id": "pyramid",
      "name": "Pyramid",
      "repetitions": 2,
      "intervals": [
        {
          "id": "build-1",
          "name": "Build 1",
          "duration": 60,
          "powerZone": 3
        },
        {
          "id": "build-2",
          "name": "Build 2",
          "duration": 60,
          "powerZone": 4
        }
      ]
    }
  ]
}
```

## Sequence Format (Recommended)

The new format uses a single `sequence` array where items can be either intervals or blocks, executed in order:

```json
{
  "id": "power-endurance-50",
  "name": "Power Endurance (50)",
  "description": "50-minute power endurance workout",
  "totalDuration": 3000,
  "sequence": [
    {
      "type": "interval",
      "id": "warmup",
      "name": "Warm-up",
      "powerZone": 1,
      "duration": 240
    },
    {
      "type": "block",
      "id": "wave-intervals",
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
    },
    {
      "type": "interval",
      "id": "cooldown",
      "name": "Cool-down",
      "powerZone": 1,
      "duration": 240
    }
  ]
}
```

**Key differences in sequence format:**

1. Items in `sequence` array have a `type` field: `"interval"` or `"block"`
2. Intervals and blocks are mixed in execution order
3. Intervals inside blocks do NOT need the `type` field
4. More intuitive to read and edit

## Example Workouts

See the `workouts/` directory for complete examples:

- `pyramid-power.json` - Legacy format with pyramid intervals
- `tabata-power.json` - High-intensity Tabata protocol
- `power-endurance-50.json` - Sequence format with multiple blocks
- `zone-modifier-demo.json` - Examples of zone modifiers (4-, 3+, etc.)

## Creating New Workouts

### Using the Sequence Format

1. Start with the basic structure:

```json
{
  "id": "my-workout",
  "name": "My Workout",
  "description": "Description here",
  "totalDuration": 3000,
  "sequence": []
}
```

2. Add intervals with `type: "interval"`:

```json
{
  "type": "interval",
  "id": "unique-id",
  "name": "Display Name",
  "powerZone": 2,
  "duration": 300
}
```

3. Add blocks with `type: "block"`:

```json
{
  "type": "block",
  "id": "unique-block-id",
  "name": "Block Name",
  "repetitions": 3,
  "intervals": [
    {
      "id": "interval-1",
      "name": "Work",
      "powerZone": 4,
      "duration": 120
    },
    {
      "id": "interval-2",
      "name": "Recover",
      "powerZone": 2,
      "duration": 60
    }
  ]
}
```

### Validation

Use the TypeScript validator in cyclesync-coach or validate against the JSON schema:

```bash
# Using Python validator
python utils/validate_json.py workouts/my-workout.json

# The cyclesync-coach app also validates on import
```

## Best Practices

1. **Use unique IDs**: Each interval and block needs a unique ID within the workout
2. **Prefer sequence format**: Easier to read and maintain
3. **Add cadence targets**: Helps guide riders during intervals
4. **Use zone modifiers**: Fine-tune difficulty with +/- modifiers
5. **Test workouts**: Import and preview in cyclesync-coach before use
6. **Document blocks**: Give blocks descriptive names (e.g., "Wave Intervals", "Pyramid Build")

## Schema Updates

When updating the schema:

1. Update `schema/workout-schema.json` (this repository)
2. Update `../cyclesync-coach/src/schemas/workoutSchema.ts` (TypeScript types)
3. Ensure both validators stay in sync
4. Test with existing workouts to ensure backward compatibility
