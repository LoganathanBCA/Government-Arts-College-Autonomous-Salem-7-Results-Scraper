import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import subprocess

# Load students from Excel and convert DOB format
df = pd.read_excel("students.xlsx", engine="openpyxl")
df['dob'] = pd.to_datetime(df['dob'], dayfirst=True).dt.strftime('%Y-%m-%d')
students = df.to_dict(orient='records')

# Setup Edge WebDriver
edge_driver_path = "msedgedriver.exe"
options = Options()
options.add_argument("--start-maximized")
service = EdgeService(edge_driver_path)
driver = webdriver.Edge(service=service, options=options)

# HTML header for results file
all_tables_html = "<html><head><title>All Student Results</title></head><body>"

for student in students:
    register_no = student["register_no"]
    dob = student["dob"]

    print(f"⏳ Processing: {register_no} ...")

    driver.get("https://ecampus.cc/gacslm7/index.php")
    time.sleep(2)

    # Fill the form
    driver.find_element(By.NAME, "register_no").send_keys(register_no)
    dob_input = driver.find_element(By.NAME, "dob")
    driver.execute_script("arguments[0].value = arguments[1];", dob_input, dob)
    driver.find_element(By.NAME, "email").send_keys("test@example.com")
    driver.find_element(By.NAME, "mobile_no").send_keys("9999999999")

    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)

    # Click "Result" button
    try:
        driver.find_element(By.LINK_TEXT, "Result").click()
        time.sleep(2)

        # Extract result table
        table = driver.find_element(By.ID, "exam_datail")
        table_html = table.get_attribute('outerHTML')

        # Append to results
        all_tables_html += f"<h2>{register_no}</h2>{table_html}<br><hr><br>"

        print(f"✅ Done: {register_no}")
    except Exception as e:
        print(f"❌ Failed for {register_no}: {e}")
        continue

# Close browser
driver.quit()

# Finalize HTML file
all_tables_html += "</body></html>"
with open("all_results.html", "w", encoding="utf-8") as f:
    f.write(all_tables_html)

print("✅ All results saved to all_results.html")

# Run main_output_process.py after finishing
subprocess.run(["python", "output_process.py"], check=True)