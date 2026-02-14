#!/usr/bin/env python3
"""
Workout Validator for Interval-Based Cycling Workouts

This utility validates interval workout JSON files against the workout-schema.json schema.
Use this for workout templates with power zones and intervals (not ride tracking data).
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_power_zone(zone: Any) -> Tuple[bool, str]:
    """Validate power zone format."""
    if isinstance(zone, int):
        if 1 <= zone <= 7:
            return True, ""
        return False, f"Power zone must be 1-7, got {zone}"
    
    if isinstance(zone, str):
        # Match pattern like Z1, Z2+, Z3-, etc.
        import re
        if re.match(r'^(?:[Zz](?:one)?\s*)?[1-7][+-]?$', zone):
            return True, ""
        return False, f"Invalid power zone format: '{zone}'"
    
    return False, f"Power zone must be integer or string, got {type(zone).__name__}"


def validate_interval(interval: Dict[str, Any], path: str = "") -> List[str]:
    """Validate a single interval."""
    errors = []
    
    # Required fields
    required = ["id", "name", "duration"]
    for field in required:
        if field not in interval:
            errors.append(f"{path}: Missing required field '{field}'")
    
    # Must have either powerZone or powerZoneRange
    has_power_zone = "powerZone" in interval
    has_power_zone_range = "powerZoneRange" in interval
    
    if not has_power_zone and not has_power_zone_range:
        errors.append(f"{path}: Must have either 'powerZone' or 'powerZoneRange'")
    elif has_power_zone and has_power_zone_range:
        errors.append(f"{path}: Cannot have both 'powerZone' and 'powerZoneRange'")
    
    # Validate powerZone if present
    if has_power_zone:
        valid, msg = validate_power_zone(interval["powerZone"])
        if not valid:
            errors.append(f"{path}: {msg}")
    
    # Validate powerZoneRange if present
    if has_power_zone_range:
        pzr = interval["powerZoneRange"]
        if not isinstance(pzr, dict):
            errors.append(f"{path}: powerZoneRange must be an object")
        else:
            if "start" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'start'")
            else:
                valid, msg = validate_power_zone(pzr["start"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.start: {msg}")
            
            if "end" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'end'")
            else:
                valid, msg = validate_power_zone(pzr["end"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.end: {msg}")
    
    # Validate duration
    if "duration" in interval:
        if not isinstance(interval["duration"], int) or interval["duration"] < 1:
            errors.append(f"{path}: duration must be a positive integer")
    
    # Validate cadence if present
    if "cadence" in interval:
        cadence = interval["cadence"]
        if not isinstance(cadence, int) or not (40 <= cadence <= 150):
            errors.append(f"{path}: cadence must be an integer between 40 and 150")
    
    # Validate alternating if present
    if "alternating" in interval:
        alt = interval["alternating"]
        if not isinstance(alt, dict):
            errors.append(f"{path}: alternating must be an object")
        else:
            if "powerZoneA" not in alt:
                errors.append(f"{path}.alternating: missing 'powerZoneA'")
            else:
                valid, msg = validate_power_zone(alt["powerZoneA"])
                if not valid:
                    errors.append(f"{path}.alternating.powerZoneA: {msg}")
            
            if "powerZoneB" not in alt:
                errors.append(f"{path}.alternating: missing 'powerZoneB'")
            else:
                valid, msg = validate_power_zone(alt["powerZoneB"])
                if not valid:
                    errors.append(f"{path}.alternating.powerZoneB: {msg}")
    
    # Validate notes if present (optional string)
    if "notes" in interval:
        if not isinstance(interval["notes"], str):
            errors.append(f"{path}: notes must be a string")
    
    return errors


def validate_block(block: Dict[str, Any], path: str = "") -> List[str]:
    """Validate a repeating block."""
    errors = []
    
    # Required fields
    required = ["id", "name", "repetitions", "intervals"]
    for field in required:
        if field not in block:
            errors.append(f"{path}: Missing required field '{field}'")
    
    # Validate repetitions
    if "repetitions" in block:
        if not isinstance(block["repetitions"], int) or block["repetitions"] < 1:
            errors.append(f"{path}: repetitions must be a positive integer")
    
    # Validate intervals
    if "intervals" in block:
        if not isinstance(block["intervals"], list):
            errors.append(f"{path}: intervals must be an array")
        elif len(block["intervals"]) == 0:
            errors.append(f"{path}: intervals array cannot be empty")
        else:
            for idx, interval in enumerate(block["intervals"]):
                interval_errors = validate_interval(
                    interval, 
                    f"{path}.intervals[{idx}]"
                )
                errors.extend(interval_errors)
    
    return errors


def validate_sequence_item(item: Dict[str, Any], idx: int) -> List[str]:
    """Validate a sequence item (interval or block)."""
    errors = []
    
    if "type" not in item:
        errors.append(f"sequence[{idx}]: Missing 'type' field")
        return errors
    
    item_type = item["type"]
    
    if item_type == "interval":
        errors.extend(validate_interval(item, f"sequence[{idx}]"))
    elif item_type == "block":
        errors.extend(validate_block(item, f"sequence[{idx}]"))
    else:
        errors.append(f"sequence[{idx}]: type must be 'interval' or 'block', got '{item_type}'")
    
    return errors


def validate_work_block_definition(definition: Dict[str, Any], path: str = "") -> List[str]:
    """Validate a work block definition for Melodic Roulette."""
    errors = []
    
    if not isinstance(definition, dict):
        errors.append(f"{path}: Work block definition must be an object")
        return errors
    
    if "name" not in definition:
        errors.append(f"{path}: Missing required field 'name'")
    elif not isinstance(definition["name"], str) or len(definition["name"]) == 0:
        errors.append(f"{path}: name must be a non-empty string")
    
    # Must have either powerZone, powerZoneRange, or alternating
    has_power_zone = "powerZone" in definition
    has_power_zone_range = "powerZoneRange" in definition
    has_alternating = "alternating" in definition
    
    exclusive_count = sum([has_power_zone, has_power_zone_range, has_alternating])
    
    if exclusive_count == 0:
        errors.append(f"{path}: Must have either 'powerZone', 'powerZoneRange', or 'alternating'")
    elif exclusive_count > 1:
        errors.append(f"{path}: Cannot have more than one of 'powerZone', 'powerZoneRange', or 'alternating'")
    
    # Validate powerZone if present
    if has_power_zone:
        valid, msg = validate_power_zone(definition["powerZone"])
        if not valid:
            errors.append(f"{path}.powerZone: {msg}")
    
    # Validate powerZoneRange if present
    if has_power_zone_range:
        pzr = definition["powerZoneRange"]
        if not isinstance(pzr, dict):
            errors.append(f"{path}: powerZoneRange must be an object")
        else:
            if "start" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'start'")
            else:
                valid, msg = validate_power_zone(pzr["start"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.start: {msg}")
            
            if "end" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'end'")
            else:
                valid, msg = validate_power_zone(pzr["end"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.end: {msg}")
    
    # Validate alternating if present
    if has_alternating:
        alt = definition["alternating"]
        if not isinstance(alt, dict):
            errors.append(f"{path}: alternating must be an object")
        else:
            if "powerZoneA" not in alt:
                errors.append(f"{path}.alternating: missing 'powerZoneA'")
            else:
                valid, msg = validate_power_zone(alt["powerZoneA"])
                if not valid:
                    errors.append(f"{path}.alternating.powerZoneA: {msg}")
            
            if "powerZoneB" not in alt:
                errors.append(f"{path}.alternating: missing 'powerZoneB'")
            else:
                valid, msg = validate_power_zone(alt["powerZoneB"])
                if not valid:
                    errors.append(f"{path}.alternating.powerZoneB: {msg}")
            
            # Validate optional cadences
            if "cadenceA" in alt:
                cadence = alt["cadenceA"]
                if not isinstance(cadence, int) or not (40 <= cadence <= 150):
                    errors.append(f"{path}.alternating.cadenceA: must be an integer between 40 and 150")
            
            if "cadenceB" in alt:
                cadence = alt["cadenceB"]
                if not isinstance(cadence, int) or not (40 <= cadence <= 150):
                    errors.append(f"{path}.alternating.cadenceB: must be an integer between 40 and 150")
    
    if "cadence" in definition:
        cadence = definition["cadence"]
        if not isinstance(cadence, int) or not (40 <= cadence <= 150):
            errors.append(f"{path}: cadence must be an integer between 40 and 150")
    
    return errors


def validate_roulette_slot(slot: Dict[str, Any], path: str = "") -> List[str]:
    """Validate a Melodic Roulette slot."""
    errors = []
    
    if not isinstance(slot, dict):
        errors.append(f"{path}: Slot must be an object")
        return errors
    
    if "id" not in slot:
        errors.append(f"{path}: Missing required field 'id'")
    
    if "intervalType" not in slot:
        errors.append(f"{path}: Missing required field 'intervalType'")
    elif slot["intervalType"] not in ("work", "recovery"):
        errors.append(f"{path}: intervalType must be 'work' or 'recovery', got '{slot['intervalType']}'")
    
    if "playlistId" not in slot:
        errors.append(f"{path}: Missing required field 'playlistId'")
    elif not isinstance(slot["playlistId"], str) or len(slot["playlistId"]) == 0:
        errors.append(f"{path}: playlistId must be a non-empty string")
    
    if "durationRange" in slot:
        valid_ranges = ["short", "medium", "long"]
        if slot["durationRange"] not in valid_ranges:
            errors.append(f"{path}: durationRange must be one of {valid_ranges}, got '{slot['durationRange']}'")
    
    # Validate optional powerZone and powerZoneRange (for recovery intervals)
    has_power_zone = "powerZone" in slot
    has_power_zone_range = "powerZoneRange" in slot
    
    if has_power_zone and has_power_zone_range:
        errors.append(f"{path}: Cannot have both 'powerZone' and 'powerZoneRange'")
    
    if has_power_zone:
        # Only allowed for recovery intervals
        if slot.get("intervalType") == "work":
            errors.append(f"{path}: powerZone not allowed for work intervals (use workBlockDefinitions instead)")
        valid, msg = validate_power_zone(slot["powerZone"])
        if not valid:
            errors.append(f"{path}.powerZone: {msg}")
    
    if has_power_zone_range:
        # Only allowed for recovery intervals
        if slot.get("intervalType") == "work":
            errors.append(f"{path}: powerZoneRange not allowed for work intervals (use workBlockDefinitions instead)")
        pzr = slot["powerZoneRange"]
        if not isinstance(pzr, dict):
            errors.append(f"{path}: powerZoneRange must be an object")
        else:
            if "start" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'start'")
            else:
                valid, msg = validate_power_zone(pzr["start"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.start: {msg}")
            
            if "end" not in pzr:
                errors.append(f"{path}: powerZoneRange missing 'end'")
            else:
                valid, msg = validate_power_zone(pzr["end"])
                if not valid:
                    errors.append(f"{path}.powerZoneRange.end: {msg}")
    
    # Validate optional cadence
    if "cadence" in slot:
        if slot.get("intervalType") == "work":
            errors.append(f"{path}: cadence not allowed for work intervals (use workBlockDefinitions instead)")
        cadence = slot["cadence"]
        if not isinstance(cadence, int) or not (40 <= cadence <= 150):
            errors.append(f"{path}: cadence must be an integer between 40 and 150")
    
    return errors


def validate_melodic_roulette(workout: Dict[str, Any]) -> List[str]:
    """Validate a Melodic Roulette workout."""
    errors = []
    
    if workout.get("mode") != "melodic-roulette":
        errors.append("mode must be 'melodic-roulette'")
    
    # Validate workBlockDefinitions
    if "workBlockDefinitions" not in workout:
        errors.append("Missing required field: 'workBlockDefinitions'")
    elif not isinstance(workout["workBlockDefinitions"], list):
        errors.append("'workBlockDefinitions' must be an array")
    elif len(workout["workBlockDefinitions"]) == 0:
        errors.append("'workBlockDefinitions' must have at least one definition")
    else:
        for idx, definition in enumerate(workout["workBlockDefinitions"]):
            errors.extend(validate_work_block_definition(
                definition, f"workBlockDefinitions[{idx}]"
            ))
    
    # Validate slots
    if "slots" not in workout:
        errors.append("Missing required field: 'slots'")
    elif not isinstance(workout["slots"], list):
        errors.append("'slots' must be an array")
    elif len(workout["slots"]) == 0:
        errors.append("'slots' must have at least one slot")
    else:
        for idx, slot in enumerate(workout["slots"]):
            errors.extend(validate_roulette_slot(slot, f"slots[{idx}]"))
    
    # Validate theme if present
    if "theme" in workout:
        valid_themes = ["default", "halloween", "christmas", "wintry", "valentines", 
                       "holyhill", "criterium", "custom"]
        if workout["theme"] not in valid_themes:
            errors.append(f"theme must be one of {valid_themes}, got '{workout['theme']}'")
    
    return errors


def validate_workout(workout: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a workout JSON structure (standard or Melodic Roulette).
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ["id", "name"]
    for field in required_fields:
        if field not in workout:
            errors.append(f"Missing required field: '{field}'")
    
    # Check if this is a Melodic Roulette workout
    if workout.get("mode") == "melodic-roulette":
        errors.extend(validate_melodic_roulette(workout))
        return len(errors) == 0, errors
    
    # Must have either 'intervals' (legacy) or 'sequence' (new format)
    has_intervals = "intervals" in workout
    has_sequence = "sequence" in workout
    has_blocks = "blocks" in workout
    
    if not has_intervals and not has_sequence:
        errors.append("Workout must have either 'intervals' or 'sequence' array")
    
    # Validate sequence if present
    if has_sequence:
        if not isinstance(workout["sequence"], list):
            errors.append("'sequence' must be an array")
        else:
            for idx, item in enumerate(workout["sequence"]):
                errors.extend(validate_sequence_item(item, idx))
    
    # Validate legacy intervals if present
    if has_intervals:
        if not isinstance(workout["intervals"], list):
            errors.append("'intervals' must be an array")
        else:
            for idx, interval in enumerate(workout["intervals"]):
                interval_errors = validate_interval(interval, f"intervals[{idx}]")
                errors.extend(interval_errors)
    
    # Validate legacy blocks if present
    if has_blocks:
        if not isinstance(workout["blocks"], list):
            errors.append("'blocks' must be an array")
        else:
            for idx, block in enumerate(workout["blocks"]):
                block_errors = validate_block(block, f"blocks[{idx}]")
                errors.extend(block_errors)
    
    # Validate totalDuration if present
    if "totalDuration" in workout:
        if not isinstance(workout["totalDuration"], int) or workout["totalDuration"] < 1:
            errors.append("totalDuration must be a positive integer")
    
    # Validate theme if present
    if "theme" in workout:
        valid_themes = ["default", "halloween", "christmas", "wintry", "valentines", 
                       "holyhill", "criterium", "custom"]
        if workout["theme"] not in valid_themes:
            errors.append(f"theme must be one of {valid_themes}, got '{workout['theme']}'")
    
    return len(errors) == 0, errors


def validate_workout_file(json_file: Path) -> bool:
    """
    Validate a workout JSON file.
    
    Returns:
        True if valid, False otherwise
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            workout = json.load(f)
        
        is_valid, errors = validate_workout(workout)
        
        if is_valid:
            workout_name = workout.get("name", "Unknown")
            workout_id = workout.get("id", "unknown")
            if workout.get("mode") == "melodic-roulette":
                slot_count = len(workout.get("slots", []))
                block_count = len(workout.get("workBlockDefinitions", []))
                print(f"✓ '{workout_name}' ({workout_id}) is valid - Melodic Roulette: {slot_count} slots, {block_count} work blocks")
            else:
                sequence_count = len(workout.get("sequence", workout.get("intervals", [])))
                print(f"✓ '{workout_name}' ({workout_id}) is valid - {sequence_count} items")
            return True
        else:
            print(f"❌ Validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point for the workout validator."""
    parser = argparse.ArgumentParser(
        description="Validate interval workout JSON files against the schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single workout file
  python validate_workout.py workouts/30min/pyramid-power.json
  
  # Validate all 90min workouts
  python validate_workout.py workouts/90min/*.json
  
  # Validate all workouts
  python validate_workout.py workouts/**/*.json
        """
    )
    
    parser.add_argument(
        "json_files",
        nargs="+",
        type=Path,
        help="Path(s) to JSON workout file(s) to validate"
    )
    
    args = parser.parse_args()
    
    all_valid = True
    for json_file in args.json_files:
        print(f"\nValidating {json_file}:")
        if not validate_workout_file(json_file):
            all_valid = False
    
    if all_valid:
        print(f"\n✓ All {len(args.json_files)} file(s) are valid!")
        sys.exit(0)
    else:
        print(f"\n❌ Some files have validation errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
