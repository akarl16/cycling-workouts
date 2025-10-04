#!/usr/bin/env python3
"""
JSON Validator for Cycling Workouts

This utility validates cycling workout JSON files against the workout-schema.json schema.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any


def validate_required_fields(workout: Dict[str, Any]) -> list:
    """
    Validate that all required fields are present.
    
    Args:
        workout: Workout data dictionary
    
    Returns:
        List of missing required fields
    """
    required_fields = ["id", "date", "duration", "distance"]
    missing = [field for field in required_fields if field not in workout]
    return missing


def validate_field_types(workout: Dict[str, Any]) -> list:
    """
    Validate field types match the schema.
    
    Args:
        workout: Workout data dictionary
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Define expected types
    string_fields = ["id", "date", "workoutType", "notes"]
    number_fields = ["duration", "distance", "avgSpeed", "maxSpeed", "elevationGain"]
    integer_fields = ["avgHeartRate", "maxHeartRate", "avgCadence", "maxCadence", 
                      "avgPower", "maxPower", "calories"]
    
    for field, value in workout.items():
        if field in string_fields and not isinstance(value, str):
            errors.append(f"Field '{field}' should be a string, got {type(value).__name__}")
        elif field in number_fields and not isinstance(value, (int, float)):
            errors.append(f"Field '{field}' should be a number, got {type(value).__name__}")
        elif field in integer_fields and not isinstance(value, int):
            errors.append(f"Field '{field}' should be an integer, got {type(value).__name__}")
    
    return errors


def validate_field_values(workout: Dict[str, Any]) -> list:
    """
    Validate field values meet constraints.
    
    Args:
        workout: Workout data dictionary
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Numeric fields that should be >= 0
    positive_fields = ["duration", "distance", "avgSpeed", "maxSpeed", "avgHeartRate", 
                       "maxHeartRate", "avgCadence", "maxCadence", "avgPower", 
                       "maxPower", "calories", "elevationGain"]
    
    for field in positive_fields:
        if field in workout and workout[field] < 0:
            errors.append(f"Field '{field}' should be >= 0, got {workout[field]}")
    
    # Validate workout type enum
    if "workoutType" in workout:
        valid_types = ["recovery", "endurance", "tempo", "threshold", "interval", "race", "other"]
        if workout["workoutType"] not in valid_types:
            errors.append(f"Field 'workoutType' should be one of {valid_types}, got '{workout['workoutType']}'")
    
    return errors


def validate_json_file(json_file: Path) -> bool:
    """
    Validate a single JSON workout file.
    
    Args:
        json_file: Path to JSON file
    
    Returns:
        True if valid, False otherwise
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            workout = json.load(f)
        
        # Check if it's a list of workouts or a single workout
        workouts = workout if isinstance(workout, list) else [workout]
        
        all_valid = True
        for idx, w in enumerate(workouts):
            prefix = f"Workout {idx + 1}: " if len(workouts) > 1 else ""
            
            # Validate required fields
            missing = validate_required_fields(w)
            if missing:
                print(f"❌ {prefix}Missing required fields: {', '.join(missing)}")
                all_valid = False
            
            # Validate field types
            type_errors = validate_field_types(w)
            for error in type_errors:
                print(f"❌ {prefix}{error}")
                all_valid = False
            
            # Validate field values
            value_errors = validate_field_values(w)
            for error in value_errors:
                print(f"❌ {prefix}{error}")
                all_valid = False
            
            if not missing and not type_errors and not value_errors:
                workout_id = w.get("id", "unknown")
                print(f"✓ {prefix}Workout '{workout_id}' is valid")
        
        return all_valid
    
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
    """Main entry point for the JSON validator."""
    parser = argparse.ArgumentParser(
        description="Validate cycling workout JSON files against the schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single workout file
  python validate_json.py workouts/workout-001.json
  
  # Validate all workouts in a directory
  python validate_json.py workouts/*.json
  
  # Validate a file containing an array of workouts
  python validate_json.py all-workouts.json
        """
    )
    
    parser.add_argument(
        "json_files",
        nargs="+",
        type=Path,
        help="Path(s) to JSON file(s) to validate"
    )
    
    args = parser.parse_args()
    
    all_valid = True
    for json_file in args.json_files:
        print(f"\nValidating {json_file}:")
        if not validate_json_file(json_file):
            all_valid = False
    
    if all_valid:
        print(f"\n✓ All {len(args.json_files)} file(s) are valid!")
        sys.exit(0)
    else:
        print(f"\n❌ Some files have validation errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
