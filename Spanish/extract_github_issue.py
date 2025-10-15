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
class IssueType(str, Enum):
    BUGREPORT = "Bug Report"
    FEATURE = "Feature"
    DOCUMENTATION = "Documentation"
    REGRESSION = "Regression"


class Issue(BaseModel):
    title: str
    description: str = Field(..., description="Una descripción de 1-2 oraciones del proyecto")
    type: IssueType
    operating_system: str


# Obtener un issue de un repositorio público de GitHub
url = "https://api.github.com/repos/Azure-Samples/azure-search-openai-demo/issues/2231"
response = requests.get(url)
if response.status_code != 200:
    logging.error(f"Error al obtener el issue: {response.status_code}")
    exit(1)
issue_body = response.json()["body"]

# Enviar solicitud al modelo GPT para extraer usando Salidas Estructuradas
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extrae la información del markdown del issue de GitHub."},
        {"role": "user", "content": issue_body},
    ],
    response_format=Issue,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
