import os
from flask import Flask, request, jsonify
from flask_cors import CORS  
from dotenv import load_dotenv
from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage
from excel_worker import excel_to_json
from data_job import run_data_job
import time

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route('/resume', methods=['GET'])
def resume():
    return jsonify({'data': get_resume_review('resume.pdf')}), 200

@app.route('/code-coverage', methods=['GET'])
def code_coverage():
    return jsonify({'data': get_code_coverage()})

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Check if a file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    # Get the jobId from form data
    job_id = request.form.get('jobId')
    
    if not job_id:
        return jsonify({'error': 'No jobId provided in the form data'}), 400

    # Validate the file is an Excel file
    if file and file.filename.endswith(('.xls', '.xlsx')):
        # Use jobId as the filename
        base, ext = os.path.splitext(file.filename)
        filename = f"{job_id}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Handle case where a file with the same name already exists
        if os.path.exists(file_path):
            timestamp = int(time.time())  # Use timestamp for uniqueness
            filename = f"{job_id}_{timestamp}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        try:
            data = excel_to_json(file_path)

            return jsonify({
                'message': 'File successfully processed',
                'data': data,
                'filename': filename
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=3000)
