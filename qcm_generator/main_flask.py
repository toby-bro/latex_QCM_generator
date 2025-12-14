import logging
import os

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from qcm_generator.main_cli import generate_subjects, parse_questions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

QUESTION_FILE = os.path.join(os.path.dirname(__file__), 'questions.txt')
QUESTION_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'questions-template.txt')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'subjects', 'images')
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}


def reload_questions(reset: bool = True) -> None:
    """Load the default questions template."""
    if os.path.exists(QUESTION_FILE):
        if reset:
            os.remove(QUESTION_FILE)
        else:
            return

    if os.path.exists(QUESTION_TEMPLATE_FILE):
        with open(QUESTION_TEMPLATE_FILE, encoding='UTF8') as template_file:
            template_content = template_file.read()
        with open(QUESTION_FILE, 'w', encoding='UTF8') as question_file:
            question_file.write(template_content)
    else:
        logging.warning('Template file not found. Cannot create questions.txt.')


@app.route('/')
def index() -> str:
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/questions', methods=['GET'])
def get_questions() -> tuple[str, int]:
    """Get the current questions content."""
    try:
        if not os.path.exists(QUESTION_FILE):
            reload_questions(reset=False)

        with open(QUESTION_FILE, encoding='UTF8') as file:
            content = file.read()
        return jsonify({'content': content}), 200
    except Exception as e:
        logging.error(f'Error loading questions: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions', methods=['POST'])
def save_questions() -> tuple[str, int]:
    """Save questions content."""
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(QUESTION_FILE, 'w', encoding='UTF8') as file:
            file.write(content)

        return jsonify({'message': 'Questions saved successfully'}), 200
    except Exception as e:
        logging.error(f'Error saving questions: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/reset', methods=['POST'])
def reset_questions() -> tuple[str, int]:
    """Reset questions to template."""
    try:
        reload_questions(reset=True)
        with open(QUESTION_FILE, encoding='UTF8') as file:
            content = file.read()
        return jsonify({'content': content, 'message': 'Questions reset successfully'}), 200
    except Exception as e:
        logging.error(f'Error resetting questions: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/validate', methods=['POST'])
def validate_questions() -> tuple[str, int]:
    """Validate questions format."""
    try:
        data = request.get_json()
        content = data.get('content', '')

        lines = content.split('\n')

        # Skip header lines
        header_lines = 0
        for line in lines:
            if not line.strip():
                break
            header_lines += 1

        raw_questions = lines[header_lines:]

        # Try to parse questions
        questions, choices = parse_questions(raw_questions)

        return jsonify({
            'valid': True,
            'message': f'Valid format: {len(questions)} questions found',
            'question_count': len(questions),
        }), 200
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': str(e),
        }), 400


@app.route('/api/generate', methods=['POST'])
def generate() -> tuple[str, int]:
    """Generate QCM PDFs."""
    try:
        data = request.get_json()
        content = data.get('content', '')

        # Save current content to questions file
        with open(QUESTION_FILE, 'w', encoding='UTF8') as file:
            file.write(content)

        # Generate subjects
        generate_subjects()

        # Get list of generated PDFs
        subjects_dir = os.path.join(os.path.dirname(__file__), 'subjects')
        pdf_files = [f for f in os.listdir(subjects_dir) if f.endswith('.pdf')]

        return jsonify({
            'message': 'Subjects generated successfully',
            'files': pdf_files,
        }), 200
    except Exception as e:
        logging.error(f'Error generating subjects: {e}')

        # Try to read debug log if it exists
        debug_log = None
        debug_log_path = os.path.join(os.path.dirname(__file__), 'debug.log')
        if os.path.exists(debug_log_path):
            try:
                with open(debug_log_path, encoding='UTF8') as log_file:
                    # Get last 50 lines or 2000 characters
                    log_content = log_file.read()
                    lines = log_content.split('\n')
                    debug_log = '\n'.join(lines[-50:])
                    if len(debug_log) > 2000:
                        debug_log = '...\n' + debug_log[-2000:]
            except Exception:
                pass

        return jsonify({
            'error': str(e),
            'logs': debug_log,
        }), 500


@app.route('/api/download/<filename>')
def download(filename: str) -> tuple[str, int] | str:
    """Download a generated PDF."""
    try:
        subjects_dir = os.path.join(os.path.dirname(__file__), 'subjects')
        file_path = os.path.join(subjects_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logging.error(f'Error downloading file: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/template')
def get_template() -> tuple[str, int]:
    """Get the template file content."""
    try:
        if not os.path.exists(QUESTION_TEMPLATE_FILE):
            return jsonify({'error': 'Template file not found'}), 404

        with open(QUESTION_TEMPLATE_FILE, encoding='UTF8') as file:
            content = file.read()
        return jsonify({'content': content}), 200
    except Exception as e:
        logging.error(f'Error loading template: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-image', methods=['POST'])
def upload_image() -> tuple[str, int]:
    """Upload an image file."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({'error': f'Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}'}), 400

        # Create images directory if it doesn't exist
        os.makedirs(IMAGES_DIR, exist_ok=True)

        # Save the file
        file_path = os.path.join(IMAGES_DIR, filename)
        file.save(file_path)

        # Return relative path for LaTeX (relative to subjects directory)
        relative_path = os.path.join('images', filename)

        return jsonify({
            'message': 'Image uploaded successfully',
            'path': relative_path,
            'filename': filename,
        }), 200
    except Exception as e:
        logging.error(f'Error uploading image: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health() -> tuple[str, int]:
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # Initialize questions file if it doesn't exist
    reload_questions(reset=False)

    # Create subjects directory if it doesn't exist
    subjects_dir = os.path.join(os.path.dirname(__file__), 'subjects')
    os.makedirs(subjects_dir, exist_ok=True)

    # Create images directory if it doesn't exist
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Run the Flask app
    # Use debug=False in production to avoid file watching issues
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
