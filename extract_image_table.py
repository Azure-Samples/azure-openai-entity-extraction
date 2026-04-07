import base64
import logging
import os

import openai
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic import BaseModel
from rich import print

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

if not os.getenv("AZURE_OPENAI_SERVICE") or not os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"):
    logging.warning("AZURE_OPENAI_SERVICE and AZURE_OPENAI_GPT_DEPLOYMENT env variables are empty. See README.")
    exit(1)

token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID")), "https://cognitiveservices.azure.com/.default"
)

client = openai.OpenAI(
    base_url=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com/openai/v1",
    api_key=token_provider,
)
model_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")


# Define models for Structured Outputs
class Plant(BaseModel):
    species: str
    common_name: str
    quantity: int
    size: str
    price: float
    county: str
    notes: str


class PlantInventory(BaseModel):
    annuals: list[Plant]
    bulbs: list[Plant]
    grasses: list[Plant]


# Prepare local image as base64 URI
def open_image_as_base64(filename):
    with open(filename, "rb") as image_file:
        image_data = image_file.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


image_url = open_image_as_base64("example_table_plants.png")

# Send request to GPT model to extract using Structured Outputs
response = client.responses.parse(
    model=model_name,
    input=[
        {"role": "system", "content": "Extract the information from the table"},
        {
            "role": "user",
            "content": [
                {"image_url": image_url, "type": "input_image"},
            ],
        },
    ],
    text_format=PlantInventory,
    store=False,
)

if response.output_parsed:
    print(response.output_parsed)
else:
    print(response.output[0].content[0].refusal)
