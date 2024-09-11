from enum import Enum
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .utils import generate_random_string

uri = "mongodb+srv://nandanasp:<password>@cluster0.s279g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True)

db = client.test

# Select the collection
collection = db.candidate

class StatusEnum(str, Enum):
    SUBMITTED = 'SUBMITTED'
    AI_REVIEWED = 'AI_REVIEWED'
    SELECTED = 'SELECTED'
    REJECTED = 'REJECTED'

def add_submission(timestamp, full_name, email, contact_number, github_repo_link, time_taken, college_name, year_of_passing, resume_link ):
    query = {"email":email}
    matched_documents = list(collection.find(query))
    if len(matched_documents) == 0:
        candidate = create_candidate(email=email, full_name=full_name, contact_number=contact_number, college_name=college_name, year_of_passing=year_of_passing)
        candidate_id = candidate["id"]
        append_submission_to_candidate(candidate_id = candidate_id, submitted_timestamp = timestamp, github_repo_link = github_repo_link, time_taken = time_taken, resume_link = resume_link)
    else:
        candidate = matched_documents[0]
        candidate_id = candidate["id"]
        append_submission_to_candidate(candidate_id = candidate_id, submitted_timestamp = timestamp, github_repo_link = github_repo_link, time_taken = time_taken, resume_link = resume_link)
    

def create_candidate(email, full_name, contact_number, college_name, year_of_passing):
    candidate = {
        "id" : 'cnd{0}'.format(generate_random_string(string_length=10)),
        "email" : str(email),
        "full_name" : str(full_name),
        "contact_number" : str(contact_number),
        "college_name" : str(college_name),
        "year_of_passing" :  str(year_of_passing),
        "submissions" : []
    }
    inserted_candidate = collection.insert_one(candidate)
    return candidate

def append_submission_to_candidate(candidate_id, submitted_timestamp, github_repo_link, time_taken, resume_link):
    
    submission = {
        "id" : 'sub{0}'.format(generate_random_string(string_length=10)),
        "submitted_timestamp" : submitted_timestamp,
        "status" : StatusEnum.SUBMITTED,
        "github_repo_link" : str(github_repo_link),
        "time_taken" : str(time_taken),
        "resume_link" : str(resume_link)
    }

    collection.update_one({"id":candidate_id}, {"$push": {"submissions": submission}})
