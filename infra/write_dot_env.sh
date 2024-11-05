#!/bin/bash

# Clear the contents of the .env file
> .env

# Append new values to the .env file
echo "AZURE_OPENAI_GPT_DEPLOYMENT=$(azd env get-value AZURE_OPENAI_GPT_DEPLOYMENT)" >> .env
echo "AZURE_OPENAI_SERVICE=$(azd env get-value AZURE_OPENAI_SERVICE)" >> .env
