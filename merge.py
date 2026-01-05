import json
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = "UUIDHERE.json"

def parse_timestamp(value):
    # PaperMC timestamp format: YYYY-MM-DD HH:MM:SS +0800
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
    except Exception:
        return None

def pick_newer(a, b):
    ta = parse_timestamp(a)
    tb = parse_timestamp(b)

    if ta and tb:
        return a if ta > tb else b
    return a or b

def merge_advancement_files(files):
    merged = {}
    highest_data_version = 0

    for filename in files:
        path = os.path.join(SCRIPT_DIR, filename)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Preserve highest DataVersion
        dv = data.get("DataVersion")
        if isinstance(dv, int):
            highest_data_version = max(highest_data_version, dv)

        for key, value in data.items():
            if key == "DataVersion" or not isinstance(value, dict):
                continue

            merged.setdefault(key, {
                "criteria": {},
                "done": False
            })

            if isinstance(value.get("done"), bool):
                merged[key]["done"] |= value["done"]

            criteria = value.get("criteria")
            if isinstance(criteria, dict):
                for criterion, timestamp in criteria.items():
                    if criterion in merged[key]["criteria"]:
                        merged[key]["criteria"][criterion] = pick_newer(
                            merged[key]["criteria"][criterion],
                            timestamp
                        )
                    else:
                        merged[key]["criteria"][criterion] = timestamp

    if highest_data_version > 0:
        merged["DataVersion"] = highest_data_version

    return merged

if __name__ == "__main__":
    json_files = [
        f for f in os.listdir(SCRIPT_DIR)
        if f.endswith(".json") and f != OUTPUT_FILE
    ]

    if not json_files:
        print("No advancement JSON files found.")
        exit(1)

    merged_data = merge_advancement_files(json_files)

    with open(os.path.join(SCRIPT_DIR, OUTPUT_FILE), "w", encoding="utf-8") as f:
        # 👇 single-line output
        json.dump(merged_data, f, separators=(",", ":"), ensure_ascii=False)

    print(f"Merged {len(json_files)} files into {OUTPUT_FILE} (single-line JSON)")

