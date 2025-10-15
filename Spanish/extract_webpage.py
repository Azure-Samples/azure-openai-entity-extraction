import logging
import os

import azure.identity
import openai
import requests
from bs4 import BeautifulSoup
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
class BlogPost(BaseModel):
    title: str
    summary: str = Field(..., description="Un resumen de 1-2 oraciones de la publicación del blog")
    tags: list[str] = Field(..., description="Una lista de etiquetas para la publicación del blog, como 'python' o 'openai'")


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
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extrae la información de la publicación del blog"},
        {"role": "user", "content": f"{post_title}\n{post_contents}"},
    ],
    response_format=BlogPost,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
