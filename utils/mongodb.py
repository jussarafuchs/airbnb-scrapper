
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

mongo_db_server = "mongodb://localhost:27017/"
database_name = "airbnb_prices"

class Database_Config:
    LOCATION = "locations"
    LOGS = "logs"
    AIRBNB_DATA = "airbnb_data"
    EXECUTIONS = "executions"

def get_database():
    client = pymongo.MongoClient(mongo_db_server)
    db = client[database_name]

    return db, client
