import logging
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from answer import RAGController
from ingestion import IngestionPipeline
from config import RESUME_DIR

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskAPI")

# Initialize Helpers
rag_engine = RAGController()
ingestion_pipeline = IngestionPipeline()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/resumes', methods=['GET'])
def list_resumes():
    """Returns a list of all available PDFs to populate the dropdown."""
    try:
        files = [f for f in os.listdir(RESUME_DIR) if f.endswith('.pdf')]
        return jsonify({"resumes": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Handles file upload and immediate ingestion."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        save_path = RESUME_DIR / filename
        
        # 1. Save File
        file.save(save_path)
        logger.info(f"File saved: {save_path}")
        
        # 2. Trigger Ingestion (This updates the Vector DB)
        success = ingestion_pipeline.ingest_new_file(save_path)
        
        if success:
            return jsonify({"message": "File uploaded and ingested successfully", "filename": filename})
        else:
            return jsonify({"error": "Ingestion failed (empty text?)"}), 500
            
    return jsonify({"error": "Invalid file type. Only PDF allowed."}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze_job():
    data = request.json
    jd_text = data.get('jd_text', '')
    resume_filename = data.get('resume_filename', '') # New Parameter

    if not jd_text or not resume_filename:
        return jsonify({"error": "Both JD and Resume selection are required."}), 400

    try:
        result = rag_engine.process_application(jd_text, resume_filename)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Analysis Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)