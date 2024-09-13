from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from pdf_utils import download_file_from_google_drive
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from db.candidate import update_status, update_candidate, update_final_status
from time import sleep

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
from code_coverage import TestResult
from code_review import get_review
        
def get_code_coverage(candidate_id, repo_link, data = {}):
    tr = TestResult(llm=llm, github_repo=repo_link)
    status = tr.get_status()

    # if status == 'success':
    tr.process()
    tro = tr.get_summary()
    coverage = tro.coverage
    data['code_coverage_score'] = coverage
    data['code_coverage_description'] = tro.summary
    # else:
    #     data['code_coverage_description'] = 'Github Action Workflow run Failed!'

    return data


def get_code_summary(repo_link, data = {}):
    res = get_review(repo_link)
    data['code_review'] = res
    print(res)
    return data

def run_single_review(candidate_id, resume_link, repo_link):

    update_status(candidate_id, 'ongoing_ai_review')
    
    data = {}
    
    data_coverage = get_code_coverage(candidate_id, repo_link, data) 

    data_resume = get_resume_review(resume_link, data)
    data_summary = get_code_summary(repo_link, data)

    data.update(data_coverage)
    data.update(data_resume)
    data.update(data_summary)
    data['status'] = 'AI_REVIEWED'

    update_candidate(candidate_id, **data)
    update_final_status(candidate_id, 'ai_reviewed')

def run_bulk_review(candidate_list):
    for candidate in candidate_list:
        run_single_review(candidate['candidate_id'], candidate['resume_link'], candidate['repo_link'])