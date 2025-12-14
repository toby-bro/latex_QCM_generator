import logging
import os
import re
import subprocess
import threading
from random import sample

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

script_dir = os.path.dirname(__file__)
num_different_subjects = 4

latex_top = r"""
\documentclass[12pt]{{article}}
\usepackage{{ae,lmodern}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{geometry}}
\usepackage{{amsmath}}
\usepackage[french]{{babel}}
\usepackage{{amsfonts}}
\usepackage{{dsfont}}
\usepackage[normalem]{{ulem}}
\usepackage{{amssymb}}
\usepackage{{xcolor}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{graphicx}}
\usepackage{{lastpage}}
\geometry{{hmargin=3cm,vmargin=2.5cm}}
\usepackage{{setspace}}
\author{{{author}}}
\pagestyle{{fancy}}
\renewcommand\headrulewidth{{1pt}}
\fancyhead[L]{{\textbf{{{subject}}}}}
\fancyhead[R]{{{school}}}
\fancyfoot[C]{{\thepage /\pageref{{LastPage}}}}
\title{{{title}}}
\date{{{date}}}
\begin{{document}}
\maketitle
\onehalfspacing
"""


class Question:
    possible_answers: list[str]
    question: str

    def __init__(self, title: str, possible_answers: list[str]):
        self.question = title
        self.possible_answers = possible_answers

    def mix_answers(self) -> None:
        order = sample(list(range(len(self.possible_answers))), len(self.possible_answers))
        self.possible_answers = [self.possible_answers[i] for i in order]


def path(rel_path: str) -> str:
    return os.path.join(script_dir, rel_path)


def read_file(file_path: str) -> list[str]:
    with open(file_path, 'r', encoding='UTF8') as file:
        return file.readlines()


def write_file(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='UTF8') as file:
        file.write(content)


