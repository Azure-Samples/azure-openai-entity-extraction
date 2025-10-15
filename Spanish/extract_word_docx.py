import logging
import os

import openai
from dotenv import load_dotenv
from markitdown import MarkItDown
from pydantic import BaseModel
from rich import print

logging.basicConfig(level=logging.WARNING)
load_dotenv(override=True)

if os.getenv("OPENAI_HOST", "github") == "azure":
    import azure.identity

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
        default_query={"api-version": "2024-08-01-preview"},
    )
    model_name = "openai/gpt-4o"


# Define modelos para Salidas Estructuradas
class DocumentMetadata(BaseModel):
    title: str
    author: str | None
    headings: list[str]


# Usar markitdown para convertir docx a markdown
md = MarkItDown(enable_plugins=False)
markdown_text = md.convert("../example_doc.docx").text_content

# Enviar solicitud al LLM para extraer usando Salidas Estructuradas
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extrae el título del documento, el autor y una lista de todos los encabezados."},
        {"role": "user", "content": markdown_text},
    ],
    response_format=DocumentMetadata,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
