import logging
import os

import rich
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID")), "https://cognitiveservices.azure.com/.default"
)

client = OpenAI(
    base_url=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com/openai/v1",
    api_key=token_provider,
)


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


completion = client.beta.chat.completions.parse(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extrae la información del evento."},
        {"role": "user", "content": "Alicia y Roberto van a ir a una feria de ciencias el viernes."},
    ],
    response_format=CalendarEvent,
)

message = completion.choices[0].message
if message.refusal:
    rich.print(message.refusal)
else:
    rich.print(message.parsed)
