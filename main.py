import base64
from datetime import datetime
import xlrd
import pandas as pd
import openpyxl

from . import db
from flask import Flask
from . import dummy
app = Flask(__name__)

@app.route("/upload")
def hello_world():
    xlStr = "dummy_string"
    xlDecoded = base64.b64decode(xlStr)
    xlFile = open('temp.xlsx', 'wb')
    xlFile.write(xlDecoded)
  
    dataframe1 = pd.read_excel('temp.xlsx')

    print(dataframe1)
    rows, cols = dataframe1.shape
    for row in range(0, rows):
        timestamp = dataframe1.loc[row,'Timestamp']
        full_name = dataframe1.loc[row,'Full Name ']
        email = dataframe1.loc[row,'Email']
        contact_number = dataframe1.loc[row,'Contact Number']
        github_repo_link = dataframe1.loc[row,'Github Repository Link']
        time_taken = dataframe1.loc[row,'How much time did you take to complete the task?']
        college_name = dataframe1.loc[row,'College Name']
        year_of_passing = dataframe1.loc[row,'Year of Passing']
        resume_link = dataframe1.loc[row,'Resume']
        video_link = dataframe1.loc[row,'Video link']
        current_hiring_eligibility = True
        reviews = []

        if str(github_repo_link)=="nan" or str(video_link) == 'nan' or str(resume_link) == 'nan':
            current_hiring_eligibility = False
            reviews.append({
                "description" : "Urls are not correctly provided",
                "updated_at": datetime.now()
            })
        
        if db.find_submission_by_github_repo_link(github_repo_link) is not None:
            current_hiring_eligibility = False
            reviews.append({
                "description" : "Github repo link duplicated",
                "updated_at": datetime.now()
            })

        if db.find_submission_by_video_link(video_link) is not None:
            current_hiring_eligibility = False
            reviews.append({
                "description" : "Video link duplicated",
                "updated_at": datetime.now()
            })

        #check for links presence or duplication
        candidate_id = db.add_submission(
            timestamp=timestamp,
            full_name=full_name,
            email=email,
            contact_number=contact_number,
            github_repo_link=github_repo_link,
            time_taken=time_taken,
            college_name=college_name,
            year_of_passing=year_of_passing,
            resume_link=resume_link,
            current_hiring_eligibility=current_hiring_eligibility,
            reviews = reviews
        )

        print(timestamp,full_name,email,contact_number,github_repo_link, time_taken,college_name,year_of_passing,resume_link)

    return "successsss"


    
@app.route("/submissions",  methods = ['GET'])
def list_submissions():
    if request.method == 'GET':
        all_submissions = []
        candidates = db.get_all_candidates()
        for candidate in candidates:
            for submission in candidate["submissions"]:
                all_submissions.append(submission)
        return all_submissions
