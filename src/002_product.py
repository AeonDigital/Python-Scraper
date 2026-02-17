import sys
import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def scrape_product_details(input_csv, output_csv, fields):
    # Configure Chrome browser options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode (no GUI window)
    options.add_argument("--no-sandbox")  # Required in some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # Prevents issues on systems with limited shared memory
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection as automated browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0 Safari/537.36")

    # Path to ChromeDriver executable
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    results = []

    # Read input CSV
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = sum(1 for _ in reader)  # Count total rows
        f.seek(0)
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, start=1):
            name = row["Name"]
            link = row["Link"]

            print(f"\n>>> Product {idx}/{total}: {name}")
            driver.get(link)
            time.sleep(3)  # wait for page to load

            soup = BeautifulSoup(driver.page_source, "html.parser")

            product_data = {"name": name, "link": link}
            for field_name, (selector, mode) in fields.items():
                if mode.endswith("[]"):  # array case
                    attr = mode[:-2]  # remove brackets
                    els = soup.select(selector)
                    values = []
                    for el in els:
                        if not attr or attr.lower() == "innertext":
                            text = el.get_text(strip=True).replace('"', "'")
                            values.append(text)
                        else:
                            val = el.get(attr, "")
                            if val:
                                val = val.replace('"', "'")
                                values.append(val)
                    product_data[field_name] = json.dumps(values, ensure_ascii=False)
                else:
                    el = soup.select_one(selector)
                    if el:
                        if not mode or mode.lower() == "innertext":
                            value = el.get_text(strip=True)
                        else:
                            value = el.get(mode, "")
                        value = value.replace('"', "'")
                    else:
                        value = ""
                    product_data[field_name] = value

            results.append(product_data)

    driver.quit()

    # Save output CSV
    fieldnames = ["name", "link"] + list(fields.keys())
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for item in results:
            writer.writerow(item)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python 002_product.py <input.csv> <output.csv> <field1> <selector1> <type1> [<field2> <selector2> <type2> ...]")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    args = sys.argv[3:]
    if len(args) % 3 != 0:
        print("Error: parameters must be in triplets (name + selector + type).")
        sys.exit(1)

    fields = {}
    for i in range(0, len(args), 3):
        field_name = args[i]
        selector = args[i+1]
        mode = args[i+2]
        fields[field_name] = (selector, mode)

    scrape_product_details(input_csv, output_csv, fields)