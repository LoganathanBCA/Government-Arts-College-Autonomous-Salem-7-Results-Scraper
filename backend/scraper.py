"""
scraper.py — Selenium browser automation for GACSLM7 eCampus portal.

Uses Chrome via webdriver-manager (no manual driver download).
Runs headless by default. Retries up to 3 times per student.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

logger = logging.getLogger(__name__)

PORTAL_URL = "https://ecampus.cc/gacslm7/index.php"
MAX_RETRIES = 3
WAIT_TIMEOUT = 15  # seconds


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return a Chrome WebDriver instance."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def _js_set_value(driver, element, value):
    """Set an input field's value via JavaScript (more reliable than .clear() + .send_keys())."""
    driver.execute_script(
        "arguments[0].value = ''; arguments[0].value = arguments[1]; "
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true})); "
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        element, value,
    )


def scrape_student(driver: webdriver.Chrome, register_no: str, dob: str) -> str | None:
    """
    Scrape a single student's result from the eCampus portal.

    Args:
        driver: Selenium WebDriver instance
        register_no: Student register number (e.g., '24UCS250904')
        dob: Date of birth in YYYY-MM-DD format (for JS injection)

    Returns:
        Raw HTML string of the result table, or None on failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[Attempt {attempt}/{MAX_RETRIES}] Scraping {register_no}")

            driver.get(PORTAL_URL)

            wait = WebDriverWait(driver, WAIT_TIMEOUT)

            # Wait for the form inputs to be CLICKABLE (not just present)
            reg_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "register_no"))
            )

            # Use JS to clear and fill fields (avoids "element not interactable")
            _js_set_value(driver, reg_input, register_no)

            # Inject DOB via JavaScript (date input requires JS)
            dob_input = driver.find_element(By.NAME, "dob")
            driver.execute_script(
                "arguments[0].value = arguments[1];", dob_input, dob
            )

            # Fill dummy email and mobile
            email_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "email"))
            )
            _js_set_value(driver, email_input, "test@example.com")

            mobile_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "mobile_no"))
            )
            _js_set_value(driver, mobile_input, "9999999999")

            # Click Submit
            submit_btn = wait.until(
                EC.element_to_be_clickable((By.NAME, "submit"))
            )
            submit_btn.click()

            # Wait for the "Result" link to appear
            result_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Result"))
            )
            result_link.click()

            # Wait for the result table to load
            table = wait.until(
                EC.presence_of_element_located((By.ID, "exam_datail"))
            )

            table_html = table.get_attribute("outerHTML")
            logger.info(f"✅ Successfully scraped {register_no}")
            return table_html

        except Exception as e:
            logger.warning(
                f"❌ Attempt {attempt}/{MAX_RETRIES} failed for {register_no}: {e}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(1)  # Brief pause before retry
            else:
                logger.error(f"🚫 Permanently failed for {register_no}")
                return None

    return None
