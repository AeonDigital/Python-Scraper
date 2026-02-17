from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Configure Chrome browser options
options = webdriver.ChromeOptions()
options.add_argument("--headless")            # Run browser in headless mode (no GUI window)
options.add_argument("--no-sandbox")          # Required in some Linux environments
options.add_argument("--disable-dev-shm-usage")  # Prevents issues on systems with limited shared memory

# Path to the ChromeDriver executable (adjust if installed elsewhere)
service = Service("/usr/bin/chromedriver")  # driver path

# Initialize the Chrome WebDriver with the defined options
driver = webdriver.Chrome(service=service, options=options)

# Open Google homepage to test Selenium setup
driver.get("https://www.google.com")

# Print the page title (should output "Google" if everything works correctly)
print(driver.title)

# Close the browser session
driver.quit()