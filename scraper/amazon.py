from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from amazoncaptcha import AmazonCaptcha
import time
import datetime
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate('FirebaseSDK.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://scraper-db-4fab4-default-rtdb.europe-west1.firebasedatabase.app/'
})

def find_amazon_search_input(driver):
    ids_to_try = ["twotabsearchtextbox", "nav-bb-search"]
    
    for id_to_try in ids_to_try:
        try:
            amzInput = driver.find_element(By.ID, id_to_try)
            return amzInput
        except NoSuchElementException:
            pass
    
    raise NoSuchElementException("Unable to find Amazon search input field with any of the provided IDs")

def runAmazonScraper(search):
    print('running with search: ',search)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--lang=en")

    chromeService = Service(executable_path=r"scraper\chromedriver.exe")
    driver = webdriver.Chrome(service=chromeService, options=options)

    #-----------------------DONT TOUCH LOADING SCREEN-----------------------

    driver.get("https://google.com")
    driver.find_element(By.ID, "L2AGLb").click() #-ACCEPT ALL COOKIES BUTTON DON'T DELETE EVER

    inputElement = driver.find_element(By.CLASS_NAME, "gLFyf")
    # time.sleep(5)
    # inputElement.send_keys("youtube" + Keys.ENTER)

    # driver.get("https://youtube.com")
    # time.sleep(5)
    # driver.get("https://google.com")

    driver.get("https://amazon.com")

    try:
        amzCaptcha = driver.find_element(By.XPATH,"//div[contains(@class, 'a-row') and contains(@class, 'a-text-center')]//img").get_attribute("src")
        captcha = AmazonCaptcha.fromlink(amzCaptcha)
        captcha_value = AmazonCaptcha.solve(captcha)

        inputBox = driver.find_element(By.ID,"captchacharacters")
        inputBox.send_keys(captcha_value + Keys.ENTER)

        time.sleep(2)
    except:
        pass

    #-----------------------DONT TOUCH LOADING SCREEN-----------------------

    try:
        amzInput = find_amazon_search_input(driver)
        amzInput.send_keys(search + Keys.ENTER)
    except NoSuchElementException as e:
        print(e)

    firstProduct = driver.find_element(By.CSS_SELECTOR, "div[data-index='2']")
    container_div = firstProduct.find_element(By.XPATH, ".//div[@class='a-section a-spacing-small a-spacing-top-small']")

    title_div = container_div.find_element(By.XPATH, ".//div[@class='a-section a-spacing-none puis-padding-right-small s-title-instructions-style']")

    # Get the text of the title
    title_text = title_div.text
    # print("Title:", title_text)

    price_info = firstProduct.find_element(By.CLASS_NAME, "a-price")
    price_text = price_info.text.replace('\n', '')

    price_integer = price_text.split('.')[0]
    price = price_integer[:-2] + '.' + price_integer[-2:]
    # print("Price:", price)

    price_float = float(price.replace('$', '').replace(',', ''))
    # print(price_float)

    title_link = title_div.find_element(By.XPATH, ".//a")
    href = title_link.get_attribute("href")

    # print("Link:", href[:50] + '...')

    driver.quit()

    # Create a reference to the specific search term in the database
    search_term_ref = db.reference(f'searches/{search}')

    current_datetime = datetime.datetime.now().isoformat()

    # Define the data to store
    data = {
        'date': current_datetime,
        'price': price_float,
        'link': href
    }

    print(datetime.datetime.fromisoformat(current_datetime))

    # Fetch existing data if it exists
    existing_data = search_term_ref.get()
    if existing_data is None:
        existing_data = []

    # Append new data to the list
    existing_data.append(data)

    # Store the updated data back in the database
    search_term_ref.set(existing_data)

    print("Data has been written to the database")

    return existing_data

def give_search_data(search):
    search_term_ref = db.reference(f'searches/{search}')
    existing_data = search_term_ref.get()
    return existing_data

def give_all_data():
    search_term_ref = db.reference('searches')
    existing_data = search_term_ref.get()
    return existing_data

# print(runAmazonScraper("4090"))