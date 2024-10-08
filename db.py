import os
from enum import Enum
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .utils import generate_random_string

uri = os.environ["db_connection_string"]


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

def add_submission(timestamp, full_name, email, contact_number, github_repo_link, time_taken, college_name, year_of_passing, resume_link, current_hiring_eligibility, reviews):
    query = {"email":email}
    matched_documents = list(collection.find(query))
    if len(matched_documents) == 0:
        candidate = create_candidate(email=email, full_name=full_name, contact_number=contact_number, college_name=college_name, year_of_passing=year_of_passing, current_hiring_eligibility = current_hiring_eligibility, reviews=reviews)
        candidate_id = candidate["id"]
        append_submission_to_candidate(candidate_id = candidate_id, submitted_timestamp = timestamp, github_repo_link = github_repo_link, time_taken = time_taken, resume_link = resume_link)
    else:
        candidate = matched_documents[0]
        candidate_id = candidate["id"]
        append_submission_to_candidate(candidate_id = candidate_id, submitted_timestamp = timestamp, github_repo_link = github_repo_link, time_taken = time_taken, resume_link = resume_link)
    

def create_candidate(email, full_name, contact_number, college_name, year_of_passing, current_hiring_eligibility, reviews):
    candidate = {
        "id" : 'cnd{0}'.format(generate_random_string(string_length=10)),
        "email" : str(email),
        "full_name" : str(full_name),
        "contact_number" : str(contact_number),
        "college_name" : str(college_name),
        "year_of_passing" :  str(year_of_passing),
        "submissions" : [],
        "current_hiring_eligibility": current_hiring_eligibility,
        "reviews" : reviews,
        "current_status": "SUBMITTED"
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

def find_submission_by_github_repo_link(github_repo_link):
    matched_submission = collection.find_one({"submissions.github_repo_link": github_repo_link})
    if matched_submission is None:
        return None
    else:
        return matched_submission

def find_submission_by_video_link(video_link):
    matched_submission = collection.find_one({"submissions.video_link": video_link})
    if matched_submission is None:
        return None
    else:
        return matched_submission

def get_all_candidates():
    all_candidates = collection.find()
    return list(all_candidates)

find_submission_by_github_repo_link("https://github.com/5h15h1r/fyle-interview-intern-backend")
