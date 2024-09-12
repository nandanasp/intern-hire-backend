from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from pdf_utils import download_file_from_google_drive

def run_data_job(data):
    arr = []
    for index, row in enumerate(data[:1]):
        row["resume_link"] = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
        resume_path = download_file_from_google_drive(row["resume_link"])
        row["resume_review"] = get_resume_review(resume_path)

        row["github_repository_link"] = "https://github.com/madangopal16072000/fyle-interview-intern-backend"

        print(f"Index {index}: {row["full_name"]}")
        row["code_coverage"] = get_code_coverage(row["github_repository_link"])
        arr.append(row)
    return arr

        
        

if __name__ == '__main__':
    print('data job')
