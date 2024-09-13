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
from db.candidate import get_candidate, update_candidate, update_status, get_candidates_by_job_id
from test_coverage_worker import get_code_coverage
from resume_worker import get_resume_review
from worker import run_single_review, run_bulk_review
from mail_worker import send_email, send_email_bulk

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

@app.route("/", methods=['GET'])
def hello():
    return "hello"

@app.route('/candidates/<candidate_id>', methods=['GET'])
def test(candidate_id):
    return get_candidate(candidate_id)

@app.route('/candidate-review/<candidate_id>', methods=['POST'])
def candidate_review(candidate_id):
    # 1. fetch candidate data from mongodb, data
    candidate = get_candidate(candidate_id)
    print(type(candidate))
    print('\n---------------------------------------------------------\n')

    submission = candidate['submission'][0]

    resume_link = submission['resume_link']
    repo_link = submission['repo_link']
    new_candidate_id = candidate['_id']
    
    queue.enqueue(run_single_review, new_candidate_id, resume_link, repo_link)

    res = {
        'message': 'REVIEW_TASK_ENQUEUED',
        'status': 'SUCCESS'
    }

    return jsonify(res), 200


@app.route('/candidate-review/bulk/<job_id>', methods=['POST'])
def candidate_review_bulk(job_id):
    
    candidate_list = get_candidates_by_job_id(job_id)
    print(len(candidate_list))
    print(candidate_list)

    queue.enqueue(run_bulk_review, candidate_list)
    res = {
        'message': 'REVIEW_TASK_ENQUEUED',
        'status': 'SUCCESS'
    }

    return jsonify(res), 200


@app.route('/send_email', methods=['POST'])
def send_mail():
    res = request.get_json()

    data = res['data']

    recipient_email = data['recipient_email']

    status = data['status']

    queue.enqueue(send_email, recipient_email, status)

    res = {
        'message': 'EMAIL_TASK_ENQUEUED',
        'status': 'SUCCESS'
    }

    return jsonify(res), 200

@app.route('/send_email/bulk', methods = ['POST'])
def send_mail_bulk():
    data = request.get_json()

    mail_list = data['data']['mail_list']

    queue.enqueue(send_email_bulk, mail_list)
    res = {
        'message': 'EMAIL_TASK_ENQUEUED',
        'status': 'SUCCESS'
    }

    return jsonify(res), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)



