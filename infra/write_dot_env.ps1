# Clear the contents of the .env file
Set-Content -Path .env -Value ""

# Append new values to the .env file
$azureOpenAiDeployment = azd env get-value AZURE_OPENAI_GPT_DEPLOYMENT
$azureOpenAiService = azd env get-value AZURE_OPENAI_SERVICE
$azureTenantId = azd env get-value AZURE_TENANT_ID

Add-Content -Path .env -Value "AZURE_OPENAI_GPT_DEPLOYMENT=$azureOpenAiDeployment"
Add-Content -Path .env -Value "AZURE_OPENAI_SERVICE=$azureOpenAiService"
Add-Content -Path .env -Value "AZURE_TENANT_ID=$azureTenantId"
