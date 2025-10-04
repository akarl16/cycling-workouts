#!/usr/bin/env python3
"""
CSV to JSON Converter for Cycling Workouts

This utility converts cycling workout data from CSV format to JSON format
according to the workout-schema.json schema.
"""

import csv
import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List


def convert_value(value: str, field_type: str) -> Any:
    """
    Convert string value to appropriate type based on schema field type.
    
    Args:
        value: String value from CSV
        field_type: Expected type ('string', 'number', 'integer')
    
    Returns:
        Converted value or None if empty
    """
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    
    if field_type == "integer":
        try:
            return int(float(value))
        except ValueError:
            return None
    elif field_type == "number":
        try:
            return float(value)
        except ValueError:
            return None
    else:  # string
        return value


def csv_to_json(csv_file: Path, output_dir: Path = None, single_file: bool = False) -> None:
    """
    Convert CSV file containing workout data to JSON format.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save JSON files (default: workouts/)
        single_file: If True, save all workouts to a single JSON file
    """
    if output_dir is None:
        output_dir = Path("workouts")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Field type mapping based on schema
    field_types = {
        "id": "string",
        "date": "string",
        "duration": "number",
        "distance": "number",
        "avgSpeed": "number",
        "maxSpeed": "number",
        "avgHeartRate": "integer",
        "maxHeartRate": "integer",
        "avgCadence": "integer",
        "maxCadence": "integer",
        "avgPower": "integer",
        "maxPower": "integer",
        "calories": "integer",
        "elevationGain": "number",
        "workoutType": "string",
        "notes": "string"
    }
    
    workouts: List[Dict[str, Any]] = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                workout = {}
                
                for field, value in row.items():
                    field_type = field_types.get(field, "string")
                    converted_value = convert_value(value, field_type)
                    
                    # Only include non-None values
                    if converted_value is not None:
                        workout[field] = converted_value
                
                if workout:  # Only add non-empty workouts
                    workouts.append(workout)
        
        if not workouts:
            print("No workouts found in CSV file.", file=sys.stderr)
            return
        
        if single_file:
            # Save all workouts to a single file
            output_file = output_dir / f"{csv_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(workouts, f, indent=2, ensure_ascii=False)
            print(f"Successfully converted {len(workouts)} workout(s) to {output_file}")
        else:
            # Save each workout to a separate file
            for workout in workouts:
                workout_id = workout.get("id", "unknown")
                output_file = output_dir / f"{workout_id}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(workout, f, indent=2, ensure_ascii=False)
                
                print(f"Converted workout {workout_id} to {output_file}")
            
            print(f"\nSuccessfully converted {len(workouts)} workout(s)")
    
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except csv.Error as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the CSV to JSON converter."""
    parser = argparse.ArgumentParser(
        description="Convert cycling workout data from CSV to JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert CSV to individual JSON files (one per workout)
  python csv_to_json.py workouts.csv
  
  # Convert CSV to a single JSON file containing all workouts
  python csv_to_json.py workouts.csv --single-file
  
  # Specify output directory
  python csv_to_json.py workouts.csv --output-dir ./my-workouts
        """
    )
    
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the CSV file containing workout data"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("workouts"),
        help="Output directory for JSON files (default: workouts/)"
    )
    
    parser.add_argument(
        "-s", "--single-file",
        action="store_true",
        help="Save all workouts to a single JSON file instead of separate files"
    )
    
    args = parser.parse_args()
    
    csv_to_json(args.csv_file, args.output_dir, args.single_file)


if __name__ == "__main__":
    main()
