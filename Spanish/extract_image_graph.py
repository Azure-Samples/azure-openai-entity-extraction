import base64
import logging
import os

import openai
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich import print

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

if not os.getenv("AZURE_OPENAI_SERVICE") or not os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"):
    logging.warning(
        "Las variables de entorno AZURE_OPENAI_SERVICE y AZURE_OPENAI_GPT_DEPLOYMENT están vacías. Revisa el README."
    )
    exit(1)

token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID")), "https://cognitiveservices.azure.com/.default"
)

client = openai.OpenAI(
    base_url=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com/openai/v1",
    api_key=token_provider,
)
model_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")


# Define modelos para Salidas Estructuradas
class Graph(BaseModel):
    title: str
    description: str = Field(..., description="Descripción de 1 oración del gráfico")
    x_axis: str
    y_axis: str
    legend: list[str]


# Preparar imagen local como URI base64
def open_image_as_base64(filename):
    with open(filename, "rb") as image_file:
        image_data = image_file.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


image_url = open_image_as_base64("../example_graph_treecover.png")

# Enviar solicitud al modelo GPT para extraer usando Salidas Estructuradas
response = client.responses.parse(
    model=model_name,
    input=[
        {"role": "system", "content": "Extrae la información del gráfico"},
        {
            "role": "user",
            "content": [
                {"image_url": image_url, "type": "input_image"},
            ],
        },
    ],
    text_format=Graph,
    store=False,
)

if response.output_parsed:
    print(response.output_parsed)
else:
    print(response.output[0].content[0].refusal)
