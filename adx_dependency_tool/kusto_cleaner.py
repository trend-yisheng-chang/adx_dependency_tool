import re


def clean(query):
    # Remove new lines in front and end.
    query = query.strip('\n')
    # Remove spaces in front and end.
    query = query.strip()
    # Remove unnecessary indents.
    query = re.sub(r'\n\s+', '\n', query)
    # Remove comments.
    query = remove_comments(query)
    # Remove multiple contiguous new line symbol.
    query = re.sub(r'\n+', '\n', query)

    return query


def remove_comments(query):
    url_pattern = r'(http:\/\/|https:\/\/)[\w\-]+(\.[\w\-]+)+([\/\w\-.]*)*'
    comment_pattern = r'\/\/.*'
    lines = query.splitlines()
    cleaned_lines = []

    for line in lines:
        if re.search(url_pattern, line):
            cleaned_lines.append(line)
        else:
            cleaned_line = re.sub(comment_pattern, '', line).rstrip()
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)
