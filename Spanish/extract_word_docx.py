import logging
import os

import openai
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from markitdown import MarkItDown
from pydantic import BaseModel
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
class DocumentMetadata(BaseModel):
    title: str
    author: str | None
    headings: list[str]


# Usar markitdown para convertir docx a markdown
md = MarkItDown(enable_plugins=False)
markdown_text = md.convert("../example_doc.docx").text_content

# Enviar solicitud al LLM para extraer usando Salidas Estructuradas
response = client.responses.parse(
    model=model_name,
    input=[
        {"role": "system", "content": "Extrae el título del documento, el autor y una lista de todos los encabezados."},
        {"role": "user", "content": markdown_text},
    ],
    text_format=DocumentMetadata,
    store=False,
)

if response.output_parsed:
    print(response.output_parsed)
else:
    print(response.output[0].content[0].refusal)
