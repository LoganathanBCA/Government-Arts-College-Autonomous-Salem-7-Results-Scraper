"""
scraper.py — Selenium browser automation for SLMGACCOE eCampus portal.

Flow:
  1. Login at index.php with regno + dob (YYYY-MM-DD format for date input)
  2. Navigate to ResultPrint.php?resulttype=Result
  3. Extract the marks table (first <table> on the page)
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

PORTAL_URL = "https://slmgaccoe.edecampus.com/student/index.php"
RESULT_URL = "https://slmgaccoe.edecampus.com/student/ResultPrint.php?resulttype=Result"
MAX_RETRIES = 3
WAIT_TIMEOUT = 20


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
    """Set an input field's value via JavaScript dispatch."""
    driver.execute_script(
        "arguments[0].value = ''; arguments[0].value = arguments[1]; "
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true})); "
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        element, value,
    )


def scrape_student(driver: webdriver.Chrome, register_no: str, dob: str) -> str | None:
    """
    Scrape a single student's result from the SLMGACCOE portal.

    Args:
        driver: Selenium WebDriver instance
        register_no: Student register number (e.g., '24UCS250904')
        dob: Date of birth in YYYY-MM-DD format

    Returns:
        Raw HTML string of the result table, or None on failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[Attempt {attempt}/{MAX_RETRIES}] Scraping {register_no}")

            driver.get(PORTAL_URL)
            wait = WebDriverWait(driver, WAIT_TIMEOUT)

            # Fill register number field
            reg_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "regno"))
            )
            _js_set_value(driver, reg_input, register_no)

            # Fill date of birth (type="date" expects YYYY-MM-DD)
            dob_input = driver.find_element(By.NAME, "dob")
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                dob_input, dob,
            )

            # Click Login button
            submit_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_btn.click()

            # Wait for redirect to dashboard (confirms login success)
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: "dashboard" in d.current_url
            )
            logger.info(f"Login successful for {register_no}")

            # Navigate directly to the result print page
            time.sleep(1)
            driver.get(RESULT_URL)

            # Wait for the page to load
            time.sleep(1.5)

            # Extract the first table on the page (the marks table)
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            table_html = table.get_attribute("outerHTML")

            logger.info(f"Successfully scraped {register_no}")
            return table_html

        except Exception as e:
            logger.warning(
                f"Attempt {attempt}/{MAX_RETRIES} failed for {register_no}: {e}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(1)
            else:
                logger.error(f"Permanently failed for {register_no}")
                return None

    return None
