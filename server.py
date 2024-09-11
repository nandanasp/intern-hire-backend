import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS  
from dotenv import load_dotenv
from resume_reviewer import get_resume_review
from code_coverage import get_code_coverage

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file and file.filename.endswith(('.xls', '.xlsx')):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            df = pd.read_excel(file_path)
            # run jobs here
            
            return jsonify({
                'message': 'File successfully processed',
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=3000)
