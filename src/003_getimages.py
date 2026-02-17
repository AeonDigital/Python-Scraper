import sys
import os
import csv
import json
import requests

def download_images(input_csv, column_name, column_type, output_dir, id_column=None):
    # Create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = sum(1 for _ in reader)  # Count total rows
        f.seek(0)
        reader = csv.DictReader(f)

        counter = 1
        for idx, row in enumerate(reader, start=1):
            cell = row.get(column_name, "")
            if not cell:
                continue

            urls = []
            if column_type.lower() == "arrayjson":
                try:
                    urls = json.loads(cell)  # Parse JSON array of URLs
                except Exception:
                    print(f"Error parsing JSON in line {idx}")
                    continue
            else:  # raw (single URL)
                urls = [cell]

            # Optional product identifier value
            id_value = ""
            if id_column and id_column in row:
                id_value = row[id_column].strip().replace(" ", "_")
                id_value = id_value.replace('"', "'")

            for u in urls:
                try:
                    resp = requests.get(u, timeout=10)
                    if resp.status_code == 200:
                        # Extract original filename from URL
                        original_name = os.path.basename(u.split("?")[0])
                        if not original_name:
                            original_name = f"img{counter}.jpg"

                        # Numeric prefix with 5 digits
                        prefix = f"{counter:05d}"

                        # Build final filename
                        if id_value:
                            filename = f"{prefix}-{id_value}-{original_name}"
                        else:
                            filename = f"{prefix}-{original_name}"

                        filepath = os.path.join(output_dir, filename)

                        # Save image to file
                        with open(filepath, "wb") as img_file:
                            img_file.write(resp.content)

                        print(f"Image saved: {filepath}")
                        counter += 1
                    else:
                        print(f"Failed to download {u} (status {resp.status_code})")
                except Exception as e:
                    print(f"Error downloading {u}: {e}")

        print(f"\nTotal images downloaded: {counter-1}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python 003_getimages.py <input.csv> <column> <type: raw|arrayJSON> <output_dir> [id_column]")
        sys.exit(1)

    input_csv = sys.argv[1]
    column_name = sys.argv[2]
    column_type = sys.argv[3]
    output_dir = sys.argv[4]
    id_column = sys.argv[5] if len(sys.argv) > 5 else None

    download_images(input_csv, column_name, column_type, output_dir, id_column)