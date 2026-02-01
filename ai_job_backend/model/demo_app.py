"""
AI Job Assistant - Standalone Demo Application
Flask application for testing/demo purposes.
This is a standalone demo app - the main backend uses FastAPI routes.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging
import os
from pathlib import Path

# Import the data science module functions
from datascientist.api_integration import (
    analyze_resume_endpoint,
    generate_answer_endpoint,
    scrape_job_description_endpoint
)
from datascientist.utils import setup_logging, get_config

# Set up logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Validate configuration
config = get_config()
if not config.validate():
    logger.warning("OPENAI_API_KEY not set. LLM features will not work.")


# HTML template for the demo page
DEMO_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Job Assistant - Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .result h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .result pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
        }
        .error {
            background: #fee;
            border-left-color: #e74c3c;
            color: #c0392b;
        }
        .success {
            background: #efe;
            border-left-color: #27ae60;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 12px 24px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-weight: 600;
            color: #666;
        }
        .tab.active {
            background: white;
            color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Job Assistant</h1>
            <p>Resume Analysis & Tailored Answer Generation</p>
        </div>

        <div class="card">
            <div class="tabs">
                <button class="tab active" onclick="showTab('scrape')">Scrape Job</button>
                <button class="tab" onclick="showTab('analyze')">Analyze Resume</button>
                <button class="tab" onclick="showTab('generate')">Generate Answer</button>
            </div>

            <!-- Scrape Job Tab -->
            <div id="scrape" class="tab-content active">
                <h2>Scrape Job Description</h2>
                <form onsubmit="scrapeJob(event)">
                    <div class="form-group">
                        <label for="job_url_scrape">Job Posting URL:</label>
                        <input type="url" id="job_url_scrape" placeholder="https://linkedin.com/jobs/view/..." required>
                    </div>
                    <button type="submit">Scrape Job Description</button>
                </form>
                <div id="scrape_result"></div>
            </div>

            <!-- Analyze Resume Tab -->
            <div id="analyze" class="tab-content">
                <h2>Analyze Resume Against Job</h2>
                <form onsubmit="analyzeResume(event)">
                    <div class="form-group">
                        <label for="resume_text">Resume Text:</label>
                        <textarea id="resume_text" placeholder="Paste your resume text here..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="job_url_analyze">Job Posting URL:</label>
                        <input type="url" id="job_url_analyze" placeholder="https://linkedin.com/jobs/view/..." required>
                    </div>
                    <button type="submit">Analyze Resume</button>
                </form>
                <div id="analyze_result"></div>
            </div>

            <!-- Generate Answer Tab -->
            <div id="generate" class="tab-content">
                <h2>Generate Tailored Answer</h2>
                <form onsubmit="generateAnswer(event)">
                    <div class="form-group">
                        <label for="question">Application Question:</label>
                        <input type="text" id="question" placeholder="Why are you a good fit for this position?" required>
                    </div>
                    <div class="form-group">
                        <label for="work_history">Work History:</label>
                        <textarea id="work_history" placeholder="5 years as Software Engineer at Tech Corp..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="skills">Skills (comma-separated):</label>
                        <input type="text" id="skills" placeholder="Python, Django, PostgreSQL, AWS" required>
                    </div>
                    <div class="form-group">
                        <label for="education">Education:</label>
                        <input type="text" id="education" placeholder="BS in Computer Science from State University" required>
                    </div>
                    <div class="form-group">
                        <label for="job_url_generate">Job Posting URL:</label>
                        <input type="url" id="job_url_generate" placeholder="https://linkedin.com/jobs/view/..." required>
                    </div>
                    <button type="submit">Generate Answer</button>
                </form>
                <div id="generate_result"></div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs and contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Show selected tab
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        function showLoading(elementId) {
            document.getElementById(elementId).innerHTML = '<div class="loading">⏳ Processing... Please wait.</div>';
        }

        function showResult(elementId, data, isError = false) {
            const resultDiv = document.getElementById(elementId);
            const className = isError ? 'result error' : 'result success';
            resultDiv.innerHTML = `<div class="${className}"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
        }

        async function scrapeJob(event) {
            event.preventDefault();
            const jobUrl = document.getElementById('job_url_scrape').value;
            showLoading('scrape_result');

            try {
                const response = await fetch('/api/job/scrape', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_url: jobUrl })
                });
                const data = await response.json();
                showResult('scrape_result', data, !data.success);
            } catch (error) {
                showResult('scrape_result', { error: error.message }, true);
            }
        }

        async function analyzeResume(event) {
            event.preventDefault();
            const resumeText = document.getElementById('resume_text').value;
            const jobUrl = document.getElementById('job_url_analyze').value;
            showLoading('analyze_result');

            try {
                const response = await fetch('/api/resume/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume_text: resumeText, job_url: jobUrl })
                });
                const data = await response.json();
                showResult('analyze_result', data, !data.success);
            } catch (error) {
                showResult('analyze_result', { error: error.message }, true);
            }
        }

        async function generateAnswer(event) {
            event.preventDefault();
            const question = document.getElementById('question').value;
            const workHistory = document.getElementById('work_history').value;
            const skills = document.getElementById('skills').value.split(',').map(s => s.trim());
            const education = document.getElementById('education').value;
            const jobUrl = document.getElementById('job_url_generate').value;
            showLoading('generate_result');

            const userProfile = {
                work_history: workHistory,
                skills: skills,
                education: education,
                additional_info: ''
            };

            try {
                const response = await fetch('/api/generate/answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question, user_profile: userProfile, job_url: jobUrl })
                });
                const data = await response.json();
                showResult('generate_result', data, !data.success);
            } catch (error) {
                showResult('generate_result', { error: error.message }, true);
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the demo page."""
    return render_template_string(DEMO_PAGE)


