from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import os

# Path to msedgedriver.exe
edge_driver_path = "msedgedriver.exe"  
# Setup Edge options
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless=new")  # Uncomment to run headless

# Create Edge service and driver
service = EdgeService(edge_driver_path)
driver = webdriver.Edge(service=service, options=options)


# Visit the site
driver.get("https://ecampus.cc/gacslm7/index.php")
time.sleep(2)

# Fill the form
driver.find_element(By.NAME, "register_no").send_keys("23PCS248103")
dob = "2004-01-29"  # format accepted by the site

dob_input = driver.find_element(By.NAME, "dob")
driver.execute_script("arguments[0].value = arguments[1];", dob_input, dob)
driver.find_element(By.NAME, "email").send_keys("loganathanbcashift2@gmail.com")
driver.find_element(By.NAME, "mobile_no").send_keys("9099999999")

# Submit
driver.find_element(By.NAME, "submit").click()
time.sleep(2)

# Click Result button
driver.find_element(By.LINK_TEXT, "Result").click()
time.sleep(2)

# Save Screenshot
# screenshot_name = "23PCS248103.png"
# driver.save_screenshot(screenshot_name)
# print(f"✅ Screenshot saved as {screenshot_name}")

# Save table HTML
table = driver.find_element(By.ID, "exam_datail")
table_html = table.get_attribute('outerHTML')
with open("exam_datail_table.html", "w", encoding="utf-8") as f:
    f.write(table_html)
print("✅ Table HTML saved to exam_datail_table.html")

driver.quit()
