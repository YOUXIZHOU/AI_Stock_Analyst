import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def call_claude(messages, max_tokens=500, system=None):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        temperature=0,
        system=system or "",
        messages=messages
    )
    for block in response.content:
        if block.type == "text":
            return block.text