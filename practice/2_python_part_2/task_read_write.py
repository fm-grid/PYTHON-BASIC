"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "23")
    file_2.txt (content: "78")
    file_3.txt (content: "3")

    Output:

    result.txt(content: "23, 78, 3")
"""
import os


def extract_key(filename: str) -> int: # 'file_42.txt' -> 42
    suffix = filename.split('_')[-1]
    number = suffix.split('.')[0]
    return int(number)


def main(path: str) -> None:
    filenames = os.listdir(path)
    filenames = sorted(filenames, key=extract_key)
    contents = []
    for filename in filenames:
        with open(path + '/' + filename) as file:
            contents.append(file.read())
    with open(path + '/result.txt', 'x') as file:
        file.write(', '.join(contents))


if __name__ == '__main__':
    main('./practice/2_python_part_2/files')
