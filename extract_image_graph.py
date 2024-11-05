import base64
import logging
import os

import azure.identity
import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich import print

logging.basicConfig(level=logging.WARNING)
load_dotenv()

# Configure Azure OpenAI
if not os.getenv("AZURE_OPENAI_SERVICE") or not os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"):
    logging.warning("AZURE_OPENAI_SERVICE and AZURE_OPENAI_GPT_DEPLOYMENT environment variables are empty. See README.")
    exit(1)
credential = azure.identity.AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID"))
token_provider = azure.identity.get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
client = openai.AzureOpenAI(
    api_version="2024-08-01-preview",
    azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com",
    azure_ad_token_provider=token_provider,
)
model_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")


# Define models for Structured Outputs
class Graph(BaseModel):
    title: str
    description: str = Field(..., description="1 sentence description of the graph")
    x_axis: str
    y_axis: str
    legend: list[str]


# Prepare local image as base64 URI
def open_image_as_base64(filename):
    with open(filename, "rb") as image_file:
        image_data = image_file.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


image_url = open_image_as_base64("example_graph_treecover.png")

# Send request to GPT model to extract using Structured Outputs
completion = client.beta.chat.completions.parse(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extract the information from the graph"},
        {
            "role": "user",
            "content": [
                {"image_url": {"url": image_url}, "type": "image_url"},
            ],
        },
    ],
    response_format=Graph,
)

output = completion.choices[0].message.parsed
graph = Graph.model_validate(output)
print(graph)
