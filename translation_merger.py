import os
import json
import argparse
from collections import defaultdict


# Function to get the user's Documents folder in a cross-platform way
def get_documents_folder():
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, 'Documents', 'Translations')

# Ensure output folder exists
def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def merge_translations(base, new):
    """
    Recursively merge the translation strings from 'new' into 'base', 
    but only include keys that already exist in 'base'.
    """
    for key, value in new.items():
        if key in base:  # Only update keys that exist in 'base'
            if isinstance(value, dict) and isinstance(base[key], dict):
                merge_translations(base[key], value)  # Recursive merge for nested dictionaries
            else:
                base[key] = value  # Overwrite with the new translation if it's not a dictionary
    return base

def extract_keys(d, parent_key=''):
    """
    Recursively extract all keys from the dictionary into a flat structure with real keys.
    """
    keys = set()
    for key, value in d.items():
        # Ensure that we only append the full key path if the key changes
        full_key = f"{parent_key}.{key}" if parent_key else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(extract_keys(value, full_key))
    return keys

def check_missing_keys(dict1, dict2, parent_key=None):
    """
    Recursively check for missing keys between two dictionaries.
    """
    missing_keys = []
    for key in dict1:
        full_key = f"{parent_key}.{key}" if parent_key else key
        if key not in dict2:
            missing_keys.append(f"Missing key: {full_key}")
        elif isinstance(dict1[key], dict) and isinstance(dict2.get(key, {}), dict):
            missing_keys.extend(check_missing_keys(dict1[key], dict2[key], full_key))
    return missing_keys

