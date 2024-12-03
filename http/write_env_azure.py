import os
from pathlib import Path

import azure.identity
from dotenv_azd import load_azd_env

load_azd_env()

# Get a token from Azure
token_provider = azure.identity.get_bearer_token_provider(
    azure.identity.AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID")),
    "https://cognitiveservices.azure.com/.default",
)
token = token_provider()

# Path to the .env file in the current directory
env_path = Path(__file__).parent / ".env"

# Write the new .env, replacing the existing Azure OpenAI lines
with open(env_path) as f:
    existing_lines = f.readlines()

existing_lines = [line for line in existing_lines if not line.startswith("AZURE_OPENAI")]

with open(env_path, "w") as f:
    f.write("")
    for line in existing_lines:
        f.write(line)
    f.write(f"AZURE_OPENAI_SERVICE={os.getenv('AZURE_OPENAI_SERVICE')}\n")
    f.write(f"AZURE_OPENAI_GPT_DEPLOYMENT={os.getenv('AZURE_OPENAI_GPT_DEPLOYMENT')}\n")
    f.write(f"AZURE_OPENAI_TOKEN={token}\n")
