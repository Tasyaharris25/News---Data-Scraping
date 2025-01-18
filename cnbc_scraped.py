from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import csv

# Define the website
website = 'https://www.cnbc.com/'

# Path to ChromeDriver
path = r'C:\Users\salsa\Downloads\chromedriver-win64\chromedriver.exe'

# Set up Chrome options (optional)
options = Options()
options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors

# Initialize ChromeDriver using the Service class
service = Service(path)
driver = webdriver.Chrome(service=service, options=options)

# Open the website
driver.get(website)

# Handle the sign-in process
try:
    driver.find_element(By.LINK_TEXT, "SIGN IN").click()
    email = driver.find_element(By.NAME, "email")
    email.send_keys("salsabilatasya.syaaa@gmail.com")
    password = driver.find_element(By.NAME, "password")
    password.send_keys("Tasya.120575")
    sign_in_button = driver.find_element(By.NAME, "signin")
    sign_in_button.click()
except Exception as e:
    print(f"Error during sign-in: {e}")

# Define a function to extract and save data from the current page
def extract_and_save_data(driver, writer, category_name):
    try:
        # Extract data
        dates = driver.find_elements(By.CSS_SELECTOR, 'span[class="Card-time"]')
        headlines = driver.find_elements(By.CSS_SELECTOR, 'a[class="Card-title"]')
        contents = [link.get_attribute('href') for link in headlines]
        publisher = "CNBC"

        # Loop through and save the data
        for date, headline, content in zip(dates, headlines, contents):
            print(f"{date.text} - {headline.text} - {content}")
            writer.writerow([date.text, headline.text, publisher, content, category_name])
    except Exception as e:
        print(f"Error while extracting data: {e}")

# Open a new CSV file
file = open("cnbc.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(file)
writer.writerow(["published_date", "headline", "publisher", "contents", "categories"])

# List of links to be clicked (based on category)
links_text = ["Business", "Investing", "Tech", "Politics"]

# Loop through each link, click it, and extract data
for link_text in links_text:
    try:
        # Wait until the link is clickable, then click it
        link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[href="/{link_text.lower()}/"]'))
        )
        link.click()

        # Handle modals if they appear
        try:
            modal_close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="modal-close-button"]'))
            )
            modal_close_button.click()
        except Exception:
            print("No modal to close.")

        # Initialize the counter for "Load More" clicks
        load_more_clicks = 0
        max_clicks = 10  # Maximum number of clicks allowed

        while load_more_clicks < max_clicks:
            # Wait for the page to load completely
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[class="Card-title"]'))
            )

            # Call the function to save data
            extract_and_save_data(driver, writer, link_text)

            # Check for the "Load More" button
            try:
                load_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[class="icon-arrow-down-readmore"]'))
                )
                load_button.click()
                load_more_clicks += 1
                print(f"'Load More' clicked {load_more_clicks} time(s) under category '{link_text}'")
            except Exception:
                print(f"No 'Load More' button found under category '{link_text}'. Exiting pagination loop.")
                break

        # After completing the "Load More" loop or hitting the limit, go back to the main page
        driver.back()

    except Exception as e:
        print(f"Error while processing link '{link_text}': {e}")
        continue

# Close the CSV file and the browser
file.close()
driver.quit()