def consolidate_missing_keys(output_folder):
    """
    Consolidate all keys across all files and check which keys are missing from each file.
    """
    files = [f for f in os.listdir(output_folder) if f.endswith('.json')]
    if not files:
        print("No JSON files found in the output folder.")
        return
    
    all_keys = set()
    file_data = {}
    
    # Load all JSON files and extract keys
    for filename in files:
        with open(os.path.join(output_folder, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            file_data[filename] = data
            file_keys = extract_keys(data)
            all_keys.update(file_keys)
    
    # Check which keys are missing from each file and which contain them
    missing_keys_report = []
    
    for filename, data in file_data.items():
        file_keys = extract_keys(data)
        missing_keys = all_keys - file_keys
        if missing_keys:
            missing_keys_report.append(f"File: {filename} is missing the following keys:\n")
            for key in missing_keys:
                present_in_files = [other_filename for other_filename, other_data in file_data.items() if key in extract_keys(other_data)]
                present_files_str = ', '.join(present_in_files)
                missing_keys_report.append(f"{key} (Present in: {present_files_str})")
            missing_keys_report.append('')
    
    # Write the missing keys report to a file
    diff_file_path = os.path.join(output_folder, 'consolidated_missing_keys_report.txt')
    with open(diff_file_path, 'w') as f:
        f.write('\n'.join(missing_keys_report))
    
    print(f"Consolidated missing keys report saved to {diff_file_path}")
    if missing_keys_report:
        print("\n".join(missing_keys_report))
    else:
        print("No missing keys found between files.")

def check_differences(current_folder, output_folder):
    """
    Check for differences between current translations and output files, focusing on missing keys.
    Output a report with missing keys into the output folder.
    Also, print the missing keys to the console.
    """
    differences = []
    
    # Iterate over the files in the output folder
    for filename in os.listdir(output_folder):
        if filename.endswith('.json'):
            current_file_path = os.path.join(current_folder, filename)
            output_file_path = os.path.join(output_folder, filename)
            
            if os.path.exists(current_file_path):
                with open(current_file_path, 'r', encoding='utf-8') as f:
                    current_translations = json.load(f)
                
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    output_translations = json.load(f)
                
                # Check for missing keys in the output files
                missing_keys = check_missing_keys(current_translations, output_translations)
                if missing_keys:
                    differences.append(f"File: {filename}\n" + '\n'.join(missing_keys))
    
    # Write the differences to a text file
    diff_file_path = os.path.join(output_folder, 'missing_keys_report.txt')
    with open(diff_file_path, 'w') as f:
        f.write('\n'.join(differences))
    
    print(f"Missing keys report saved to {diff_file_path}")
    if differences:
        print("\n".join(differences))

def merge_translation_files(current_translations_folder, updated_translations_folder, output_folder):
    """
    Merges all translation files from current_translations folder and updated_translations folder, 
    and saves the result into the output folder.
    """
    ensure_folder_exists(output_folder)
    
    # Get list of JSON files in the current translations folder
    for filename in os.listdir(current_translations_folder):
        if filename.endswith('.json'):
            # Full paths to the files
            current_translations_path = os.path.join(current_translations_folder, filename)
            updated_translations_path = os.path.join(updated_translations_folder, filename)
            
            # Check if the corresponding updated translations file exists
            if os.path.exists(updated_translations_path):
                with open(current_translations_path, 'r', encoding='utf-8') as f:
                    current_translations = json.load(f)
                    
                with open(updated_translations_path, 'r', encoding='utf-8') as f:
                    updated_translations = json.load(f)
                    
                # Merge translations (only update existing keys)
                merged_translations = merge_translations(current_translations, updated_translations)
                
                # Save the merged file to the output folder
                output_path = os.path.join(output_folder, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(merged_translations, f, indent=2, ensure_ascii=False)
                
                print(f"Merged {filename} and saved to {output_path}.")
            else:
                print(f"Updated translations file {filename} not found in {updated_translations_folder}.")

def find_untranslated_keys(current_translations_folder, updated_translations_folder, output_folder):
    """
    Find keys that exist in the current translations but are missing from the updated translations.
    Save a report of untranslated keys.
    """
    ensure_folder_exists(output_folder)
    untranslated_report = []

    # Iterate over the files in the current translations folder
    for filename in os.listdir(current_translations_folder):
        if filename.endswith('.json'):
            current_file_path = os.path.join(current_translations_folder, filename)
            updated_file_path = os.path.join(updated_translations_folder, filename)

            # Check if the corresponding updated translations file exists
            if os.path.exists(updated_file_path):
                with open(current_file_path, 'r', encoding='utf-8') as f:
                    current_translations = json.load(f)

                with open(updated_file_path, 'r', encoding='utf-8') as f:
                    updated_translations = json.load(f)

                # Extract keys from both files
                current_keys = extract_keys(current_translations)
                updated_keys = extract_keys(updated_translations)

                # Find untranslated keys
                untranslated_keys = current_keys - updated_keys

                if untranslated_keys:
                    untranslated_report.append(f"File: {filename} is missing translations for the following keys:\n")
                    untranslated_report.extend(untranslated_keys)
            
            else:
                print(f"Updated translations file {filename} not found in {updated_translations_folder}.")

    # Write the untranslated keys report to a file
    untranslated_report_path = os.path.join(output_folder, 'untranslated_keys_report.txt')
    with open(untranslated_report_path, 'w') as f:
        f.write('\n'.join(untranslated_report))

    print(f"Untranslated keys report saved to {untranslated_report_path}")
    if untranslated_report:
        print("\n".join(untranslated_report))
    else:
        print("No untranslated keys found.")

def find_untranslated_keys_grouped(current_translations_folder, updated_translations_folder, output_folder):
    """
    Find keys that exist in the current translations but are missing from the updated translations.
    Group the keys by how many files they are missing from and save a report.
    """
    ensure_folder_exists(output_folder)
    missing_keys_map = defaultdict(list)

    # Iterate over the files in the current translations folder
    for filename in os.listdir(current_translations_folder):
        if filename.endswith('.json'):
            current_file_path = os.path.join(current_translations_folder, filename)
            updated_file_path = os.path.join(updated_translations_folder, filename)

            # Check if the corresponding updated translations file exists
            if os.path.exists(updated_file_path):
                with open(current_file_path, 'r', encoding='utf-8') as f:
                    current_translations = json.load(f)

                with open(updated_file_path, 'r', encoding='utf-8') as f:
                    updated_translations = json.load(f)

                # Extract keys from both files
                current_keys = extract_keys(current_translations)
                updated_keys = extract_keys(updated_translations)

                # Find untranslated keys
                untranslated_keys = current_keys - updated_keys

                # Group missing keys by file
                for key in untranslated_keys:
                    missing_keys_map[key].append(filename)
            
            else:
                print(f"Updated translations file {filename} not found in {updated_translations_folder}.")

    # Generate the report
    untranslated_report = []
    for key, files in missing_keys_map.items():
        file_list = ', '.join(files)
        untranslated_report.append(f"{key} (has not been translated in: {file_list})")

    # Write the untranslated keys report to a file
    untranslated_report_path = os.path.join(output_folder, 'grouped_untranslated_keys_report.txt')
    with open(untranslated_report_path, 'w') as f:
        f.write('\n'.join(untranslated_report))

    print(f"Grouped untranslated keys report saved to {untranslated_report_path}")
    if untranslated_report:
        print("\n".join(untranslated_report))
    else:
        print("No untranslated keys found.")



def main():
    # Get the default Documents folder path
    default_folder = get_documents_folder()

    # Setup argument parser for easy configuration
    parser = argparse.ArgumentParser(description="Merge translation JSON files from two folders.")
    parser.add_argument('--current_translations', type=str, default=os.path.join(default_folder, 'current_translations'), 
                        help='Path to the current translations folder.')
    parser.add_argument('--updated_translations', type=str, default=os.path.join(default_folder, 'updated_translations'), 
                        help='Path to the updated translations folder.')
    parser.add_argument('--output', type=str, default=os.path.join(default_folder, 'output'), 
                        help='Path to the output folder for merged files.')
    parser.add_argument('--checkdiff', action='store_true', help='Check for missing keys in the output files compared to the current translations.')
    parser.add_argument('--crosscheck', action='store_true', help='Check for missing keys between output translation files.')
    
    args = parser.parse_args()

    current_translations_folder = args.current_translations
    updated_translations_folder = args.updated_translations
    output_folder = args.output

    # Merge the files
    merge_translation_files(current_translations_folder, updated_translations_folder, output_folder)

    #Find the untranslated keys
    find_untranslated_keys(current_translations_folder, updated_translations_folder, output_folder)

    # Find the untranslated keys grouped by how many files they are missing from
    find_untranslated_keys_grouped(current_translations_folder, updated_translations_folder, output_folder)



    # Check for missing keys compared to current translations
    if args.checkdiff:
        check_differences(current_translations_folder, output_folder)
    
    # Consolidate and check for missing keys across translation files
    if args.crosscheck:
        consolidate_missing_keys(output_folder)

if __name__ == "__main__":
    main()
