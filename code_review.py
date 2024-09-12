import os
import subprocess
import tempfile
import shutil
from openai import OpenAI

client = OpenAI()

def clone_repo(repo_url, dest_dir):
    """Clone a git repository to the specified destination directory."""
    try:
        subprocess.run(['git', 'clone', repo_url, dest_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred cloning repo {repo_url}: {e}")
        return False
    return True

def get_diff(repo1_dir, repo2_dir):
    """Get the diff between two git repositories."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--no-index', repo1_dir, repo2_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error occurred when comparing repos: {e}")
        return None

def compare_repos(repo1_url, repo2_url):
    """Main function to compare two git repositories."""
    temp_dir = tempfile.mkdtemp()

    repo1_dir = os.path.join(temp_dir, 'repo1')
    repo2_dir = os.path.join(temp_dir, 'repo2')

    try:
        # Clone both repositories
        if not (clone_repo(repo1_url, repo1_dir) and clone_repo(repo2_url, repo2_dir)):
            return

        # Get the diff between the two repos
        diff_output = get_diff(repo1_dir, repo2_dir)

        return diff_output
    finally:
        # Clean up the temporary directories
        shutil.rmtree(temp_dir)

async def get_code_review(challenge_description, parent_repo_url, submission_repo_url):
    git_diff = compare_repos(parent_repo_url, submission_repo_url)
    prompt = f"""
    Challenge Description: {challenge_description}
    The following are the differences between the boilerplate code and the submission:
    Git diff - {git_diff}

    Based on the provided differences, evaluate the submission and provide a JSON output with scores for the following criteria (0-10 scale):

    implementation_closeness: How closely the submission matches the expected implementation. Check if all the points mentioned in challenge description is implemented in the git diff. If the git diff is almost the same or entirely different from challenge description, set this to 0.
    code_cleanliness: The overall cleanliness of the code, including formatting and readability.
    best_practices: Adherence to coding best practices.
    edge_cases: The handling of edge cases in the implementation.

    Output only the JSON and make sure the generated output can be parsed as a JSON.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": prompt},
        ]
    )
    
    relevance_score = response.choices[0].message.content.strip()
    return relevance_score

if __name__ == "__main__":
    challenge_description = '''
    There are 5 resources:
    - Users
    - Principal
    - Students
    - Teachers
    - Assignments
    5 Users ie. 1 Principal, 2 students and 2 teachers have already been created for you in the db fixture
    - A principal can view all the teachers
    - A principal can view all the assignments submitted and/or graded by teachers.
    - A principal can re-grade the assignments already graded by the teacher.
    - A student can create and edit a draft assignment
    - A student can list all his created assignments
    - A student can submit a draft assignment to a teacher
    - A teacher can list all assignments submitted to him
    - A teacher can grade an assignment submitted to him
    - Add missing APIs mentioned here and get the automated tests to pass
    - Add tests for grading API
    - Please be aware that intentional bugs have been incorporated into the application, leading to test failures. Kindly address and rectify these issues as part of the assignment.
    - All tests should pass
    - Get the test coverage to 94 percentage or above
    - There are certain SQL tests present inside tests/SQL/. You have to write SQL in following files:
        - count_grade_A_assignments_by_teacher_with_max_grading.sql
        - number_of_assignments_per_state.sql
    - Optionally, Dockerize your application by creating a Dockerfile and a docker-compose.yml file, providing clear documentation on building and running the application with Docker, to stand out in your submission
    ## Available APIs
    ### Auth
    - header: "X-Principal"
    - value: {"user_id":1, "student_id":1}
    For APIs to work you need a principal header to establish identity and context
    ### GET /student/assignments
    List all assignments created by a student
    ### POST /student/assignments
    Create an assignment
    ### POST /student/assignments/submit
    Submit an assignment
    ### GET /teacher/assignments
    List all assignments submitted to this teacher
    ### POST /teacher/assignments/grade
    Grade an assignment
    ## Missing APIs
    You'll need to implement these APIs
    ### GET /principal/assignments
    List all submitted and graded assignments
    ### GET /principal/teachers
    List all the teachers
    ### POST /principal/assignments/grade
    Grade or re-grade an assignment
    '''
    repo1_url = "https://github.com/fylein/fyle-interview-intern-backend"
    repo2_url = "https://github.com/atharvakinikar/fyle-interview-intern-backend"
    
    print(get_code_review(challenge_description, repo1_url, repo2_url))