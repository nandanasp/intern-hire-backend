from .setup import db 
from marshmallow import Schema, fields

jobs = db.jobposts 

class JobSchema(Schema):
    job_id = fields.Str()
    job_title = fields.Str()
    job_domain = fields.Str()
    job_desc = fields.Str()
    code_coverage = fields.Str()
    code_review_score = fields.Str()
    resume_score = fields.Str()
    base_repo_url = fields.Str()
    is_active = fields.Bool()

job_schema = JobSchema()

def get_jobs(job_id):
    jobpost = jobs.find_one({job_id: job_id})
    return jobpost