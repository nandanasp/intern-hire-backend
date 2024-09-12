from .setup import db 
from marshmallow import Schema, fields, ValidationError
from bson import ObjectId

candidates = db.candidates 


class CandidateSchema(Schema):
    fullname = fields.Str()
    email = fields.Str()
    contact_number = fields.Str()
    github_repository_link = fields.Str()
    test_screenshot_link = fields.Str()
    video_introduction_link = fields.Str()
    timestamp = fields.Str()
    college_year = fields.Str()
    year_of_passing = fields.Str()
    time_to_complete_task = fields.Str()
    resume_link = fields.Str() 
    available_for_full_internship_link = fields.Str() 
    ai_used_by_candidate = fields.Str()
    application_state = fields.Str()
    slack_reference = fields.Str()
    graded_by = fields.Str()


candidate_schema = CandidateSchema()

def get_candidate(candidate_id):
    candidate = candidates.find_one({"email": 'cshekharmshr2407@gmail.com'})
    return candidate



def update_status(candidate_id, status):
    try:
        result = candidates.update_one({'email': 'cshekharmshr2407@gmail.com'}, {'$set' : {
            'submission.0.status': status
        }})

        # Check if any document was updated
        if result.matched_count > 0:
            print("document updated successfully")
        else:
            print("no document found with given id")
    except Exception as e:
        print(f"Error : {e}")


def update_candidate(candidate_id, **kwargs):
    try:
        # Construct the update dictionary
        update_fields = {f'submission.0.{key}': value for key, value in kwargs.items()}

        result = candidates.update_one(
            {'email': 'cshekharmshr2407@gmail.com'},
            {'$set': update_fields}
        )

        if result.matched_count > 0:
            print('document updated successfully')
        else:
            print('no document found with given id')
    except Exception as e:
        print(f"Error: {e}")