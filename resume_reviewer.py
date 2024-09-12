from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from pdf_utils import download_file_from_google_drive
import json
import re
import pdfx
from dotenv import load_dotenv
load_dotenv()

pdf_url = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
job_desc = """
    Backend Development Work From Home Internship
    Selected intern's day-to-day responsibilities include:

    1. Working on backend modules using technologies like Python, flask framework, etc.
    2. Working on building and maintaining efficient thoroughly tested RESTful APIs
    3. Working on relational databases such as PostgreSQL, etc.
    4. Working on writing tests, fixing broken tests for any new feature (pytest)
    5. Working on code versioning and containerization tools such as Git, Docker, etc.
    6. Working on interesting technical challenges in a fast-paced environment
    7. Taking ownership of product features from conception to implementation, testing deployment, and support
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0)

def extract_urls_email_mobile(pdf_path: str):
    pdf = pdfx.PDFx(pdf_path)
    urls = pdf.get_references_as_dict()
    
    http_urls = []
    emails = []
    mobile_numbers = []
    
    email_pattern = r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    mobile_pattern = r'(?:\+91|91)?[7-9]\d{9}'

    for url_list in urls.values():
        for url in url_list:
            if url.startswith('http://') or url.startswith('https://'):
                http_urls.append(url)
            email_match = re.match(email_pattern, url)
            if email_match:
                emails.append(email_match.group(1))
            mobile_match = re.search(mobile_pattern, url)
            if mobile_match:
                mobile_numbers.append(mobile_match.group())
    
    return {
        'http_urls': http_urls,
        'emails': emails,
        'mobile_numbers': mobile_numbers
    }

def extract_and_parse_json(input_string: str) -> dict:
    try:
        json_match = re.search(r'\{.*\}', input_string, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed_json = json.loads(json_str)
            return parsed_json
        else:
            return { "content": input_string }
    
    except json.JSONDecodeError:
        return { "content": input_string }
    except Exception as e:
        print(f"An error occurred: {e}")
        return { "content": input_string }

def write_to_file(file_path: str, content: str, mode: str = 'w') -> None:
    try:
        with open(file_path, mode) as file:
            file.write(content)
        print(f"Content successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def llm_convert_pdf_resume_to_json(pdf_path: str):
    loader = PyPDFLoader(file_path=pdf_path)
    resume_pages = loader.load()
    resume = ''
    for page in resume_pages:
        resume += page.page_content
    
    parse_template = """
      I want you to give a JSON as an output, which I can pass as input to another function.
      The JSON object should contain the following properties: 
      \n1. name (name of candidate)
      \n2. languages (array of name of languages spoken by candidate, null if not found)
      \n3. skills (array of name of skills found in resume)
      \n4. experience (array of type object with 3 properties 'company' (name of company), 'position' (position in that company), 'work_done' (string summary of work done in that company))
      \n5. projects (array of type object with 3 property 'name', 'summary', 'tech_used' (array of name of technologies used, ex: ['JavaScript', 'Flask']))
      \n6. education (array of type object with 5 properties 'course_name', 'college_or_uni', 'start_year', 'end_year', 'cgpa_or_percentage'

      \nYou should extract all this data yourself from below resume and give me JSON output without any other text.
      \nI repeat, do not give any extra sentence, word or character in the output apart from the JSON.
      Your output should start with `{{` and end with `}}`
      \n{resume}
    """

    parse_prompt_template = PromptTemplate(
        input_variables=["resume"],
        template=parse_template, 
    )

    chain = parse_prompt_template | llm
    res = chain.invoke(input={"resume": resume})
    parsed_resume = extract_and_parse_json(res.content)
    data = extract_urls_email_mobile(pdf_path)
    parsed_resume["emails"] = data["emails"]
    parsed_resume["urls"] = data["http_urls"]
    parsed_resume["mobile_numbers"] = data["mobile_numbers"]
    return parsed_resume

def llm_review_resume_on_job_desc(json_resume, job_desc):
    resume = json.dumps(json_resume)
    parse_template = """
    Imagine you are an expert at reviewing resume. Given a job description and resume details,
    I want you to give me a JSON object which I can pass to another function.
    The JSON object should contain the following properties: 
    1. skill_match (Score out of 5 whether the candidate has the skills we need for the job.)
    2. relevant_experience (Score out of whether their past work or projects is relevant to the job, like preferring candidates with web app experience over machine learning experience if we’re hiring for backend roles.)
    3. summary (Objective summary of the candidate, showing whether he is fit or not for the job along with proofs)
    4. overall_rating (Overall rating out of 5, where 5 is best fit.)

    The job description is 
    ```{job_desc}```.
    
    The candidate details are {resume}.

    \nYou should give me JSON output without any other text.
    \nI repeat, do not give any extra sentence, word or character in the output apart from the JSON.
    Your output should start with `{{` and end with `}}`
    """
    parse_prompt_template = PromptTemplate(
    input_variables=["resume", "job_desc"],
    template=parse_template, 
    )

    chain = parse_prompt_template | llm
    res = chain.invoke(input={"resume": resume, "job_desc": job_desc})
    parsed_response = extract_and_parse_json(res.content) 
    return parsed_response

def get_resume_review(pdf_url: str, data = {}):
    print("resume reviewer function called!")
    pdf_path = download_file_from_google_drive(pdf_url)
    parsed_resume = llm_convert_pdf_resume_to_json(pdf_path)
    resume_review = llm_review_resume_on_job_desc(parsed_resume, job_desc)
    data['resume'] = parsed_resume
    data['resume_review'] = resume_review
    # write_to_file('results/' + parsed_resume["name"] + '.json', json.dumps(obj, indent=4))
    print("resume reviewer terminated!")
    return data

if __name__ == "__main__":
    res = get_resume_review(pdf_url)
    print(res)
