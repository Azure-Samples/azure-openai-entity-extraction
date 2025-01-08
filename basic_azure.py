import logging
import os

import requests
import rich
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider

# Use BeautifulSoup to extract the article text
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.WARNING)
load_dotenv()

token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID")), "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_SERVICE')}.openai.azure.com",
    azure_ad_token_provider=token_provider,
    api_version="2024-10-21",
)

# Fetch a NPR article using requests


response = requests.get("https://www.npr.org/2024/12/01/nx-s1-5211874/lake-effect-snow-northeast-and-midwest")
article = response.text


soup = BeautifulSoup(article, "html.parser")
article_text = soup.find("div", class_="storytext").get_text()


class Person(BaseModel):
    first_name: str
    last_name: str


class Location(BaseModel):
    name: str
    type: str


class ArticleEntities(BaseModel):
    persons: list[Person]
    locations: list[Location]


completion = client.beta.chat.completions.parse(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extract information from the given article."},
        {"role": "user", "content": article_text},
    ],
    response_format=ArticleEntities,
)

output = completion.choices[0].message.parsed
rich.print(output)
