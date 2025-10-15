import base64
import logging
import os

import azure.identity
import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich import print

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

if os.getenv("OPENAI_HOST", "github") == "azure":
    if not os.getenv("AZURE_OPENAI_SERVICE") or not os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"):
        logging.warning("Las variables de entorno AZURE_OPENAI_SERVICE y AZURE_OPENAI_GPT_DEPLOYMENT están vacías. Revisa el README.")
        exit(1)
    credential = azure.identity.AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID"))
    token_provider = azure.identity.get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    client = openai.OpenAI(
        base_url=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com/openai/v1",
        api_key=token_provider,
    )
    model_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")
else:
    if not os.getenv("GITHUB_TOKEN"):
        logging.warning("La variable de entorno GITHUB_TOKEN está vacía. Revisa el README.")
        exit(1)
    client = openai.OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=os.environ["GITHUB_TOKEN"],
        # Especifica la versión de la API para usar la función de Salidas Estructuradas
        default_query={"api-version": "2024-08-01-preview"},
    )
    model_name = "openai/gpt-4o"


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
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extrae la información del gráfico"},
        {
            "role": "user",
            "content": [
                {"image_url": {"url": image_url}, "type": "image_url"},
            ],
        },
    ],
    response_format=Graph,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
