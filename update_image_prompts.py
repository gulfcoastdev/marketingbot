#!/usr/bin/env python3
"""
Update upcoming_holidays_output.json with new image prompts from image_prompts.json
and create a new simplified JSON format.
"""

import json
from datetime import datetime

def load_json(file_path):
    """Load JSON data from file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        # Try to fix and parse partially
        if file_path == 'image_prompts.json':
            return load_partial_json(file_path)
        return None

def load_partial_json(file_path):
    """Try to load partial JSON by fixing common issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to find the last complete entry
        lines = content.split('\n')
        fixed_lines = []
        in_object = False
        brace_count = 0

        for line in lines:
            if '{' in line:
                brace_count += line.count('{')
                in_object = True
            if '}' in line:
                brace_count -= line.count('}')

            fixed_lines.append(line)

            # If we're at the end of a complete object and brace count is reasonable
            if in_object and brace_count <= 1 and '}' in line and ',' not in line.strip():
                break

        # Add closing bracket if needed
        fixed_content = '\n'.join(fixed_lines)
        if not fixed_content.rstrip().endswith(']'):
            if fixed_content.rstrip().endswith(','):
                fixed_content = fixed_content.rstrip()[:-1]  # Remove trailing comma
            fixed_content += '\n]'

        data = json.loads(fixed_content)
        print(f"✅ Loaded partial JSON with {len(data)} entries")
        return data

    except Exception as e:
        print(f"❌ Could not fix JSON: {e}")
        return None

def save_json(data, file_path):
    """Save data to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {file_path}")

def main():
    # Load data files
    print("Loading image prompts...")
    image_prompts = load_json('image_prompts.json')
    if not image_prompts:
        return

    print("Loading upcoming holidays output...")
    holidays_output = load_json('data/output/upcoming_holidays_output.json')
    if not holidays_output:
        return

    # Create lookup dictionary for image prompts
    prompts_by_date = {item['date']: item['image_prompt'] for item in image_prompts}

    # Update upcoming_holidays_output with new image prompts
    updated_count = 0
    holidays_by_date = holidays_output.get('holidays_by_date', {})

    for date, holiday_data in holidays_by_date.items():
        if date in prompts_by_date:
            # Update the image prompt
            holiday_data['image_prompt'] = prompts_by_date[date]
            updated_count += 1
            print(f"  ✅ Updated image prompt for {date}")

    # Update metadata
    holidays_output['updated_at'] = datetime.now().isoformat()
    holidays_output['image_prompts_updated'] = updated_count

    # Save updated holidays output
    save_json(holidays_output, 'data/output/upcoming_holidays_output.json')
    print(f"📊 Updated {updated_count} image prompts in upcoming_holidays_output.json")

    # Create new simplified format
    simplified_data = []

    for date, holiday_data in holidays_by_date.items():
        simplified_entry = {
            "date": date,
            "selected_holiday": holiday_data.get('selected_holiday', ''),
            "image_prompt": holiday_data.get('image_prompt', ''),
            "caption": holiday_data.get('caption', '')
        }
        simplified_data.append(simplified_entry)

    # Sort by date
    simplified_data.sort(key=lambda x: x['date'])

    # Save simplified format
    save_json(simplified_data, 'holidays_simplified.json')
    print(f"📄 Created simplified format with {len(simplified_data)} entries")

    # Show summary
    print(f"\n📋 Summary:")
    print(f"  • Image prompts loaded: {len(image_prompts)}")
    print(f"  • Holiday entries in output: {len(holidays_by_date)}")
    print(f"  • Image prompts updated: {updated_count}")
    print(f"  • Simplified entries created: {len(simplified_data)}")

if __name__ == "__main__":
    main()