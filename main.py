import base64
import xlrd
import pandas as pd
import openpyxl

from . import db
from flask import Flask
from . import dummy
app = Flask(__name__)

@app.route("/upload")
def hello_world():
    xlStr = dummy.d
    xlDecoded = base64.b64decode(xlStr)
    xlFile = open('temp.xlsx', 'wb')
    xlFile.write(xlDecoded)
  
    dataframe1 = pd.read_excel('temp.xlsx')

    # print(dataframe1)
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
        
        #check for links presence or duplication
        db.add_submission(
            timestamp=timestamp,
            full_name=full_name,
            email=email,
            contact_number=contact_number,
            github_repo_link=github_repo_link,
            time_taken=time_taken,
            college_name=college_name,
            year_of_passing=year_of_passing,
            resume_link=resume_link
        )
        

        print(timestamp,full_name,email,contact_number,github_repo_link, time_taken,college_name,year_of_passing,resume_link)

    return "successsss"


    
 