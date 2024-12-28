from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pdfplumber
import os
from transformers import pipeline

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# pre-trained NLP model for question answering
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased", tokenizer="distilbert-base-uncased")

# Endpoint to upload PDF
def extract_text_from_pdf(file_path):
    extracted_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Save the text to a file or database for chatbot usage
    text_file_path = file_path.replace('.pdf', '.txt')
    with open(text_file_path, 'w') as text_file:
        text_file.write(extracted_text)

    return jsonify({"message": "File uploaded and processed successfully", "text_file": text_file_path}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get("question")
    context_file = data.get("context_file")

    if not question or not context_file:
        return jsonify({"error": "Question and context_file are required"}), 400

    if not os.path.exists(context_file):
        return jsonify({"error": "Context file not found"}), 404

    with open(context_file, 'r') as file:
        context = file.read()

    # Use the NLP model to generate an answer
    result = qa_pipeline(question=question, context=context)
    return jsonify({"answer": result['answer'], "score": result['score']}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
