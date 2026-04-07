import logging
import os

import openai
import requests
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from bs4 import BeautifulSoup
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
class BlogPost(BaseModel):
    title: str
    summary: str = Field(..., description="Un resumen de 1-2 oraciones de la publicación del blog")
    tags: list[str] = Field(
        ..., description="Una lista de etiquetas para la publicación del blog, como 'python' o 'openai'"
    )


# Obtener la publicación del blog y extraer título/contenido
url = "https://blog.pamelafox.org/2024/09/integrating-vision-into-rag-applications.html"
response = requests.get(url)
if response.status_code != 200:
    print(f"Error al obtener la página: {response.status_code}")
    exit(1)
soup = BeautifulSoup(response.content, "html.parser")
post_title = soup.find("h3", class_="post-title")
post_contents = soup.find("div", class_="post-body").get_text(strip=True)


# Enviar solicitud al modelo GPT para extraer usando Salidas Estructuradas
response = client.responses.parse(
    model=model_name,
    input=[
        {"role": "system", "content": "Extrae la información de la publicación del blog"},
        {"role": "user", "content": f"{post_title}\n{post_contents}"},
    ],
    text_format=BlogPost,
    store=False,
)

if response.output_parsed:
    print(response.output_parsed)
else:
    print(response.output[0].content[0].refusal)
