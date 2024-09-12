import pandas as pd
import json


def excel_to_json(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Convert each row into a dictionary with meaningful keys
    data = []
    for index, row in df.iterrows():
        record = {
            "timestamp": row['Timestamp'].isoformat() if pd.notna(row['Timestamp']) else None,
            "email": row['Email'] if pd.notna(row['Email']) else None,
            "full_name": row['Full Name '].strip() if pd.notna(row['Full Name ']) else None,
            "contact_number": row['Contact Number'] if pd.notna(row['Contact Number']) else None,
            "github_repository_link": row['Github Repository Link'] if pd.notna(row['Github Repository Link']) else None,
            "test_screenshot_link": row['Screenshot with all tests passing and the test coverage report'] if pd.notna(row['Screenshot with all tests passing and the test coverage report']) else None,
            "time_to_complete_task": row['How much time did you take to complete the task?'] if pd.notna(row['How much time did you take to complete the task?']) else None,
            "video_introduction_link": row['Please record a video introducing yourself. We also want to hear your thoughts on your recently completed assignment. Keep the video under 2 minutes. Mention the following points in the video:\n1. Introduce yourself. You can include:\n      a. Personal details like name, education, hobbies, etc.      \n      b. Will you be available for a full-time internship for 6 months?\n2. What was the most challenging part of the assignment?\n3. If you were to change anything about the assignment, what would it be?'] if pd.notna(row['Please record a video introducing yourself. We also want to hear your thoughts on your recently completed assignment. Keep the video under 2 minutes. Mention the following points in the video:\n1. Introduce yourself. You can include:\n      a. Personal details like name, education, hobbies, etc.      \n      b. Will you be available for a full-time internship for 6 months?\n2. What was the most challenging part of the assignment?\n3. If you were to change anything about the assignment, what would it be?']) else None,
            "college_name": row['College Name'] if pd.notna(row['College Name']) else None,
            "year_of_passing": row['Year of Passing'] if pd.notna(row['Year of Passing']) else None,
            "resume_link": row['Resume'] if pd.notna(row['Resume']) else None,
            "available_for_full_time_internship": row['Can you confirm that you do not have any pre-existing commitments, such as attending daily classes, and that you will be able to devote 8 hours per day to work, given that this is a full-time internship?'] if pd.notna(row['Can you confirm that you do not have any pre-existing commitments, such as attending daily classes, and that you will be able to devote 8 hours per day to work, given that this is a full-time internship?']) else None,
            "ai_used_by_candidate": row['Did you use any AI tool such as ChatGPT, Gemini while completing the assignment?'] if pd.notna(row['Did you use any AI tool such as ChatGPT, Gemini while completing the assignment?']) else None,
            "application_state": row['State'] if pd.notna(row['State']) else None,
            "slack_reference": row['Slack Ref'] if pd.notna(row['Slack Ref']) else None,
            "graded_by": row['Graded by'] if pd.notna(row['Graded by']) else None,
        }
        data.append(record)

    
    return data


if __name__ == "__main__":
    excel_file = "backend.xlsx"
    data = excel_to_json(excel_file)
    with open('excel_output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
