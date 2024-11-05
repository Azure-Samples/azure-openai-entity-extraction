import logging
import os

import azure.identity
import openai
import pymupdf4llm
from dotenv import load_dotenv
from pydantic import BaseModel
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
class Item(BaseModel):
    product: str
    price: float
    quantity: int


class Receipt(BaseModel):
    total: float
    shipping: float
    payment_method: str
    items: list[Item]
    order_number: int


# Prepare PDF as markdown text
md_text = pymupdf4llm.to_markdown("example_receipt.pdf")

# Send request to GPT model to extract using Structured Outputs
completion = client.beta.chat.completions.parse(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extract the information from the blog post"},
        {"role": "user", "content": md_text},
    ],
    response_format=Receipt,
)

output = completion.choices[0].message.parsed
receipt = Receipt.model_validate(output)
print(receipt)
