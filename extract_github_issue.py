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
load_dotenv()


if os.getenv("OPENAI_HOST", "azure") == "azure":
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
class Technology(str, Enum):
    JAVASCRIPT = "JavaScript"
    PYTHON = "Python"
    DOTNET = ".NET"
    AISTUDIO = "AI Studio"
    AISEARCH = "AI Search"
    POSTGRESQL = "PostgreSQL"
    COSMOSDB = "CosmosDB"
    AZURESQL = "Azure SQL"


class HackSubmission(BaseModel):
    name: str
    description: str = Field(..., description="A 1-2 sentence description of the project")
    technologies: list[Technology]
    repository_url: str
    video_url: str
    team_members: list[str]


# Fetch an issue from a public GitHub repository
url = "https://api.github.com/repos/microsoft/RAG_Hack/issues/159"
response = requests.get(url)
if response.status_code != 200:
    logging.error(f"Failed to fetch issue: {response.status_code}")
    exit(1)
issue_body = response.json()["body"]

# Send request to GPT model to extract using Structured Outputs
completion = client.beta.chat.completions.parse(
    model=model_name,
    messages=[
        {"role": "system", "content": "Extract the info from the GitHub issue markdown about this hack submission."},
        {"role": "user", "content": issue_body},
    ],
    response_format=HackSubmission,
)

output = completion.choices[0].message.parsed
hack_submission = HackSubmission.model_validate(output)
print(hack_submission)
