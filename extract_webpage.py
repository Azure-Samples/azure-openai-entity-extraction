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
        logging.warning("AZURE_OPENAI_SERVICE and AZURE_OPENAI_GPT_DEPLOYMENT env variables are empty. See README.")
        exit(1)
    credential = azure.identity.AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID"))
    token_provider = azure.identity.get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    client = openai.AzureOpenAI(
        api_version="2024-08-01-preview",
        azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com",
        azure_ad_token_provider=token_provider,
    )
    model_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")
else:
    if not os.getenv("GITHUB_TOKEN"):
        logging.warning("GITHUB_TOKEN env variable is empty. See README.")
        exit(1)
    client = openai.OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
        # Specify the API version to use the Structured Outputs feature
        default_query={"api-version": "2024-08-01-preview"},
    )
    model_name = "gpt-4o"


# Define models for Structured Outputs
class BlogPost(BaseModel):
    title: str
    summary: str = Field(..., description="A 1-2 sentence summary of the blog post")
    tags: list[str] = Field(..., description="A list of tags for the blog post, like 'python' or 'openai'")


# Fetch blog post and extract title/content
url = "https://blog.pamelafox.org/2024/09/integrating-vision-into-rag-applications.html"
response = requests.get(url)
if response.status_code != 200:
    print(f"Failed to fetch the page: {response.status_code}")
    exit(1)
soup = BeautifulSoup(response.content, "html.parser")
post_title = soup.find("h3", class_="post-title")
post_contents = soup.find("div", class_="post-body").get_text(strip=True)


# Send request to GPT model to extract using Structured Outputs
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extract the information from the blog post"},
        {"role": "user", "content": f"{post_title}\n{post_contents}"},
    ],
    response_format=BlogPost,
)

message = completion.choices[0].message
if message.refusal:
    print(message.refusal)
else:
    print(message.parsed)
