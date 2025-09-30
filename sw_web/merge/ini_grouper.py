import json
import configparser
import os
from pathlib import Path

def load_and_group_ini_files(directory='.', output_file='grouped_sessions.json'):
    """
    Load all INI files from a directory and group them by category.
    
    Args:
        directory: Directory containing the .ini files (default: current directory)
        output_file: Path to the output JSON file
    """
    # Dictionary to store grouped sessions
    grouped_sessions = {
        'client': {},
        'DROP_COPY': {}
    }
    
    # Get all .ini files in the directory
    ini_files = list(Path(directory).glob('*.ini'))
    
    if not ini_files:
        print(f"No .ini files found in {directory}")
        return
    
    print(f"Found {len(ini_files)} INI files")
    
    # Process each INI file
    for ini_file in ini_files:
        try:
            config = configparser.ConfigParser()
            config.read(ini_file)
            
            # Get the session name from filename (without extension)
            session_name = ini_file.stem
            
            # Convert INI to dictionary
            session_data = {}
            category = None
            
            for section in config.sections():
                session_data[section] = {}
                
                for key, value in config.items(section):
                    # Try to convert numeric values
                    try:
                        session_data[section][key] = int(value)
                    except ValueError:
                        try:
                            session_data[section][key] = float(value)
                        except ValueError:
                            session_data[section][key] = value
                
                # Check if this section has a category field
                if 'category' in session_data[section]:
                    category = session_data[section]['category']
            
            # Group by category
            if category and category in grouped_sessions:
                grouped_sessions[category][session_name] = session_data
                print(f"  ✓ {session_name} -> {category}")
            else:
                # If no category found or unknown category, log it
                if category:
                    print(f"  ⚠ {session_name} has unknown category: {category}")
                    # Create a new category for unknown ones
                    if category not in grouped_sessions:
                        grouped_sessions[category] = {}
                    grouped_sessions[category][session_name] = session_data
                else:
                    print(f"  ⚠ {session_name} has no category field")
        
        except Exception as e:
            print(f"  ✗ Error processing {ini_file.name}: {e}")
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(grouped_sessions, f, indent=2)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"{'='*50}")
    for category, sessions in grouped_sessions.items():
        print(f"{category}: {len(sessions)} sessions")
    print(f"\nOutput written to: {output_file}")

if __name__ == "__main__":
    # You can specify a different directory if needed
    # load_and_group_ini_files(directory='/path/to/ini/files')
    load_and_group_ini_files()
