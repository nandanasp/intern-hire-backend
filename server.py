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

# db imports
from db.candidate import get_candidate, update_candidate, update_status

load_dotenv()
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
    print(candidate)
    print('\n---------------------------------------------------------\n')

    submission = candidate['submission'][0]
    resume_link = submission['resume_link']
    repo_link = submission['repo_link']
    new_candidate_id = candidate['_id']

    # 3. start run_data_job([data]) and update status
    update_status(candidate_id, 'REVIEW_STARTED')
    llm_res = await run_single_review(new_candidate_id, resume_link, repo_link)
    print("llm_res: ", llm_res)
    print('\n---------------------------------------------------------\n')
    # 4. update candidate details and change statust to review_done
    update_candidate(candidate_id, **llm_res)
    print('everything ran')
    return llm_res

if __name__ == '__main__':
    app.run(debug=True, port=3000)



