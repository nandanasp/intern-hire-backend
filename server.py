import os
from flask import Flask, request, jsonify
from flask_cors import CORS  
from dotenv import load_dotenv
from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from excel_worker import excel_to_json
from data_job import run_data_job, run_single_review
import time
import asyncio
import redis 
from rq import Queue

# db imports
from db.candidate import get_candidate, update_candidate, update_status
from test_coverage_worker import get_code_coverage
from resume_worker import get_resume_review
from worker import run_single_review

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
connection = redis.from_url('redis://localhost:6379/0')
queue = Queue("llms", connection=connection)
# Test the connection
try:
    # Ping the Redis server
    response = connection.ping()
    if response:
        print("Connected to Redis successfully!")
    else:
        print("Failed to connect to Redis.")
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")


app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route('/candidates/<candidate_id>', methods=['GET'])
def test(candidate_id):
    return get_candidate(candidate_id)

@app.route('/candidate-review/<candidate_id>', methods=['POST'])
async def candidate_review(candidate_id):
    # 1. fetch candidate data from mongodb, data
    candidate = get_candidate(candidate_id)
    print(type(candidate))
    print('\n---------------------------------------------------------\n')

    submission = candidate['submission'][0]

    resume_link = submission['resume_link']
    repo_link = submission['repo_link']
    new_candidate_id = candidate['_id']

    # queue.enqueue(get_code_coverage, new_candidate_id, "https://github.com/madangopal16072000/fyle-interview-intern-backend")

    # queue.enqueue(get_resume_review, "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view")
    
    queue.enqueue(run_single_review, new_candidate_id, resume_link, repo_link)

    return ""
    # # 3. start run_data_job([data]) and update status
    # llm_res = await run_single_review(new_candidate_id, resume_link, repo_link)
    # print("llm_res: ", llm_res)
    # print('\n---------------------------------------------------------\n')
    # # 4. update candidate details and change statust to review_done
    # update_candidate(candidate_id, **llm_res)
    # print('everything ran')
    # return llm_res

@app.route('/candidate-review/<job_id>', methods=['POST'])
async def candidate_review_bulk(candidate_id):

    
if __name__ == '__main__':
    app.run(debug=True, port=3000)



