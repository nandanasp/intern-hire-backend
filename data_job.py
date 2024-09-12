from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from code_review import get_code_review
from pdf_utils import download_file_from_google_drive
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from db.job import get_jobs

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


async def get_code_summary(candidate, repo_link, data = {}):
    job = get_jobs(candidate.submission[0].job_id)
    try:
        data['code_review_score'] = get_code_review(job.job_desc, job.base_repo_url, repo_link)
    except:
        data['code_review_description'] = 'Token limit exceeded'
    return data

async def run_single_review(candidate_id, resume_link, repo_link, candidate):
    resume_link = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
    repo_link = "https://github.com/madangopal16072000/fyle-interview-intern-backend"
    data = {}
    
    data_coverage, data_resume, data_summary = await asyncio.gather(
        get_code_coverage(candidate_id, repo_link, data),
        get_resume_review(resume_link, data),
        get_code_summary(candidate, repo_link, data)
    )

    data.update(data_coverage)
    data.update(data_resume)
    data.update(data_summary)
    
    return data

if __name__ == '__main__':
    print('data job')
