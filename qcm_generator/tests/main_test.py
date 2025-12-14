import os

import pytest
from pytest_mock import MockerFixture

from qcm_generator import Question, clean, parse_questions, path, read_file, shuffle_questions, write_file


def test_path() -> None:
    assert path('test.txt') == os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.txt')


def test_read_file(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='test'))
    result = read_file('dummy_path')
    mock_open.assert_called_once_with('dummy_path', 'r', encoding='UTF8')
    assert result == ['test']


def test_write_file(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('builtins.open', mocker.mock_open())
    write_file('dummy_path', 'test content')
    mock_open.assert_called_once_with('dummy_path', 'w', encoding='UTF8')
    mock_open().write.assert_called_once_with('test content')


@pytest.mark.parametrize(
    ('input_data', 'expected_questions', 'expected_choices'),
    [
        (
            ['Q1. Question 1\n', 'Answer 1\n', 'Answer 2\n', 'Q2. Question 2\n', 'Answer 3\n'],
            ['Question 1', 'Question 2'],
            [['Answer 1', 'Answer 2'], ['Answer 3']],
        ),
        (['Q1. Test question\n', 'Choice A\n', 'B. Choice B\n'], ['Test question'], [['Choice A', 'B. Choice B']]),
    ],
)
def test_parse_questions(
    input_data: list[str],
    expected_questions: list[str],
    expected_choices: list[list[str]],
) -> None:
    questions, choices = parse_questions(input_data)
    assert questions == expected_questions
    assert choices == expected_choices


def test_generate_qcm() -> None:

    questions = [Question('What is A?', ['A1', 'A2']), Question('What is B?', ['B1', 'B2'])]
    result = shuffle_questions(questions, 2)
    assert len(result) == 2  # Two subjects
    assert len(result[0]) == len(questions)  # Same number of questions


def test_clean(mocker: MockerFixture) -> None:
    mock_rmdir = mocker.patch('os.rmdir')
    mock_remove = mocker.patch('os.remove')
    mock_walk = mocker.patch('os.walk', return_value=[('dir', ('subdir',), ('file.tex',))])

    clean()

    mock_remove.assert_called()
    mock_rmdir.assert_not_called()
    mock_walk.assert_called()
