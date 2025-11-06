
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote_plus


load_dotenv()

user=os.getenv("MONGO_ATLAS_USER")
password=os.getenv("MONGO_ATLAS_PASSWORD")
host=os.getenv("MONGO_ATLAS_HOST")
params=os.getenv("MONGO_ATLAS_PARAMS","?retryWrites=true&w=majority")


if not user or not password or not host:
    print("Missing MongoDB credentials in enviroment. Kindly set it up ")
    sys.exit(1)

password_quoted=quote_plus(password)


uri = f"mongodb+srv://{user}:{password_quoted}@{host}/{params}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)