import json
from anthropic import Anthropic

from app.core.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)

INSIGHTS_SYSTEM_PROMPT = """You are a corporate finance analyst writing board-level \
commentary for Senus PLC, an Irish Natural Capital management software company \
listed on Euronext Access Dublin.

You will be given a JSON object containing this period's financial metrics, plus \
qualitative commercial context (notable events, deal values, pipeline). Write a \
short, board-level narrative - 3 to 5 sentences - that a CEO or board member would \
actually want to read.

Rules:
- ONLY reference figures and events present in the provided data. Never invent, \
estimate, or assume any number or event not explicitly given.
- If a metric is null, do not mention it or make up a reason for its absence.
- Where relevant, connect a financial movement to a qualitative event from the \
commercial context (e.g. explain a cash or working capital change using an \
acquisition or funding event, if one is present in the data).
- Write in plain, direct business English - no generic filler phrases.
- Do not restate every number - pick the 2-3 most board-relevant points.
- Return ONLY the commentary text - no headers, no markdown, no JSON."""


def generate_period_insights(metrics: dict, commercial_context: dict) -> str:
    payload = {
        "metrics": metrics,
        "commercial_context": commercial_context,
    }

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=500,
        system=INSIGHTS_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": json.dumps(payload, default=str),
            }
        ],
    )

    return message.content[0].text.strip()