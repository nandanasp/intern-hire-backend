from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from pdf_utils import download_file_from_google_drive
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from db.candidate import update_status, update_candidate

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
from code_coverage import TestResult


def run_data_job(data):
    arr = []
    for index, row in enumerate(data):
        row["resume_link"] = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
        resume_path = download_file_from_google_drive(row["resume_link"])
        row["resume_review"] = get_resume_review(resume_path)

        row["github_repository_link"] = "https://github.com/madangopal16072000/fyle-interview-intern-backend"

        print(f"Index {index}: {row["full_name"]}")
        row["code_coverage"] = get_code_coverage(row["github_repository_link"])
        arr.append(row)
    return arr

        
async def get_code_coverage(candidate_id, repo_link, data = {}):
    tr = TestResult(llm=llm, github_repo=repo_link)
    status = tr.get_status()

    if status == 'success':
        tr.process()
        tro = tr.get_summary()
        coverage = tro.coverage
        data['code_coverage_score'] = coverage
    else:
        data['code_coverage_description'] = 'Github Action Workflow run Failed!'
    return data


async def get_code_summary(resume_link, data = {}):
    return data

async def run_single_review(candidate_id, resume_link, repo_link):

    update_status(candidate_id, 'REVIEW_STARTED_TESTING')

    resume_link = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
    repo_link = "https://github.com/madangopal16072000/fyle-interview-intern-backend"
    data = {}
    
    data_coverage, data_resume, data_summary = await asyncio.gather(
        get_code_coverage(candidate_id, repo_link, data),
        get_resume_review(resume_link, data),
        get_code_summary(resume_link, data)
    )

    data.update(data_coverage)
    data.update(data_resume)
    data.update(data_summary)
    
    update_candidate(candidate_id, **data)

# if __name__ == '__main__':
#     print('data job')
