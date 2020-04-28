import os
import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from dotenv import load_dotenv

from areas import areas
from platforms import platforms

REGEX = "([^\s]+)"

# load dotenv vars
project_folder = os.path.expanduser('~/code/projects/immowatch/immodigest')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))
MONGO_URI = os.getenv("MONGO_URI")

# init db connection
client = MongoClient(MONGO_URI, retryWrites=False)
db = client.immodigest

# set selenium options
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

for area in areas:
  for key, platform in platforms.items():
    print(f"Counting houses in {area}")
    print(platform["uri"].format(area, platform["housekey"]))
    driver.get(platform["uri"].format(area, platform["housekey"]))
    house_count = re.search(REGEX, driver.find_element(By.CSS_SELECTOR, platform["css_selector"]).text).group(0)
    print(house_count)
    print(f"Counting appartments in {area}")
    print(platform["uri"].format(area, platform["appkey"]))
    driver.get(platform["uri"].format(area, platform["appkey"]))
    appartment_count = re.search(REGEX, driver.find_element(By.CSS_SELECTOR, platform["css_selector"]).text).group(0)
    print(appartment_count)
    data = {
      "date_created": datetime.datetime.utcnow(),
      "platform": key,
      "houses": house_count,
      "appartments": appartment_count,
      "area": area
    }
    print(data)
    db.property.insert_one(data)
print("Goodbye :)")
driver.close()
client.close()
