import os

import rich
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
    # Specify the API version to use the Structured Outputs feature
    default_query={"api-version": "2024-08-01-preview"},
)
model_name = "gpt-4o"


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    response_format=CalendarEvent,
)

message = completion.choices[0].message
if (message.refusal):
    rich.print(message.refusal)
else:
    rich.print(message.parsed)
