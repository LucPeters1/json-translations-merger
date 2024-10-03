# JSON-Translation Merger & Diff Checker

This Python script is designed to merge JSON translation files from two folders (current and updated translations) and provide reports on missing translation keys. The script identifies untranslated keys, checks for differences between translation files, and generates a concise report for missing translations across multiple languages.

## Features

* Merge Translations: Merge updated translations into current translations, ensuring only existing keys in the current translations are updated.
* Find Untranslated Keys: Detect keys that exist in the current translations but are missing in the updated translations.
* Grouped Missing Keys Report: Consolidate and group missing keys across multiple translation files, indicating in which files a key is missing.
* Cross-Check Translations: Compare translations between all output files (e.g., between en.json and fr.json), identifying missing keys in any language files.
* Missing Key Detection: Generate a detailed report listing which files are missing specific keys compared to the current translations or across all output files.

## Prerequisites
* Python 3+
* Json translation files

## Installation
1. Clone this repo to your local machine:
```bash
  git clone https://github.com/LucPeters1/json-translations-merger.git
  cd json-translations-merger
```
    
## Folder Structure

```bash
json-translations-merger/
├── current_translations/        # Current translations with existing keys
│   ├── en.json
│   ├── fr.json
│   └── ...
├── updated_translations/        # Updated translations to merge into current translations
│   ├── en.json
│   ├── fr.json
│   └── ...
└── output/                      # Output folder for merged files and reports
    └── (Generated merged files and reports are saved here)
```

## Usage
The script offers several functionalities, from merging translation files to checking for missing keys and generating detailed reports.

## Command-line Options

| Argument | Description | Default path |
| ----------- | ----------- | ----------- |
| `--current_translations` | Path to the current translations folder. | `~/Documents/Translations/current_translations` |
| `--updated-translations` | Path to the current translations folder. | `~/Documents/Translations/updated_translations` |
| `--output` | Path to the output folder where merged files and reports will be saved. | `~/Documents/Translations/output` |
| `--checkdiff` | Check for missing keys between current translations and the output.	 | N/A |
| `--crosscheck` | Cross-check missing keys across all output files.	 | N/A |


## Basic Merge example
```bash
python3 translation_merger.py --current_translations /path/to/current_translations --updated_translations /path/to/updated_translations --output /path/to/output
```

## Find untranslated keys
To find keys that exist in the `current_translations` but are missing in `updated_translations`:

```bash
python3 translation_merger.py --current_translations /path/to/current_translations --updated_translations /path/to/updated_translations --output /path/to/output
```

This generates a report `untranslated_keys_report.txt` in the `output` folder, listing the missing keys per file.

## Group Missing Keys by File
To group missing keys across multiple files, showing which translation files are missing which keys:

```bash
python3 translation_merger.py --current_translations /path/to/current_translations --updated_translations /path/to/updated_translations --output /path/to/output
```

## Check Difference Between Files
To check for missing keys between `current_translations` and the `output` files:
```bash
python3 translation_merger.py --current_translations /path/to/current_translations --updated_translations /path/to/updated_translations --output /path/to/output --checkdiff
```
This will output a `missing_keys_report.txt` with all missing keys between the `current_translations` and `output` files.

## Cross-Check Missing Keys Across All Files
To cross-check keys across all output translation files (e.g., check if `en.json`, `fr.json`, etc. have missing keys):
```bash
python3 translation_merger.py --current_translations /path/to/current_translations --updated_translations /path/to/updated_translations --output /path/to/output --crosscheck
```
