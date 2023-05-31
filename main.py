from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Your profile path
profile_path = 'C:/Users/nmozol/AppData/Local/Google/Chrome/User Data/Default'

# Setup selenium webdriver with a profile
options = Options()
options.add_argument(f'user-data-dir={profile_path}')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins-discovery")
options.add_argument("--start-maximized")
options.add_argument("user_agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)






# Target URL
url = 'https://business.google.com/u/0/groups/113213648489666118794/reviews'  # Fill the URL of the Google Reviews
driver.get(url)

"""
# Accept the cookies
time.sleep(3)
try:
    driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span').click()
except Exception:
   pass
"""
# Wait until page is loaded
time.sleep(5)

# Define list to store reviews data
reviews = []
i=0

# Clicking the button to load more reviews
while True:
    try:
        # Find the button and click
        next_button = driver.find_element(By.XPATH, '//i[contains(text(), "navigate_next")]')
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)  # Wait for the reviews to load
      

        # Get page source and parse it
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Get all review containers
        containers = soup.find_all('div', class_='DsOcnf')
        


        # Extract data from each container
        for container in containers:
            adress = container.find('span', class_='ijHgsc').text
            name = container.find('a', class_='bFubHb').text
            date_review = container.find('span', class_='Wxf3Bf wUfJz').text
            #rating = container.find('span', class_='ODSEW-ShBeI-H1e3jb').get('aria-label')
            #review_text = container.find('span', class_='DT6Wnd').text

            code_filia = container.find('span', class_='mjZtse wjs4p').text
            i=code_filia.find(':')
            code_filia=code_filia[i+1:]


            answer_text = container.find('div', class_='DT6Wnd')
            reviews.append({'adress':adress, 'name': name, 'date_review': date_review, 'code_filia': code_filia, 'answer_text':answer_text})
        break
    except NoSuchElementException:
        # If the button is not found on the page, break the loop
        break


driver.close()



# Create dataframe
df = pd.DataFrame(reviews)

# Save to csv
df.to_csv('./reviews.csv', index=False, sep='|')

print('Reviews are saved.')