@app.route('/api/resume/analyze', methods=['POST'])
def analyze_resume():
    """POST /api/resume/analyze - Analyzes a resume against a job description."""
    try:
        data = request.json
        
        if not data or 'resume_text' not in data or 'job_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: resume_text, job_url'
            }), 400
        
        logger.info(f"Resume analysis request for job: {data['job_url']}")
        result = analyze_resume_endpoint(
            resume_text=data['resume_text'],
            job_url=data['job_url']
        )
        
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in analyze_resume endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/generate/answer', methods=['POST'])
def generate_answer():
    """POST /api/generate/answer - Generates a tailored answer to an application question."""
    try:
        data = request.json
        
        if not data or 'question' not in data or 'user_profile' not in data or 'job_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: question, user_profile, job_url'
            }), 400
        
        logger.info(f"Answer generation request for job: {data['job_url']}")
        result = generate_answer_endpoint(
            question=data['question'],
            user_profile=data['user_profile'],
            job_url=data['job_url']
        )
        
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in generate_answer endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/job/scrape', methods=['POST'])
def scrape_job():
    """POST /api/job/scrape - Scrapes a job description from a URL."""
    try:
        data = request.json
        
        if not data or 'job_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: job_url'
            }), 400
        
        logger.info(f"Job scraping request for: {data['job_url']}")
        result = scrape_job_description_endpoint(data['job_url'])
        
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in scrape_job endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'job-assistant-data-science',
        'version': '1.0.0'
    }), 200


@app.route('/api/status', methods=['GET'])
def status():
    """Get service status and configuration."""
    config = get_config()
    return jsonify({
        'status': 'running',
        'openai_configured': bool(config.OPENAI_API_KEY),
        'selenium_enabled': config.USE_SELENIUM,
        'model': config.OPENAI_MODEL
    }), 200


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting AI Job Assistant demo server on http://{host}:{port}")
    logger.info(f"Open http://localhost:{port} in your browser to use the demo interface")
    
    app.run(debug=True, host=host, port=port)
