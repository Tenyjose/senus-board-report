
import json


def parse_json_response(raw_text: str) -> dict:
    """Clean and parse Claude's reply into a Python dict, or raise clearly."""
    cleaned = raw_text.strip()

    # Remove markdown code fences if present (```json ... ``` or ``` ... ```)
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]              # drop the opening ``` line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]         # drop the closing ``` line
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude did not return valid JSON. Error: {e}\n"
            f"Raw response was:\n{raw_text}"
        )