import io
import os

from parameters_and_helpers import WORDS_TO_FIND, save_dict_as_json


def find_words_in_files(root_dir: str, words: list) -> dict:
    main_dict = {}
    for subdir, _, files in os.walk(root_dir):
        for file in files:

            matched_lines = find_words_in_single_file(
                file_path=os.path.join(subdir, file),
                words=words
            )
            if matched_lines:
                key = os.path.join(subdir, file).split('/')[2]
                main_dict[key] = matched_lines
    return main_dict


def find_words_in_single_file(file_path: str, words: list) -> list:
    try:
        with open(file_path, "r") as file_reader:
            file_contents = file_reader.readlines()
    except io.UnsupportedOperation:
        return []

    lines_with_a_match = []
    for line in file_contents:
        if any([x in line.lower() for x in words]):
            lines_with_a_match.append(line)
    return lines_with_a_match


if __name__ == "__main__":
    findings = find_words_in_files(
        "./logs_extracted/",
        words=WORDS_TO_FIND
    )
    save_dict_as_json(findings, "matched_lines.json")
