import configparser
import json
import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Union, Optional

def read_ini_files_to_json(
    ini_files: Union[str, List[str], Path, List[Path]],
    json_path: Union[str, Path],
    flatten_sections: bool = False
) -> Dict[str, Dict]:
    """
    Read multiple INI files and save to JSON format.
    
    Args:
        ini_files: Single file path, directory path, or list of INI file paths
        json_path: Path to save the JSON output
        flatten_sections: If True, flatten sections into single dict with 
                         section.key naming. If False, keep nested structure.
    
    Returns:
        Dictionary containing all INI data
    
    Example:
        >>> data = read_ini_files_to_json('*.ini', 'output.json')
        >>> data = read_ini_files_to_json(['file1.ini', 'file2.ini'], 'output.json')
        >>> data = read_ini_files_to_json('/path/to/directory', 'output.json')
    """
    
    # Convert to list of file paths
    if isinstance(ini_files, (str, Path)):
        ini_files = [Path(ini_files)]
    
    file_paths = []
    for item in ini_files:
        item = Path(item)
        if item.is_dir():
            # If directory, find all .ini and .cfg files
            file_paths.extend(item.glob('*.ini'))
            file_paths.extend(item.glob('*.cfg'))
        elif item.is_file():
            file_paths.append(item)
        elif '*' in str(item):
            # Handle wildcards
            parent = item.parent
            pattern = item.name
            file_paths.extend(parent.glob(pattern))
    
    # Remove duplicates
    file_paths = list(set(file_paths))
    
    if not file_paths:
        raise FileNotFoundError(f"No INI files found matching: {ini_files}")
    
    all_data = {}
    
    for file_path in file_paths:
        try:
            config = configparser.ConfigParser()
            
            # Preserve case sensitivity
            config.optionxform = str
            
            # Read INI file
            config.read(file_path, encoding='utf-8')
            
            file_data = {}
            
            for section in config.sections():
                if flatten_sections:
                    # Flatten sections: section.key = value
                    for key, value in config.items(section):
                        file_data[f"{section}.{key}"] = value
                else:
                    # Nested structure
                    file_data[section] = dict(config.items(section))
            
            # Handle DEFAULT section if exists
            if config.defaults():
                if flatten_sections:
                    for key, value in config.defaults().items():
                        file_data[f"DEFAULT.{key}"] = value
                else:
                    file_data["DEFAULT"] = dict(config.defaults())
            
            # Use filename as key in overall dictionary
            all_data[file_path.name] = file_data
            
            print(f"Read: {file_path.name} ({len(file_data)} {'items' if flatten_sections else 'sections'})")
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {json_path}")
    print(f"Total files processed: {len(all_data)}")
    
    return all_data


def json_to_dataframe(
    json_path: Union[str, Path],
    flatten: bool = True
) -> pd.DataFrame:
    """
    Read JSON file and convert to pandas DataFrame.
    
    Args:
        json_path: Path to JSON file
        flatten: If True, create flattened DataFrame. If False, keep hierarchical structure.
    
    Returns:
        pandas DataFrame
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if flatten:
        # Create flattened DataFrame
        rows = []
        
        for filename, sections in data.items():
            # Handle both flattened and nested structures
            if any('.' in key for key in sections.keys()):
                # Already flattened in JSON
                row = {'filename': filename}
                row.update(sections)
                rows.append(row)
            else:
                # Nested structure - flatten it
                row = {'filename': filename}
                for section, items in sections.items():
                    for key, value in items.items():
                        row[f"{section}.{key}"] = value
                rows.append(row)
        
        df = pd.DataFrame(rows)
        
    else:
        # Create multi-index DataFrame for hierarchical data
        records = []
        
        for filename, sections in data.items():
            if any('.' in key for key in sections.keys()):
                # Already flattened - convert to nested
                nested_data = {}
                for key, value in sections.items():
                    if '.' in key:
                        section, item_key = key.split('.', 1)
                        if section not in nested_data:
                            nested_data[section] = {}
                        nested_data[section][item_key] = value
                    else:
                        if "DEFAULT" not in nested_data:
                            nested_data["DEFAULT"] = {}
                        nested_data["DEFAULT"][key] = value
                sections = nested_data
            
            for section, items in sections.items():
                for key, value in items.items():
                    records.append({
                        'filename': filename,
                        'section': section,
                        'key': key,
                        'value': value
                    })
        
        df = pd.DataFrame(records)
    
    return df


def read_ini_files_to_dataframe(
    ini_files: Union[str, List[str], Path, List[Path]],
    json_path: Optional[Union[str, Path]] = None,
    flatten_sections: bool = False
) -> pd.DataFrame:
    """
    Combined function to read INI files and directly return a DataFrame.
    
    Args:
        ini_files: INI file paths, directory, or pattern
        json_path: Optional JSON path to save intermediate data
        flatten_sections: Whether to flatten section.key structure
    
    Returns:
        pandas DataFrame
    """
    if json_path:
        # Read INI files and save to JSON
        data = read_ini_files_to_json(ini_files, json_path, flatten_sections)
        # Load from JSON to DataFrame
        df = json_to_dataframe(json_path, flatten=True)
    else:
        # Read directly without saving JSON intermediate
        data = read_ini_files_to_json(ini_files, "temp_output.json", flatten_sections)
        df = json_to_dataframe("temp_output.json", flatten=True)
        # Clean up temp file
        os.remove("temp_output.json")
    
    return df


# Example usage
if __name__ == "__main__":
    # Example 1: Read specific INI files and save to JSON
    ini_files = ["quifixj.cfg", "config.ini", "settings.cfg"]
    data = read_ini_files_to_json(ini_files, "output.json", flatten_sections=True)
    
    # Example 2: Read from JSON to DataFrame
    df = json_to_dataframe("output.json")
    print("\nDataFrame shape:", df.shape)
    print("\nDataFrame columns:", df.columns.tolist())
    print("\nFirst few rows:")
    print(df.head())
    
    # Example 3: Direct conversion (without explicit JSON file)
    df_direct = read_ini_files_to_dataframe("*.ini", flatten_sections=True)
    print("\nDirect conversion DataFrame shape:", df_direct.shape)
    
    # Example 4: Process a directory
    # df_dir = read_ini_files_to_dataframe("/path/to/configs/", "configs.json")
    
    # Example 5: Save DataFrame to CSV for analysis
    df.to_csv("ini_analysis.csv", index=False, encoding='utf-8')
    print("\nDataFrame saved to: ini_analysis.csv")
    
    # Display basic info about the DataFrame
    print("\n" + "="*50)
    print("DataFrame Information:")
    print("="*50)
    print(f"Total files: {len(df)}")
    print(f"Total columns (parameters): {len(df.columns) - 1}")  # minus filename column
    
    # Show missing values
    missing = df.isnull().sum().sum()
    print(f"Total missing values: {missing}")
    
    # Show unique sections/keys
    if 'section' in df.columns:
        print(f"Unique sections: {df['section'].nunique()}")
        print(f"Unique keys: {df['key'].nunique()}")