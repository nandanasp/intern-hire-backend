from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://team-ctrl-cv:IsGrEwDfaJCDJY2b@cluster0.jwls1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)

# Send a ping to confirm a successful connection

db = client['test']

# try:
#     client.admin.command('ping')

#     db = client['test']
#     candidates = db['candidates']
#     print(candidates.find_one())
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)