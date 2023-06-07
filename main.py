from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
#from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import xpath
import dateparser
import datetime
import pyodbc
from traceback import format_exc
import os

from warnings import filterwarnings
filterwarnings("ignore")


# get the current working directory
current_working_directory = os.getcwd()

try:
    #import secret variables
    import base64
    from secrets_file import server,database,port,user,password
    server=base64.b64decode(server.decode("utf-8")).decode()
    database=base64.b64decode(database.decode("utf-8")).decode()
    port=base64.b64decode(port.decode("utf-8")).decode()
    user=base64.b64decode(user.decode("utf-8")).decode()
    password=base64.b64decode(password.decode("utf-8")).decode()




    #connect to sql server
    driver='SQL Server'
    cnxn = pyodbc.connect('DRIVER={};Server={};Database={};Port={};User ID={};Password={}'.format(driver,server,database,port,user,password))
    cursor = cnxn.cursor()

    #cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
    #cnxn.setencoding('latin1')

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


    # # Accept the cookies
    # time.sleep(3)
    # try:
    #     driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span').click()
    # except Exception:
    #    pass

    # Wait until page is loaded
    time.sleep(5)

    # Define list to store reviews data

    #reviews = []
    j=0


    #clearing table
    cursor.execute("delete from {}.{}.[dbo].[Google_Review_Scrapping];".format(server,database))
    cnxn.commit()


    # Clicking the button to load more reviews
    while True:
    
        j+=1
        # Get page source and parse it
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Get all review containers
        containers = soup.find_all('div', class_='DsOcnf')
        


        # Extract data from each container
        for container in containers:
            

            adress = container.find('span', class_='ijHgsc').text
            name = container.find('a', class_='bFubHb').text
            date_review = container.find('span', class_='Wxf3Bf wUfJz').text
            
            rating = container.find_all('span', class_='DPvwYc L12a3c z3FsAc')
            rating=len(rating)
            
            try:
                review_text = container.find('span', class_='oiQd1c').text
            except:
                review_text=None


            user_url=container.find('a', class_='bFubHb').attrs['href']
            try:
                replay_time=container.find('span', class_='Wxf3Bf Gjqk4b').text
                replay_time=dateparser.parse(replay_time, languages=['uk'])
                replay_time=replay_time.strftime('%Y-%m-%d')
                
            except:
                replay_time=None

            code_filia = container.find('span', class_='mjZtse wjs4p').text
            i=code_filia.find(':')
            code_filia=int(code_filia[i+1:].replace(" ", ""))


            try:
                reply_text = container.find('div', class_='DT6Wnd').text
                
            except:
                reply_text=None
            

            date_review=dateparser.parse(date_review, languages=['uk'])
            date_review=date_review.strftime('%Y-%m-%d')

            # reviews.append({'date_review': date_review
            #                 ,'code_filia': code_filia
            #                 ,'adress':adress
            #                 ,'name': name
            #                 ,'user_url':user_url
            #                 ,'review_text':review_text
            #                 ,'replay_time':replay_time
            #                 ,'reply_text':reply_text
            #                 ,'rating':rating})
            
            
            insert_statement="""INSERT INTO {}.{}.[dbo].[Google_Review_Scrapping] 
            VALUES (?,?,?,?,?,?,?,?,?)""".format(server,database)
            
            # print((
            #     date_review
            #     ,code_filia
            #     ,adress
            #     ,name
            #     ,user_url
            #     ,review_text
            #     ,replay_time
            #     ,reply_text
            #     ,rating))
            

            cursor.execute(insert_statement, (
                date_review
                ,code_filia
                ,adress
                ,name
                ,user_url
                ,review_text
                ,replay_time
                ,reply_text
                ,rating))
            cnxn.commit()


        #exit when 'next' button will be unavalible
        try:
            button_check=soup.find('button', class_="VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ QDwDD mN1ivc vX5N7b").attrs['disabled']
            break
        except:
            pass
        
    #click on 'next' button
        try:
            next_button = driver.find_element(By.XPATH, '//i[contains(text(), "navigate_next")]')
            driver.execute_script("arguments[0].click();", next_button)
        except:
            break
        time.sleep(5)  # Wait for the reviews to load
        
    time.sleep(3)


    #closing sql connection
    cnxn.close()
    driver.close()



    # Create dataframe
    #df = pd.DataFrame(reviews)

    # Save to csv
    #df.to_csv('./reviews.csv', index=False, sep='\t', encoding='utf-16')

    print('Reviews are saved.')
except:
        f=open(current_working_directory + '/log.txt', 'a')
        f.write('----------------------------------------\n')
        f.write(format_exc())
        f.write('\nstopped on : '+ str(j) + '  th page\n')
        f.write('occurred on ' + str(datetime.datetime.now())+ '\n')
        f.write('----------------------------------------\n\n\n')
        f.close()