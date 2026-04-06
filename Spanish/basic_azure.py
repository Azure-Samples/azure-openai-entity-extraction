import logging
import os

import rich
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

if not os.getenv("AZURE_OPENAI_SERVICE") or not os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"):
    logging.warning("AZURE_OPENAI_SERVICE and AZURE_OPENAI_GPT_DEPLOYMENT env variables are empty. See README.")
    exit(1)

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


response = client.responses.parse(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"),
    input=[
        {"role": "system", "content": "Extrae la información del evento."},
        {"role": "user", "content": "Alicia y Roberto van a ir a una feria de ciencias el viernes."},
    ],
    text_format=CalendarEvent,
    store=False,
)

if response.output_parsed:
    rich.print(response.output_parsed)
else:
    rich.print(response.output[0].content[0].refusal)
