from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
NUMBERED_FILE = re.compile(r"^(\d{2})-[^/]+\.md$")
HEADING = re.compile(r"^ {0,3}#(?:[ \t]+|$)")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]*)\)")
CARD_LINK = re.compile(r'\{\{<[ \t]+card[ \t]+[^\n]*link="([^"]+)"[^\n]*title="([^"]+)"')
YAML_KEY = re.compile(r"^([A-Za-z0-9_.-]+):(?:[ \t]*(.*))?$")


def split_scalar(value: str, separator: str) -> list[str]:
    parts: list[str] = []
    start = 0
    quote = ""
    depth = 0
    index = 0
    while index < len(value):
        character = value[index]
        if quote:
            if character == quote:
                if quote == "'" and index + 1 < len(value) and value[index + 1] == "'":
                    index += 2
                    continue
                quote = ""
            elif quote == '"' and character == "\\":
                index += 1
        elif character in "'\"":
            quote = character
        elif character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == separator and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
        index += 1
    if quote or depth:
        raise ValueError("unterminated flow value")
    parts.append(value[start:].strip())
    return parts


def parse_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid quoted scalar: {error.msg}") from error
        if not isinstance(parsed, (str, int, float, bool)) and parsed is not None:
            raise ValueError("unsupported quoted scalar")
        return str(parsed)
    if value.startswith("["):
        if not value.endswith("]"):
            raise ValueError("unterminated flow sequence")
        for item in split_scalar(value[1:-1], ","):
            if item:
                parse_scalar(item)
        return value
    if value.startswith("{"):
        if not value.endswith("}"):
            raise ValueError("unterminated flow mapping")
        for item in split_scalar(value[1:-1], ","):
            if not item:
                continue
            match = YAML_KEY.match(item)
            if not match or not match.group(2):
                raise ValueError("invalid flow mapping entry")
            parse_scalar(match.group(2))
        return value
    if "\t" in value or any(ord(character) < 32 for character in value):
        raise ValueError("invalid control character in scalar")
    if re.search(r":[ \t]", value) or re.search(r"[ \t]#", value):
        raise ValueError("ambiguous plain scalar")
    return value


def yaml_key(value: str) -> str:
    match = YAML_KEY.match(value)
    if not match:
        raise ValueError("expected a mapping key")
    return match.group(1)


def validate_yaml_block(lines: list[str], start: int, indent: int) -> tuple[dict[str, str], int]:
    values: dict[str, str] = {}
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError("unexpected indentation")
        stripped = line.strip()
        if stripped.startswith("-"):
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip() or next_line.lstrip().startswith("#"):
                    index += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent < indent:
                    break
                if next_indent != indent or not next_line.strip().startswith("-"):
                    raise ValueError("invalid list structure")
                parse_scalar(next_line.strip()[1:].strip())
                index += 1
            continue
        key = yaml_key(stripped)
        if key in values:
            raise ValueError(f"duplicate key {key!r}")
        match = YAML_KEY.match(stripped)
        assert match is not None
        raw_value = match.group(2) or ""
        if not raw_value:
            next_index = index + 1
            while next_index < len(lines) and not lines[next_index].strip():
                next_index += 1
            if next_index < len(lines):
                next_indent = len(lines[next_index]) - len(lines[next_index].lstrip(" "))
                if next_indent > indent:
                    nested, index = validate_yaml_block(lines, next_index, next_indent)
                    values[key] = json.dumps(nested, sort_keys=True)
                    continue
            values[key] = ""
        else:
            values[key] = parse_scalar(raw_value)
        index += 1
    return values, index


def front_matter(path: Path, text: str) -> tuple[dict[str, str], int, list[str]]:
    lines = text.splitlines()
    problems: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, 0, ["missing YAML front matter delimiter"]
    end = next((index for index in range(1, len(lines)) if lines[index].strip() in {"---", "..."}), None)
    if end is None:
        return {}, 0, ["unterminated YAML front matter"]
    block = lines[1:end]
    try:
        values, _ = validate_yaml_block(block, 0, 0)
    except ValueError as error:
        problems.append(f"invalid YAML front matter: {error}")
        return {}, end + 1, problems
    return values, end + 1, problems


