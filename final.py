from dotenv import load_dotenv
import os 
import requests 
import zipfile 
from langchain_community.document_loaders import TextLoader
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import TokenTextSplitter
from langchain_groq import ChatGroq
import time 
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json',
    "X-GitHub-Api-Version" : "2022-11-28"
}

# Ensure the current directory is writable
current_directory = os.getcwd()
log_file_path = os.path.join(current_directory, "workflow_logs.zip")
extracted_folder = 'workflow_logs_extracted'


class TestResultSchema(BaseModel):
    """Results of Test Execution"""
    coverage: float = Field(description="coverage percentage")
    required_coverage: float = Field(description="Required percentage of coverage")
    total_tests: int = Field(description="Total number of tests")
    passed_tests: int = Field(description="Number of passed tests")
    failed_tests: int = Field(description="Total number of tests failed")
    skipped_tests: int = Field(description="Number of Skipped tests")
    total_lines: int = Field(description="Total number of lines")
    covered_lines: int = Field(description="Total covered lines")
    missed_lines: int = Field(description="Total number of missed lines")
    summary: str = Field(description="Detailed Summary of tests results",
                         example="The test results show that all 24 tests have passed. The coverage report shows that 96.45% of the code has been covered by the tests. The required coverage percentage was 80%, which has been reached. The missing lines are mainly in the exception handling and assignment models.")


class TestResultSchema2(BaseModel):
    """Results of Test Execution"""
    coverage: float = Field(description="coverage percentage")
    required_coverage: float = Field(description="Required percentage of coverage")
    total_tests: int = Field(description="Total number of tests")
    passed_tests: int = Field(description="Number of passed tests")
    failed_tests: int = Field(description="Total number of tests failed")


class TestResult:

    def __init__(self, llm, github_repo) -> None:
        self.llm = llm 
        self.github_repo = github_repo
        owner_repo = self.extract_owner_repo()
        url = f"https://api.github.com/repos/{owner_repo}/actions/runs"

        response = requests.get(url, headers=headers)
        resp_js = response.json()
        self.run_status = resp_js['workflow_runs'][0]['conclusion']
        self.logs_url = resp_js['workflow_runs'][0]['logs_url']

    def extract_owner_repo(self):
        parts = self.github_repo.rstrip('/').split('/')
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
        else:
            return None

    def get_status(self):
        return self.run_status
    
    def process(self):
        # Download the logs
        logs_response = requests.get(url=self.logs_url, headers=headers)

        if logs_response.status_code == 200:
            # Save logs to a file
            try:
                with open(log_file_path, "wb") as f:
                    f.write(logs_response.content)
                print(f"Logs downloaded successfully and saved to {log_file_path}")
            except Exception as e:
                print(f"An error occurred while saving or extracting logs: {e}")

        else:
            print(f'Failed to download logs: {logs_response.status_code}')
            print(logs_response.text)

        # Path to the downloaded ZIP file
        zip_file_path = os.path.join(os.getcwd(), f"workflow_logs.zip")

        # Create the directory where files will be extracted
        os.makedirs(extracted_folder, exist_ok=True)

        # Extract the ZIP file
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_folder)
            print(f"Logs extracted to the '{extracted_folder}' directory.")
        except zipfile.BadZipFile:
            print("Error: The file is not a ZIP file or is corrupted.")
        except FileNotFoundError:
            print(f"Error: The file {zip_file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_summary(self):
        loader = TextLoader(f"{extracted_folder}/build/6_Test with pytest.txt")
        docs = loader.load()

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """   
                    You are an expert assistant specialized in analyzing test execution logs from GitHub Actions. 
                    Your task is to extract a concise summary of the test results, including key metrics such as total tests, passed tests, failed tests, skipped tests, code coverage percentage, and any missing lines or files. 
                    If the provided logs do not contain relevant information, do not extract anything.
                    """
                ),
                ("human", "{context}"),
            ]
        )

        text_splitter = text_splitter = TokenTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
        )
        texts = text_splitter.split_text(docs[0].page_content)

        extractor = prompt | self.llm.with_structured_output(
            schema=TestResultSchema2,
            include_raw=False
        )
        res = extractor.invoke({"context": texts[-4:]})
        return res
    

if __name__ == '__main__':
    os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
    llm = ChatGroq(model="llama3-70b-8192")
    github_repo1 = 'https://github.com/mgs222324/fyle-interview-intern-backend'
    github_repo2 = 'https://github.com/madangopal16072000/fyle-interview-intern-backend'

    repo_list = [github_repo1, github_repo2]

    for repo in repo_list:
        tr = TestResult(llm, github_repo = repo)

        # call get status to status of github action run 
        status = tr.get_status()
        # call process to process logs
        tr.process()

        # call summary to get summary result
        print(tr.get_summary().dict())