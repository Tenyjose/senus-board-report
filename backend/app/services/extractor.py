import base64
import json

from anthropic import Anthropic

from app.services.json_utils import parse_json_response
from app.core.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)


def _bytes_to_base64(pdf_bytes: bytes) -> str:
    # Convert raw PDF bytes to a base64 text string for sending.
    return base64.standard_b64encode(pdf_bytes).decode("utf-8")


def extract_financials(pdf_bytes: bytes, extraction_prompt: str) -> dict:
    # Send PDF bytes to Claude with a specific instruction, and return the
    # structured data Claude extracts, parsed from JSON into a Python dict.
    pdf_base64 = _bytes_to_base64(pdf_bytes)

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {"type": "text", "text": extraction_prompt},
                ],
            }
        ],
    )

    raw_text = message.content[0].text
    return parse_json_response(raw_text)