Here's an enhanced Python solution that reads INI/CFG files and replaces placeholders with values from a properties file before saving to JSON and converting to DataFrame:

```python
import configparser
import json
import pandas as pd
import os
import re
from pathlib import Path
from typing import List, Dict, Union, Optional, Any

def load_properties(file_path: Union[str, Path]) -> Dict[str, str]:
    """
    Load properties from a .properties file.
    
    Args:
        file_path: Path to .properties file
        
    Returns:
        Dictionary of key-value pairs
    """
    properties = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Handle multiline values (ending with \)
            while line.endswith('\\'):
                next_line = next(f, '').strip()
                line = line.rstrip('\\') + next_line
            
            # Split on first '=' or ':'
            if '=' in line:
                key, value = line.split('=', 1)
            elif ':' in line:
                key, value = line.split(':', 1)
            else:
                print(f"Warning: Line {line_num} has no delimiter: {line}")
                continue
            
            key = key.strip()
            value = value.strip()
            
            # Remove surrounding quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            properties[key] = value
    
    return properties

def replace_placeholders(value: str, properties: Dict[str, str]) -> str:
    """
    Replace placeholders in a string with values from properties.
    
    Args:
        value: String potentially containing placeholders
        properties: Dictionary of key-value replacements
        
    Returns:
        String with placeholders replaced
    """
    if not isinstance(value, str):
        return value
    
    # Pattern for placeholders: ${key} or {key} or %key%
    patterns = [
        r'\$\{([^}]+)\}',  # ${key}
        r'\{([^}]+)\}',    # {key}
        r'%([^%]+)%',      # %key%
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, value)
        for key in matches:
            if key in properties:
                replacement = properties[key]
                # Replace all occurrences
                if pattern == r'\$\{([^}]+)\}':
                    value = value.replace(f'${{{key}}}', replacement)
                elif pattern == r'\{([^}]+)\}':
                    value = value.replace(f'{{{key}}}', replacement)
                elif pattern == r'%([^%]+)%':
                    value = value.replace(f'%{key}%', replacement)
    
    return value

def process_config_value(value: Any, properties: Dict[str, str]) -> Any:
    """
    Process a configuration value, replacing placeholders if it's a string.
    
    Args:
        value: Configuration value (could be string, list, etc.)
        properties: Dictionary of key-value replacements
        
    Returns:
        Processed value
    """
    if isinstance(value, str):
        return replace_placeholders(value, properties)
    elif isinstance(value, dict):
        return {k: process_config_value(v, properties) for k, v in value.items()}
    elif isinstance(value, list):
        return [process_config_value(item, properties) for item in value]
    else:
        return value

def read_ini_files_with_properties(
    ini_files: Union[str, List[str], Path, List[Path]],
    properties_file: Union[str, Path],
    json_path: Union[str, Path],
    flatten_sections: bool = False,
    replace_placeholders_flag: bool = True
) -> Dict[str, Dict]:
    """
    Read multiple INI files, replace placeholders with properties, and save to JSON.
    
    Args:
        ini_files: INI file paths, directory, or pattern
        properties_file: Path to .properties file
        json_path: Path to save JSON output
        flatten_sections: Flatten sections into single dict
        replace_placeholders_flag: Whether to replace placeholders
        
    Returns:
        Dictionary containing all processed INI data
    """
    # Load properties
    properties = load_properties(properties_file)
    print(f"Loaded {len(properties)} properties from {properties_file}")
    
    # Convert to list of file paths
    if isinstance(ini_files, (str, Path)):
        ini_files = [Path(ini_files)]
    
    file_paths = []
    for item in ini_files:
        item = Path(item)
        if item.is_dir():
            file_paths.extend(item.glob('*.ini'))
            file_paths.extend(item.glob('*.cfg'))
        elif item.is_file():
            file_paths.append(item)
        elif '*' in str(item):
            parent = item.parent
            pattern = item.name
            file_paths.extend(parent.glob(pattern))
    
    file_paths = list(set(file_paths))
    
    if not file_paths:
        raise FileNotFoundError(f"No INI files found matching: {ini_files}")
    
    all_data = {}
    replacement_stats = {
        'total_replacements': 0,
        'files_with_replacements': 0,
        'keys_with_placeholders': 0
    }
    
    for file_path in file_paths:
        try:
            config = configparser.ConfigParser()
            config.optionxform = str  # Preserve case
            
            config.read(file_path, encoding='utf-8')
            
            file_data = {}
            file_replacements = 0
            
            for section in config.sections():
                section_dict = {}
                for key, value in config.items(section):
                    original_value = value
                    
                    if replace_placeholders_flag:
                        value = process_config_value(value, properties)
                    
                    section_dict[key] = value
                    
                    # Track replacements
                    if replace_placeholders_flag and value != original_value:
                        file_replacements += 1
                        replacement_stats['keys_with_placeholders'] += 1
                        print(f"  Replaced in {file_path.name}: {section}.{key}")
                        print(f"    Original: {original_value}")
                        print(f"    New: {value}")
                
                if flatten_sections:
                    for key, value in section_dict.items():
                        file_data[f"{section}.{key}"] = value
                else:
                    file_data[section] = section_dict
            
            # Handle DEFAULT section
            if config.defaults():
                default_dict = {}
                for key, value in config.defaults().items():
                    original_value = value
                    
                    if replace_placeholders_flag:
                        value = process_config_value(value, properties)
                    
                    default_dict[key] = value
                    
                    if replace_placeholders_flag and value != original_value:
                        file_replacements += 1
                        replacement_stats['keys_with_placeholders'] += 1
                
                if flatten_sections:
                    for key, value in default_dict.items():
                        file_data[f"DEFAULT.{key}"] = value
                else:
                    file_data["DEFAULT"] = default_dict
            
            # Add metadata about replacements
            if replace_placeholders_flag and file_replacements > 0:
                file_data["__metadata__"] = {
                    "replacements_count": file_replacements,
                    "original_file": str(file_path)
                }
                replacement_stats['files_with_replacements'] += 1
                replacement_stats['total_replacements'] += file_replacements
            
            all_data[file_path.name] = file_data
            
            print(f"Read: {file_path.name} (sections: {len(config.sections())}, "
                  f"replacements: {file_replacements})")
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'data': all_data,
            'properties_used': properties if len(properties) < 100 else {"count": len(properties)},
            'replacement_stats': replacement_stats,
            'metadata': {
                'ini_files_processed': len(all_data),
                'properties_file': str(properties_file),
                'timestamp': pd.Timestamp.now().isoformat()
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {json_path}")
    print(f"Files processed: {len(all_data)}")
    print(f"Total replacements: {replacement_stats['total_replacements']}")
    print(f"Files with replacements: {replacement_stats['files_with_replacements']}")
    
    return all_data

def json_to_dataframe_with_properties(
    json_path: Union[str, Path],
    include_metadata: bool = False,
    flatten: bool = True
) -> pd.DataFrame:
    """
    Read JSON file (with properties replacements) and convert to DataFrame.
    
    Args:
        json_path: Path to JSON file
        include_metadata: Whether to include metadata columns
        flatten: Create flattened DataFrame
        
    Returns:
        pandas DataFrame
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract actual data and metadata
    config_data = data.get('data', data)  # Handle both old and new format
    metadata = data.get('metadata', {})
    properties = data.get('properties_used', {})
    
    if flatten:
        rows = []
        
        for filename, sections in config_data.items():
            # Skip metadata keys
            if filename == "__metadata__" or isinstance(sections, dict) and "__metadata__" in sections:
                continue
            
            row = {'filename': filename}
            
            # Handle nested structure
            if any('.' in key for key in sections.keys() if isinstance(sections, dict)):
                # Already flattened
                for key, value in sections.items():
                    if key != "__metadata__":
                        row[key] = value
            else:
                # Nested structure - flatten it
                for section, items in sections.items():
                    if section != "__metadata__":
                        for key, value in items.items():
                            row[f"{section}.{key}"] = value
            
            # Add metadata if requested
            if include_metadata:
                row['_properties_file'] = metadata.get('properties_file', '')
                row['_processed_timestamp'] = metadata.get('timestamp', '')
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
    else:
        # Create long format DataFrame
        records = []
        
        for filename, sections in config_data.items():
            if filename == "__metadata__":
                continue
            
            if any('.' in key for key in sections.keys() if isinstance(sections, dict)):
                # Already flattened - convert to nested for long format
                for key, value in sections.items():
                    if key == "__metadata__":
                        continue
                    if '.' in key:
                        section, item_key = key.split('.', 1)
                        records.append({
                            'filename': filename,
                            'section': section,
                            'key': item_key,
                            'value': value,
                            'has_placeholder': '${' in str(value) or '{' in str(value) or '%' in str(value)
                        })
                    else:
                        records.append({
                            'filename': filename,
                            'section': 'DEFAULT',
                            'key': key,
                            'value': value,
                            'has_placeholder': '${' in str(value) or '{' in str(value) or '%' in str(value)
                        })
            else:
                # Nested structure
                for section, items in sections.items():
                    if section == "__metadata__":
                        continue
                    for key, value in items.items():
                        records.append({
                            'filename': filename,
                            'section': section,
                            'key': key,
                            'value': value,
                            'has_placeholder': '${' in str(value) or '{' in str(value) or '%' in str(value)
                        })
        
        df = pd.DataFrame(records)
    
    return df, metadata, properties

def analyze_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze which values still contain placeholders after replacement.
    
    Args:
        df: DataFrame with configuration data
        
    Returns:
        DataFrame with placeholder analysis
    """
    placeholder_patterns = [
        r'\$\{[^}]+\}',
        r'\{[^}]+\}(?!\})',  # Exclude nested
        r'%[^%]+%'
    ]
    
    def contains_placeholder(value):
        if not isinstance(value, str):
            return False
        for pattern in placeholder_patterns:
            if re.search(pattern, value):
                return True
        return False
    
    # Find rows with placeholders
    placeholder_rows = []
    
    if 'value' in df.columns:  # Long format
        for idx, row in df.iterrows():
            if contains_placeholder(row['value']):
                placeholder_rows.append({
                    'filename': row['filename'],
                    'section': row.get('section', ''),
                    'key': row.get('key', ''),
                    'value': row['value'],
                    'placeholder_type': 'unknown'
                })
    else:  # Wide format
        for idx, row in df.iterrows():
            for col in df.columns:
                if col != 'filename' and isinstance(row[col], str):
                    if contains_placeholder(row[col]):
                        placeholder_rows.append({
                            'filename': row['filename'],
                            'parameter': col,
                            'value': row[col],
                            'placeholder_type': 'unknown'
                        })
    
    placeholder_df = pd.DataFrame(placeholder_rows)
    
    if not placeholder_df.empty:
        # Extract placeholder keys
        def extract_placeholder_keys(value):
            keys = []
            patterns = [
                (r'\$\{([^}]+)\}', '${}'),
                (r'\{([^}]+)\}', '{}'),
                (r'%([^%]+)%', '%%')
            ]
            for pattern, fmt in patterns:
                matches = re.findall(pattern, value)
                for match in matches:
                    keys.append(fmt.format(match))
            return ', '.join(keys)
        
        placeholder_df['placeholder_keys'] = placeholder_df['value'].apply(extract_placeholder_keys)
    
    return placeholder_df

# Main workflow function
def process_config_files_with_properties(
    ini_files: Union[str, List[str], Path, List[Path]],
    properties_file: Union[str, Path],
    output_dir: Union[str, Path] = "output",
    flatten_sections: bool = True,
    analyze_unresolved: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Complete workflow: Process INI files with properties and generate outputs.
    
    Args:
        ini_files: INI/CFG files to process
        properties_file: .properties file for replacements
        output_dir: Directory to save outputs
        flatten_sections: Whether to flatten sections
        analyze_unresolved: Analyze unresolved placeholders
        
    Returns:
        Dictionary of DataFrames
    """
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Define output paths
    json_path = output_dir / "configs_with_properties.json"
    csv_path = output_dir / "configs_flat.csv"
    excel_path = output_dir / "configs_analysis.xlsx"
    
    # Step 1: Read INI files and apply property replacements
    print("=" * 60)
    print("Step 1: Reading INI files and applying property replacements")
    print("=" * 60)
    data = read_ini_files_with_properties(
        ini_files=ini_files,
        properties_file=properties_file,
        json_path=json_path,
        flatten_sections=flatten_sections,
        replace_placeholders_flag=True
    )
    
    # Step 2: Convert to DataFrame
    print("\n" + "=" * 60)
    print("Step 2: Converting to DataFrame")
    print("=" * 60)
    df_flat, metadata, properties = json_to_dataframe_with_properties(
        json_path=json_path,
        flatten=True
    )
    
    print(f"DataFrame shape: {df_flat.shape}")
    print(f"Files: {len(df_flat)}")
    print(f"Parameters: {len(df_flat.columns) - 1}")
    
    # Step 3: Save to CSV
    df_flat.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nFlattened data saved to: {csv_path}")
    
    # Step 4: Create long format for analysis
    df_long, _, _ = json_to_dataframe_with_properties(
        json_path=json_path,
        flatten=False
    )
    
    # Step 5: Analyze unresolved placeholders
    if analyze_unresolved:
        print("\n" + "=" * 60)
        print("Step 3: Analyzing unresolved placeholders")
        print("=" * 60)
        unresolved_df = analyze_placeholders(df_long)
        
        if not unresolved_df.empty:
            print(f"Found {len(unresolved_df)} unresolved placeholders:")
            print(unresolved_df[['filename', 'parameter' if 'parameter' in unresolved_df.columns else 'key', 
                                'placeholder_keys']].to_string(index=False))
            
            unresolved_csv = output_dir / "unresolved_placeholders.csv"
            unresolved_df.to_csv(unresolved_csv, index=False)
            print(f"Unresolved placeholders saved to: {unresolved_csv}")
        else:
            print("All placeholders were successfully resolved!")
    
    # Step 6: Create Excel with multiple sheets
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_flat.to_excel(writer, sheet_name='Flat_Configs', index=False)
        df_long.to_excel(writer, sheet_name='Long_Format', index=False)
        
        # Add properties sheet
        if properties:
            if isinstance(properties, dict) and 'count' not in properties:
                props_df = pd.DataFrame(list(properties.items()), columns=['Key', 'Value'])
                props_df.to_excel(writer, sheet_name='Properties', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Files Processed', 'Total Parameters', 'Properties Used', 
                      'Total Rows (Flat)', 'Total Rows (Long)'],
            'Value': [len(df_flat), len(df_flat.columns) - 1, len(properties) if isinstance(properties, dict) else 0,
                     len(df_flat), len(df_long)]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        if 'unresolved_df' in locals() and not unresolved_df.empty:
            unresolved_df.to_excel(writer, sheet_name='Unresolved', index=False)
    
    print(f"\nComplete analysis saved to: {excel_path}")
    
    # Step 7: Generate report
    report_path = output_dir / "processing_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("CONFIGURATION FILE PROCESSING REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Properties file: {properties_file}\n")
        f.write(f"INI files processed: {len(df_flat)}\n")
        f.write(f"Total unique parameters: {len(df_flat.columns) - 1}\n")
        f.write(f"Properties loaded: {len(properties) if isinstance(properties, dict) else 0}\n")
        f.write(f"Processing timestamp: {metadata.get('timestamp', 'N/A')}\n")
        
        if 'unresolved_df' in locals():
            f.write(f"\nUnresolved placeholders: {len(unresolved_df)}\n")
    
    print(f"Processing report saved to: {report_path}")
    
    return {
        'df_flat': df_flat,
        'df_long': df_long,
        'metadata': metadata,
        'properties': properties,
        'unresolved': unresolved_df if 'unresolved_df' in locals() else None
    }

# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    result = process_config_files_with_properties(
        ini_files=["quifixj.cfg", "config.ini", "settings.cfg"],
        properties_file="all.properties",
        output_dir="config_analysis",
        flatten_sections=True
    )
    
    # Access the DataFrames
    df_flat = result['df_flat']
    df_long = result['df_long']
    
    print("\n" + "=" * 60)
    print("DATA ANALYSIS")
    print("=" * 60)
    
    # Show sample of flat data
    print("\nSample of flat data (first 3 files, first 5 parameters):")
    sample_columns = ['filename'] + df_flat.columns[1:6].tolist() if len(df_flat.columns) > 6 else df_flat.columns.tolist()
    print(df_flat[sample_columns].head(3).to_string(index=False))
    
    # Show unique sections in long format
    if 'section' in df_long.columns:
        print(f"\nUnique sections across all files: {df_long['section'].nunique()}")
        print(f"Most common sections:")
        print(df_long['section'].value_counts().head(10))
    
    # Example 2: Process directory with wildcard
    # result2 = process_config_files_with_properties(
    #     ini_files="*.cfg",
    #     properties_file="all.properties",
    #     output_dir="cfg_analysis"
    # )
    
    # Example 3: Just replace placeholders without full analysis
    # data = read_ini_files_with_properties(
    #     ini_files="configs/*.ini",
    #     properties_file="all.properties",
    #     json_path="replaced_configs.json"
    # )
```

