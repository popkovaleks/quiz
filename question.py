import random
import re
import os


def parse_questions(questions_dir, questions_file):
    questions = []
    with open(f'{questions_dir}/{questions_file}', 'r', encoding='KOI8-R') as file:
        file_content = file.read()
        for section in file_content.split("\n\n\n"):
            for section_part in section.split("\n\n"):
                sect_parts = section_part.split("\n")
                if re.match(r'Вопрос \d+:', sect_parts[0]):
                    sect_parts.pop(0)
                    question = {'Вопрос': ''.join(sect_parts)}
                if re.match(r'Ответ:', sect_parts[0]):
                    sect_parts.pop(0)
                    question.update({'Ответ': ''.join(sect_parts)})
                    questions.append(question)
    return questions
