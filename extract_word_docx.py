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
class DocumentMetadata(BaseModel):
    title: str
    author: str | None
    headings: list[str]


# Use markitdown to convert docx to markdown
md = MarkItDown(enable_plugins=False)
markdown_text = md.convert("example_doc.docx").text_content

# Send request to LLM to extract using Structured Outputs
response = client.responses.parse(
    model=model_name,
    input=[
        {"role": "system", "content": "Extract the document title, author, and a list of all headings."},
        {"role": "user", "content": markdown_text},
    ],
    text_format=DocumentMetadata,
    store=False,
)

if response.output_parsed:
    print(response.output_parsed)
else:
    print(response.output[0].content[0].refusal)
