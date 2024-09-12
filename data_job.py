from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from pdf_utils import download_file_from_google_drive

def run_data_job(data):
    for index, row in enumerate(data[:2]):
        row["resume_link"] = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
        print(f"Index {index}: {row["name"]}")
        resume_path = download_file_from_google_drive(row["resume_link"])
        print(resume_path)
        

if __name__ == '__main__':
    print('data job')