This enhanced solution provides:

## Key Features:

1. **Properties File Support**: Loads key-value pairs from `all.properties` file
2. **Placeholder Replacement**: Replaces `${key}`, `{key}`, or `%key%` placeholders in INI values
3. **Multiple Output Formats**:
   - JSON with replaced values
   - Flattened DataFrame (wide format)
   - Long format DataFrame for analysis
   - CSV and Excel exports
4. **Placeholder Analysis**: Identifies unresolved placeholders
5. **Metadata Tracking**: Tracks what was replaced and when

## Example Properties File (`all.properties`):
```properties
# Database configuration
db.host=localhost
db.port=5432
db.name=production_db

# Server configuration
server.url=https://api.example.com
server.timeout=30

# Feature flags
feature.enabled=true
```

## Example INI File with Placeholders:
```ini
[database]
host = ${db.host}
port = ${db.port}
name = ${db.name}
connection_string = jdbc:postgresql://${db.host}:${db.port}/${db.name}

[server]
api_url = ${server.url}/api/v1
timeout = ${server.timeout}

[features]
new_ui = ${feature.enabled}
```

## Outputs Generated:

1. **configs_with_properties.json** - All configs with placeholders replaced
2. **configs_flat.csv** - Wide format DataFrame
3. **configs_analysis.xlsx** - Multi-sheet Excel file with:
   - Flat_Configs: Wide format
   - Long_Format: Detailed view
   - Properties: Properties used
   - Summary: Processing statistics
   - Unresolved: Any placeholders not found
