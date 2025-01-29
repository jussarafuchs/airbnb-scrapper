import pymongo
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bson.objectid import ObjectId
from datetime import datetime

def extract_listing_data(driver, obj):
    
    # Find all listings
    type_element = driver.find_element(By.CSS_SELECTOR, 'h2[elementtiming="LCP-target"]')
    type = "Espaço inteiro" if "Espaço inteiro" in type_element.text else "Quarto"
    
    owner_name_element = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="HOST_OVERVIEW_DEFAULT"]')
    owner_name_split = owner_name_element.text.split('\n')
    name = owner_name_split[0].replace("Anfitriã(o): ", "")
    
    obj["type"] = type
    obj["typeCompleteDescription"] = type_element.text
    obj["ownerName"] = name
    
    return obj

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
service = Service('chromedriver.exe')

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=service, options=chrome_options)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["airbnb_prices"]
locationCollection = db["locations"]
logsCollection = db["logs"]

page_size = 10 
page_number = 1 

while True:
    try: 
        missing_type_listings = locationCollection.find({
            "$or": [
                { "type": { "$exists": False } },
                { "type": "" }
            ]
        }).skip((page_number - 1) * page_size).limit(page_size)

        updates = []
        listings_found = False

        for obj in missing_type_listings:
            
            try:
                listings_found = True  # At least one listing was found
                url = obj.get("url")
                
                if "http" not in url:
                    url = "https://" + url
                
                # Open the URL
                driver.get(url)

                # Wait for the page to load
                time.sleep(5)  # Adjust sleep time as necessary
        
                newObj = extract_listing_data(driver, obj)
                
                # Prepare the update operation
                update_result = locationCollection.update_one(
                    {"airbnbId": newObj.get("airbnbId")},   # Filter to find the document by airbnbId
                    {"$set": newObj}                        # Update operation to set the newObj data
                )
                
            except Exception as e:
                log = {
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "data": obj,
                    "when": "Failed to save airbnb type for a specific one",
                    "message": str(e)
                }
                logsCollection.insert_one(log)  
                listing_found = False
            
        # Break the loop if no more listings are found
        if not listings_found:
            break

        # Increment the page number for the next iteration
        page_number += 1
    except Exception as e:
        log = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": "page: " + str(page_number),
            "when": "Failed to save airbnb types",
            "message": str(e)
        }
        logsCollection.insert_one(log)            
        break

client.close()
