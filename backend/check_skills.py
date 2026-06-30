import json
import os
import re
import sys

def main():
    # Attempt to locate paths intelligently
    base_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(base_dir, "Questions")
    frontend_dir = os.path.join(os.path.dirname(base_dir), "frontend", "src", "pages", "CustomAssessment.js")

    if not os.path.exists(questions_dir):
        print(f"Questions directory not found at: {questions_dir}")
        sys.exit(1)

    if not os.path.exists(frontend_dir):
        print(f"Frontend JS not found at: {frontend_dir}")
        sys.exit(1)

    # 1. Extract frontend canonical skills
    skills = set()
    with open(frontend_dir, 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find("const subRoleSkills = useMemo(() => ({")
    if start_idx == -1:
        print("Could not find subRoleSkills base object!")
        sys.exit(1)

    end_idx = content.find("}), []);", start_idx)
    sub_role_block = content[start_idx:end_idx]

    arrays = re.findall(r"\[(.*?)\]", sub_role_block)
    for arr in arrays:
        items = re.findall(r"'([^']+)'", arr)
        for item in items:
            skills.add(item.strip())

    print(f"Found {len(skills)} canonical skills from frontend CustomAssessment.js")

    def normalize(s):
        if not s:
            return ""
        return s.lower().replace(" ", "").replace("-", "").replace("/", "").replace("_", "")

    canon_map = {normalize(ks): ks for ks in skills}

    files = [f for f in os.listdir(questions_dir) if f.endswith('.json')]
    print(f"Scanning {len(files)} JSON files in {questions_dir}...")

    updated_files = 0
    renamed_files = 0
    skipped_files = 0
    unmapped = []

    for filename in files:
        filepath = os.path.join(questions_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

        old_skill = data.get("skill", "")
        base_name = filename.replace(".json", "")

        norm_sk = normalize(old_skill)
        norm_fn = normalize(base_name)

        target_sk = None

        if old_skill in skills:
            target_sk = old_skill
        elif base_name in skills:
            target_sk = base_name
        else:
            if norm_sk in canon_map:
                target_sk = canon_map[norm_sk]
            elif norm_fn in canon_map:
                target_sk = canon_map[norm_fn]

        if not target_sk:
            unmapped.append(f"{filename} (Internal skill: '{old_skill}')")
            skipped_files += 1
            continue

        needs_save = False
        if old_skill != target_sk:
            data["skill"] = target_sk
            needs_save = True

        safe_filename = target_sk.replace("/", "_").replace(":", "-") + ".json"
        
        if safe_filename != filename:
            new_filepath = os.path.join(questions_dir, safe_filename)
            
            if needs_save:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                needs_save = False
            
            if os.path.exists(new_filepath) and new_filepath.lower() != filepath.lower():
                print(f"[Warning] Cannot rename {filename} to {safe_filename} because it already exists.")
            else:
                os.rename(filepath, new_filepath)
                renamed_files += 1
                filepath = new_filepath

        if needs_save:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            updated_files += 1

    print("\n--- Summary ---")
    print(f"Files updated (JSON inner 'skill' modified): {updated_files}")
    print(f"Files renamed: {renamed_files}")
    print(f"Files unmapped/skipped: {skipped_files}")

    if unmapped:
        print("\nCould not automatically map the following files to CustomAssessment.js skills:")
        for u in unmapped:
            print(f"  - {u}")

if __name__ == '__main__':
    main()
