import re


def parse_description(text: str) -> dict:
    pattern = r"([А-ЯҐІЄЇ][а-яґіїєА-ЯҐІЄЇ\s]+)([^А-ЯҐІЄЇ]+)"
    matches = re.findall(pattern, text)

    return {k.strip(): v.strip() for k, v in matches}
