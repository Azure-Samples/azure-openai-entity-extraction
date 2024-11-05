# Clear the contents of the .env file
Set-Content -Path .env -Value ""

# Append new values to the .env file
$azureOpenAiDeployment = azd env get-value AZURE_OPENAI_GPT_DEPLOYMENT
$azureOpenAiService = azd env get-value AZURE_OPENAI_SERVICE

Add-Content -Path .env -Value "AZURE_OPENAI_GPT_DEPLOYMENT=$azureOpenAiDeployment"
Add-Content -Path .env -Value "AZURE_OPENAI_SERVICE=$azureOpenAiService"