def markdown_body(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence_character = ""
    fence_length = 0
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if not fence_character:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = ""
                fence_length = 0
            continue
        if not fence_character:
            result.append((number, line))
    return result


def destination_value(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1:value.index(">")]
    return value.split()[0] if value else ""


def resolve_destination(source: Path, destination: str) -> Path | None:
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    raw_path = unquote(parsed.path)
    if raw_path.startswith("/"):
        candidate = CONTENT / raw_path.lstrip("/")
    else:
        candidate = source.parent / raw_path
    candidate = Path(os.path.normpath(str(candidate)))
    try:
        candidate.relative_to(CONTENT)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    if candidate.is_dir():
        index = candidate / "_index.md"
        if index.is_file():
            return index
    if not candidate.suffix:
        markdown_candidate = candidate.with_name(candidate.name + ".md")
        if markdown_candidate.is_file():
            return markdown_candidate
    return None


def markdown_links(lines: list[str]) -> list[tuple[int, str, str]]:
    links: list[tuple[int, str, str]] = []
    for number, line in markdown_body(lines):
        for match in MARKDOWN_LINK.finditer(line):
            links.append((number, destination_value(match.group(1)), match.group(0)))
    return links


def navigation_entries(index_path: Path) -> list[tuple[int, str, str]]:
    lines = index_path.read_text(encoding="utf-8-sig").splitlines()
    entries: list[tuple[int, str, str]] = []
    for number, line in markdown_body(lines):
        for match in MARKDOWN_LINK.finditer(line):
            text = re.match(r"\[([^\]]*)\]", match.group(0))
            entries.append((number, destination_value(match.group(1)), text.group(1) if text else ""))
        for match in CARD_LINK.finditer(line):
            entries.append((number, destination_value(match.group(1)), match.group(2)))
    return entries


def validate() -> list[str]:
    files = sorted(CONTENT.rglob("*.md"))
    metadata: dict[Path, tuple[dict[str, str], int, list[str], str]] = {}
    problems: list[str] = []
    if not files:
        return ["no content Markdown files found"]
    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        values, body_start, issues = front_matter(path, text)
        metadata[path] = (values, body_start, issues, text)
        problems.extend(f"{path.relative_to(ROOT)}:{index + 1}: {issue}" for index, issue in enumerate(issues))
    for path, (values, _, issues, _) in metadata.items():
        title = values.get("title", "")
        raw_weight = values.get("weight")
        if raw_weight is None or not re.fullmatch(r"[+-]?\d+", raw_weight):
            if path.name != "_index.md" and NUMBERED_FILE.match(path.name):
                problems.append(f"{path.relative_to(ROOT)}:{1}: chapter weight must be an integer matching its filename prefix")
        match = NUMBERED_FILE.match(path.name)
        if match and raw_weight is not None and re.fullmatch(r"[+-]?\d+", raw_weight):
            expected = int(match.group(1))
            actual = int(raw_weight)
            if actual != expected:
                problems.append(f"{path.relative_to(ROOT)}:1: weight {actual} does not match filename prefix {expected:02d}")
        if raw_weight is not None and raw_weight and not re.fullmatch(r"[+-]?\d+", raw_weight):
            problems.append(f"{path.relative_to(ROOT)}:1: weight must be an integer")
    sibling_weights: dict[Path, list[Path]] = {}
    for path, (values, _, _, _) in metadata.items():
        raw_weight = values.get("weight")
        if path.name == "_index.md" or raw_weight is None or not re.fullmatch(r"[+-]?\d+", raw_weight):
            continue
        sibling_weights.setdefault(path.parent, []).append(path)
    for parent, paths in sibling_weights.items():
        grouped: dict[int, list[Path]] = {}
        for path in paths:
            grouped.setdefault(int(metadata[path][0]["weight"]), []).append(path)
        for weight, matches in grouped.items():
            if len(matches) > 1:
                for path in matches:
                    problems.append(f"{path.relative_to(ROOT)}:1: duplicate sibling weight {weight} with {', '.join(str(item.relative_to(ROOT)) for item in matches)}")
    for path, (values, body_start, issues, text) in metadata.items():
        if not values.get("title") and not issues:
            problems.append(f"{path.relative_to(ROOT)}:1: missing title")
        for number, line in markdown_body(text.splitlines()[body_start:]):
            if HEADING.match(line):
                problems.append(f"{path.relative_to(ROOT)}:{body_start + number}: stray H1 heading")
        for number, destination, original in markdown_links(text.splitlines()):
            if not destination or urlsplit(destination).scheme or urlsplit(destination).netloc or not urlsplit(destination).path:
                continue
            if resolve_destination(path, destination) is None:
                problems.append(f"{path.relative_to(ROOT)}:{number}: unresolved internal link {destination} in {original}")
    nav_exempt = {CONTENT / "_index.md", CONTENT / "docs" / "_index.md"}
    for path, (values, _, issues, _) in metadata.items():
        if path in nav_exempt or issues:
            continue
        title = values.get("title", "")
        indexes: list[Path] = []
        parent = path.parent
        while parent >= CONTENT:
            index = parent / "_index.md"
            if index.is_file():
                indexes.append(index)
            if parent == CONTENT:
                break
            parent = parent.parent
        listed = False
        for index in indexes:
            for _, destination, link_title in navigation_entries(index):
                if link_title != title:
                    continue
                target = resolve_destination(index, destination)
                if target is not None and target == path:
                    listed = True
                    break
            if listed:
                break
        if not listed:
            problems.append(f"{path.relative_to(ROOT)}:1: page is not listed in a parent navigation index")
    return problems


def main() -> int:
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        print(f"{len(problems)} problem(s) found")
        return 1
    print(f"{len(list(CONTENT.rglob('*.md')))} content Markdown files checked, 0 problems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
