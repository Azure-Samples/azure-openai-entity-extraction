import base64
import logging
import os
from enum import Enum

import azure.identity
import openai
import requests
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
class Language(str, Enum):
    JAVASCRIPT = "JavaScript"
    PYTHON = "Python"
    DOTNET = ".NET"


class AzureService(str, Enum):
    AISTUDIO = "AI Studio"
    AISEARCH = "AI Search"
    POSTGRESQL = "PostgreSQL"
    COSMOSDB = "CosmosDB"
    AZURESQL = "Azure SQL"


class Framework(str, Enum):
    LANGCHAIN = "Langchain"
    SEMANTICKERNEL = "Semantic Kernel"
    LLAMAINDEX = "Llamaindex"
    AUTOGEN = "Autogen"
    SPRINGBOOT = "Spring Boot"
    PROMPTY = "Prompty"


class RepoOverview(BaseModel):
    name: str
    description: str = Field(..., description="Una descripción de 1-2 oraciones del proyecto")
    languages: list[Language]
    azure_services: list[AzureService]
    frameworks: list[Framework]


# Obtener un README de un repositorio público de GitHub
url = "https://api.github.com/repos/shank250/CareerCanvas-msft-raghack/contents/README.md"
response = requests.get(url)
if response.status_code != 200:
    logging.error(f"Error al obtener el issue: {response.status_code}")
    exit(1)
content = response.json()
readme_content = base64.b64decode(content["content"]).decode("utf-8")

# Enviar solicitud al modelo GPT para extraer usando Salidas Estructuradas
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {
            "role": "system",
            "content": "Extrae la información del markdown del issue de GitHub sobre esta presentación del hackathon.",
        },
        {"role": "user", "content": readme_content},
    ],
    response_format=RepoOverview,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
