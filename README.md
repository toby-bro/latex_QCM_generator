# LaTeX QCM Generator

Generates anti-cheating QCM PDFs in LaTeX from a document of questions and correct answers.

## Description

This project automatically generates multiple-choice questionnaires (QCM) in LaTeX. The script takes a text file containing questions and possible answers and generates several versions of the QCM to minimize cheating risks.

## Features

- **Web Interface**: Modern Flask-based web application with an intuitive editor
- Generates multiple versions of QCM from a question file
- Shuffles questions and answers for each version
- Automatically creates PDF files using `pdflatex`
- Supports LaTeX math syntax for questions
- **Docker support** for easy deployment
- Real-time validation of question format

## Prerequisites

### For Web Application (Recommended)

- [Docker](https://www.docker.com/get-started) and Docker Compose (easiest option)

**OR**

- [Python 3.12+](https://www.python.org/downloads/)
- [LaTeX](https://www.latex-project.org/get/) (with `pdflatex`)

### For CLI/GUI (Legacy)

- [Python 3.12+](https://www.python.org/downloads/)
- [LaTeX](https://www.latex-project.org/get/)

## Installation & Usage

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker:

```sh
# Clone the repository
git clone https://github.com/toby-bro/latex_QCM_generator.git
cd latex_QCM_generator

# Build and run with Docker Compose
docker-compose up -d

# Access the web application at http://localhost:5000
```

To stop the application:

```sh
docker-compose down
```

### Option 2: Local Flask Installation

```sh
# Clone the repository
git clone https://github.com/toby-bro/latex_QCM_generator.git
cd latex_QCM_generator

# Install dependencies
pip install .

# Run the Flask application
python -m qcm_generator.main_flask

# Access the web application at http://localhost:5000
```

### Option 3: CLI (Legacy)

1. Create a `questions.txt` file in the project root containing the following information:

    ```txt
    QCM Title
    Author
    School
    Course
    Date

    Q First question?
    Answer A
    Answer B
    Answer C

    Q Second question?
    Answer A
    Answer B
    Answer C
    ```

2. Run the Python script from CLI:

    ```sh
    python qcm_generator/main_cli.py
    ```

3. The generated PDF files will be located in the `subjects` directory.

### Option 4: GUI (Legacy)

Provided the required packages are installed, double-click on [main_gui.py](qcm_generator/main_gui.py) or run:

```sh
python qcm_generator/main_gui.py
```

## Web Application Features

The Flask web interface provides:

- **Live Editor**: Edit questions with syntax highlighting for LaTeX math
- **Validation**: Real-time validation of question format
- **PDF Generation**: Generate multiple exam versions with shuffled questions
- **Download**: Download individual generated PDF files
- **Template Reset**: Reset to default question template

### Question Format

The web editor expects questions in this format:

```
QCM Title
Author Name
School Name
Course Name
Date

Q What is $2 + 2$?
3
4
5
6

Q Calculate $\sqrt{16}$
2
3
4
5
```

**Header (first 5 non-empty lines):**

- Line 1: QCM Title
- Line 2: Author
- Line 3: School
- Line 4: Course
- Line 5: Date

**Questions:**

- Start each question with `Q` followed by a space and the question text
- List possible answers below (one per line)
- Separate questions with blank lines
- Support LaTeX math: `$x^2$` or `\[E=mc^2\]`

## Docker Details

### Building the Image

```sh
docker build -t qcm-generator .
```

### Running Manually

```sh
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/qcm_generator/subjects:/app/qcm_generator/subjects \
  -v $(pwd)/qcm_generator/questions.txt:/app/qcm_generator/questions.txt \
  --name qcm-generator \
  qcm-generator
```

### Viewing Logs

```sh
docker-compose logs -f
```

## Development

### For Development Setup

Clone the repository and install dependencies:

```sh
git clone https://github.com/toby-bro/latex_QCM_generator.git
cd latex_QCM_generator
make install
```

### API Endpoints

The Flask application exposes these REST API endpoints:

- `GET /` - Web interface
- `GET /api/questions` - Get current questions
- `POST /api/questions` - Save questions
- `POST /api/questions/reset` - Reset to template
- `POST /api/questions/validate` - Validate question format
- `POST /api/generate` - Generate PDF subjects
- `GET /api/download/<filename>` - Download generated PDF
- `GET /health` - Health check

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
