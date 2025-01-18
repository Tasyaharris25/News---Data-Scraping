from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
import csv
import getpass

# Define the website
website = 'https://www.bbc.com/news'

# Path to ChromeDriver
path = r'C:\Users\salsa\Downloads\chromedriver-win64\chromedriver.exe'

# Set up Chrome options (optional)
options = Options()
#options.add_argument("--start-maximized")  # Example option to start maximized

# Initialize ChromeDriver using the Service class
service = Service(path)
driver = webdriver.Chrome(service=service)  # Pass the service and options explicitly

# Open the website
driver.get(website)

driver.find_element(By.LINK_TEXT,"Sign In").click()
#time.sleep(3)

email = driver.find_element(By.NAME,"email")
email.send_keys("salsabilatasya.syaaa@gmail.com")

driver.find_element(By.ID, "submit-button").click()

password = driver.find_element(By.NAME,"password")
#my_pass = getpass.getpass()
password.send_keys("Tasya.120575")
sign_in_button = driver.find_element(By.CSS_SELECTOR,'div[data-bbc-container="PasswordForm"]')
sign_in_button.click()


# Define a function to extract and save data from the current page
def extract_and_save_data(driver, writer, category_name):
    # Extract data
    dates = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="card-metadata-lastupdated"]')
    headlines = driver.find_elements(By.CSS_SELECTOR, 'h2[data-testid="card-headline"]')
    titles = driver.find_elements(By.CSS_SELECTOR,'a[data-testid="internal-link"]')
    contents = [link.get_attribute('href') for link in titles]
    #contents = driver.find_elements(By.CSS_SELECTOR, 'p[data-testid="card-description"]')
    #categories = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="card-metadata-tag"]')
    publisher = "BBC"

    # Loop through and save the data
    for date, headline, content, category in zip(dates, headlines, contents, category_name):
        print(date.text + " - " + headline.text + " - " + content + " - " )
        writer.writerow([date.text, headline.text, publisher, content,  category_name])


# Open a new CSV file
file = open("scraped_news_data.csv", "w", newline="", encoding="utf-8")

# Variable to write to the CSV
writer = csv.writer(file)
# Add header names for each column
writer.writerow(["published_date", "headline", "publisher", "contents", "categories"])

# List of links to be clicked
links_text = ["News", "Sport", "Business", "Innovation", "Culture", "Arts", "Travel", "Earth"]

# Loop through each link, click it, and extract data
for link_text in links_text:
    try:
        # Wait until the link is clickable, then click it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, link_text))).click()
        
        while True:  # Keep looping to handle pagination
            # Wait for the page to load completely
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h2[data-testid="card-headline"]')))
            
            # Call the function to save data
            extract_and_save_data(driver, writer,link_text)

            # Check for the "Next" button
            try:
                next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="pagination-next-button"]')))
                next_button.click()  # Click the "Next" button
            except:
                print(f"No 'Next' button found on page under '{link_text}'. Saving final page data and exiting pagination loop.")
                
                # Call the function again for the last page
                extract_and_save_data(driver, writer,link_text)
                
                break  # Exit the pagination loop

        # Go back to the main page
        driver.back()

    except Exception as e:
        print(f"Error while processing link '{link_text}': {e}")
        continue

# Close the CSV file and the browser
file.close()