4. **processing_report.txt** - Summary report

## Usage Examples:

```python
# 1. Process specific files
result = process_config_files_with_properties(
    ini_files=["file1.cfg", "file2.ini"],
    properties_file="all.properties",
    output_dir="analysis"
)

# 2. Process directory
result = process_config_files_with_properties(
    ini_files="/path/to/configs/",
    properties_file="all.properties",
    output_dir="config_analysis"
)

# 3. Use wildcard
result = process_config_files_with_properties(
    ini_files="*.cfg",
    properties_file="all.properties",
    output_dir="cfg_output"
)

# 4. Access individual components
df_flat = result['df_flat']  # Wide format DataFrame
df_long = result['df_long']  # Long format DataFrame
properties = result['properties']  # Properties used
unresolved = result['unresolved']  # Unresolved placeholders

# 5. Manual processing (without full workflow)
data = read_ini_files_with_properties(
    ini_files="*.ini",
    properties_file="all.properties",
    json_path="output.json"
)

df, metadata, props = json_to_dataframe_with_properties("output.json")
```

## The solution handles:
- Multiple placeholder formats (${key}, {key}, %key%)
- Multiline values in properties files
- Comments and empty lines in properties files
- Case-sensitive keys
- Tracking of what was replaced
- Analysis of unresolved placeholders
- Multiple output formats for different use cases