def parse_questions(raw_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    questions: list[str] = []
    choices: list[list[str]] = []
    current_question: str | None = None

    raw_lines = [re.sub(r'(?<!\\)%', r'\%', line).strip() for line in raw_lines]

    for line in raw_lines:
        if line.startswith('Q'):
            try:
                current_question = line[1:].strip().split(' ', 1)[1]
            except IndexError as e:
                logging.error(f'Invalid question format: {line}')
                raise ValueError(
                    f'Invalid question format: \n{line}.\n'
                    'Ensure questions start with "Q" followed by a space and then the title of the question.',
                ) from e
            questions.append(current_question)
            choices.append([])
        elif current_question is not None and line:
            choices[-1].append(line)

    if not questions:
        raise ValueError('No questions found. Ensure lines start with "Q" for questions.')

    return questions, choices


# Regex pattern to match relative \includegraphics (with or without options)
INCLUDE_PATTERN = r'\\includegraphics(?:\[(.*?)\])?\{([^:/].*?)\}'


def transform_include_path(match: re.Match[str]) -> str:
    options = match.group(1) if match.group(1) else ''
    relative_path = match.group(2)

    # Check if the path is an absolute Windows path
    if re.match(r'^[a-zA-Z]:(\\|/)', relative_path):
        new_path = relative_path
    else:
        new_path = f'../../{relative_path}'

    if options:
        return f'\\includegraphics[{options}]{{{new_path}}}'
    return f'\\includegraphics{{{new_path}}}'


def transform_image_includes(latex_content: str) -> str:
    return re.sub(INCLUDE_PATTERN, transform_include_path, latex_content)


def shuffle_questions(questions: list[Question], num_subjects: int) -> list[list[Question]]:
    return [sample(questions, len(questions)) for _ in range(num_subjects)]


def clean() -> None:
    base_path = os.path.dirname(__file__)
    full_output_dir = os.path.join(base_path, 'subjects')
    extensions = ['.tex', '.log', '.aux', '.out']
    aux_files_dir = os.path.join(full_output_dir, 'aux_files')

    for root, _, files in os.walk(full_output_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                os.remove(os.path.join(root, file))

    if os.path.isdir(aux_files_dir):
        for root, dirs, files in os.walk(aux_files_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(aux_files_dir)


def create_latex_files(liste_qcm: list[list[Question]], latex_top: str) -> None:
    aux_dir = path('subjects/aux_files')
    output_dir = path('subjects')

    os.makedirs(aux_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    threads = []
    errors = []

    def thread_wrapper(latex_top: str, output_dir: str, i: int, qcm: list[Question]) -> None:
        try:
            generate_tex_file(latex_top, output_dir, i, qcm)
        except Exception as e:
            errors.append((i, e))

    for i, qcm in enumerate(liste_qcm):
        thread = threading.Thread(target=thread_wrapper, args=(latex_top, output_dir, i, qcm))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # If any thread had an error, raise the first one
    if errors:
        subject_num, error = errors[0]
        raise RuntimeError(f'Failed to generate subject {subject_num + 1}: {error}') from error


def generate_tex_file(latex_top: str, output_dir: str, i: int, qcm: list[Question]) -> None:
    for quest in qcm:
        quest.mix_answers()

    tq = f'{latex_top}\n\\textsc{{subject {i + 1}}}\n\\begin{{enumerate}}\n'

    for question in qcm:
        tq += f'\n\\item {question.question}'
        if len(question.possible_answers) > 1:
            tq += '\n\\begin{enumerate}'
            for answer in question.possible_answers:
                tq += f'\n\\item {answer}'
            tq += '\n\\end{enumerate}'
        else:
            tq += f'\n \\newline{question.possible_answers[0]}\n'
        tq += '\n\\vspace{0.5cm}'

    # Don't transform image paths - use them as-is
    # tq = transform_image_includes(tq)

    subject_path = path(f'subjects/aux_files/subject{i + 1}.tex')
    write_file(subject_path, tq + '\n\\end{enumerate}\n\\end{document}')

    compile_documents(output_dir, subject_path)
    compile_documents(output_dir, subject_path)


def compile_documents(output_dir: str, subject_path: str) -> None:
    if os.name == 'nt':  # Windows
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                'pdflatex',
                '-interaction=nonstopmode',
                f'-output-directory={output_dir}',
                subject_path,
            ],
            capture_output=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore[attr-defined]
        )
    else:  # Unix-based systems
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                'pdflatex',
                '-interaction=nonstopmode',
                f'-output-directory={output_dir}',
                subject_path,
            ],
            capture_output=True,
            check=False,
        )

    if result.returncode != 0:
        raise_compile_error(result)

    if result.stdout:
        logging.debug(result.stdout)
    if result.stderr:
        raise_compile_error(result)


def raise_compile_error(result: subprocess.CompletedProcess[bytes]) -> None:
    logging.error(result.stdout)
    log_file_path = os.path.join(script_dir, 'debug.log')
    with open(log_file_path, 'a', encoding='UTF8') as log_file:
        # Use latin-1 encoding as LaTeX logs often contain Latin-1 encoded characters
        log_file.write(result.stdout.decode('latin-1', errors='replace'))
        log_file.write(result.stderr.decode('latin-1', errors='replace'))
    raise RuntimeError(
        f'LaTeX compilation failed\n Check the log file at {log_file_path} for more information',
    )


def generate_subjects() -> None:
    raw_questions = read_file(path('questions.txt'))

    title = 'QCM'
    author = ''
    school = ''
    course = ''
    date = ''

    for i, line in enumerate(raw_questions):
        if not line.strip():
            break
        if i == 0:
            title = line.strip()
        elif i == 1:
            author = line.strip()
        elif i == 2:
            school = line.strip()
        elif i == 3:
            course = line.strip()
        elif i == 4:
            date = line.strip()

    head_lines = len({title, author, school, course, date})
    if date == '':
        logging.warning('Title, author, school, course, or date information is missing in questions.txt')

    raw_questions = raw_questions[head_lines:]

    formatted_title_header = latex_top.format(title=title, author=author, subject=course, school=school, date=date)

    question_list, possible_choices = parse_questions(raw_questions)

    questions = [Question(question_list[i], possible_choices[i]) for i in range(len(question_list))]
    shuffled_questions = shuffle_questions(questions, num_different_subjects)

    create_latex_files(shuffled_questions, formatted_title_header)

    clean()


if __name__ == '__main__':
    generate_subjects()
