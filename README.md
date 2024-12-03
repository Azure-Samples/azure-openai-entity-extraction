<!--
---
name: Entity extraction with Azure OpenAI structured outputs
description: Use Azure OpenAI structured outputs and the openai Python SDK to extract details from images, GitHub issues, PDFs, and more.
languages:
- python
- bicep
- azdeveloper
products:
- azure-openai
- azure
page_type: sample
urlFragment: azure-openai-entity-extraction
---
-->
# Entity extraction with Azure OpenAI structured outputs (Python)

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&skip_quickstart=true&machine=basicLinux32gb&repo=784926917&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=WestUs2)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/azure-openai-entity-extraction)

This repository includes both the infrastructure and Python files needed so that you can create an Azure OpenAI gpt-4o model deployment and then perform entity extraction using the [structured outputs mode](https://learn.microsoft.com/azure/ai-services/openai/how-to/structured-outputs?tabs=python-secure) and the Python openai SDK. Example scripts are provided for extracting details from images, PDFs, webpages, and GitHub issues.

* [Features](#features)
* [Getting started](#getting-started)
  * [GitHub Codespaces](#github-codespaces)
  * [VS Code Dev Containers](#vs-code-dev-containers)
  * [Local environment](#local-environment)
* [Deployment](#deployment)
* [Running the Python examples](#running-the-python-examples)
* [Guidance](#guidance)
  * [Costs](#costs)
  * [Security guidelines](#security-guidelines)
* [Resources](#resources)

## Features

* Provisions an Azure OpenAI account with keyless authentication enabled
* Grants the "Cognitive Services OpenAI User" RBAC role to your user account
* Deploys a gpt-4o model, version 2024-08-06 (the [only version supported for structured outputs](https://learn.microsoft.com/azure/ai-services/openai/how-to/structured-outputs?tabs=python-secure#supported-models)
* Example scripts use the [openai Python package](https://pypi.org/project/openai/) and [Pydantic models](https://docs.pydantic.dev/) to make requests for structured outputs

### Architecture diagram

![Architecture diagram: Microsoft Entra managed identity connecting to Azure AI services](./readme_diagram.png)

## Getting started

You have a few options for getting started with this template.
The quickest way to get started is GitHub Codespaces, since it will setup all the tools for you, but you can also [set it up locally](#local-environment).

### GitHub Codespaces

You can run this template virtually by using GitHub Codespaces. The button will open a web-based VS Code instance in your browser:

1. Open the template (this may take several minutes):

    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/azure-openai-entity-extraction)

2. Open a terminal window
3. Continue with the [deployment steps](#deployment)

### VS Code Dev Containers

A related option is VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/azure-openai-entity-extraction)

3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
4. Continue with the [deployment steps](#deployment)

### Local environment

1. Make sure the following tools are installed:

    * [Azure Developer CLI (azd)](https://aka.ms/install-azd)
    * [Python 3.9+](https://www.python.org/downloads/)

2. Make a new directory called `azure-openai-entity-extraction` and clone this template into it using the `azd` CLI:

    ```shell
    azd init -t azure-openai-entity-extraction
    ```

    You can also use git to clone the repository if you prefer.

3. Continue with the [deployment steps](#deployment)

## Deployment

1. Login to Azure:

    ```shell
    azd auth login
    ```

    For GitHub Codespaces users, if the previous command fails, try:

   ```shell
    azd auth login --use-device-code
    ```

2. Provision the OpenAI account:

    ```shell
    azd provision
    ```

    It will prompt you to provide an `azd` environment name (like "entityext"), select a subscription from your Azure account, and select a [location where the OpenAI model is available](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#standard-deployment-model-availability) (like "canadaeast"). Then it will provision the resources in your account and deploy the latest code.

    ⚠️ If you get an error or timeout with deployment, changing the location can help, as there may be availability constraints for the OpenAI resource. To change the location run:

    ```shell
    azd env set AZURE_LOCATION "yournewlocationname"
    ```

3. When `azd` has finished, you should have an OpenAI account you can use locally when logged into your Azure account, and a `.env` file should now exist with your Azure OpenAI configuration.

4. Then you can proceed to [run the Python examples](#running-the-python-examples).

## Running the Python examples

To run the samples, you'll either need to have already [deployed the Azure OpenAI account](#deployment) or use GitHub models.

1. Check that the `.env` file exists in the root of the project. If you [deployed an Azure OpenAI account](#deployment), it should have been created for you, and look like this:

    ```shell
    OPENAI_HOST=azure
    AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4o
    AZURE_OPENAI_SERVICE=your-service-name
    AZURE_TENANT_ID=your-tenant-id-1234
    ```

    If you're using GitHub models, create a `.env` file with the following content:

    ```shell
    OPENAI_HOST=github
    GITHUB_TOKEN=
    ```

    You can create a GitHub token by following the [GitHub documentation](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token),
    or open this project inside GitHub Codespaces where the token is already exposed as an environment variable.

2. If you're not already running in a Codespace or Dev Container, create a Python virtual environment.

3. Install the requirements:

    ```shell
    python -m pip install -r requirements.txt
    ```

4. Run an example by running either `python example_file.py` or selecting the `Run` button on the opened file. Available examples:

    | Script filename       | Description                                                                 |
    |---------------------------|-----------------------------------------------------------------------------|
    | `basic_azure.py`          | A basic example that uses deployed Azure OpenAI resource to extract from string input. |
    | `basic_githubmodels.py`         | A basic example that uses free gpt-4o from GitHub Models  to extract from string input. |
    | `extract_github_issue.py` | Fetches a public issue using the GitHub API, and then extracts details.     |
    | `extract_github_repo.py`  | Fetches a public README using the GitHub API, and then extracts details.    |
    | `extract_image_graph.py`  | Parses a local image of a graph and extracts details like title, axis, legend. |
    | `extract_image_table.py`  | Parses a local image with tables and extracts nested tabular data.          |
    | `extract_pdf_receipt.py`  | Parses a local PDF using `pymupdf`, which converts it to Markdown, and extracts order details. |
    | `extract_webpage.py`      | Parses a blog post using `BeautifulSoup`, and extracts title, description, and tags. |

## Guidance

### Costs

This template creates only the Azure OpenAI resource, which is free to provision. However, you will be charged for the usage of the Azure OpenAI chat completions API. The pricing is based on the number of tokens used, with around 1-3 tokens used per word. You can find the pricing details for the OpenAI API on the [Azure Cognitive Services pricing page](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/).

### Security guidelines

This template uses [keyless authentication](https://learn.microsoft.com/azure/developer/ai/keyless-connections) for authenticating to the Azure OpenAI resource. This is a secure way to authenticate to Azure resources without needing to store credentials in your code. Your Azure user account is assigned the "Cognitive Services OpenAI User" role, which allows you to access the OpenAI resource. You can find more information about the permissions of this role in the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control).

For further security, you could also deploy the Azure OpenAI inside a private virtual network (VNet) and use a private endpoint to access it. This would prevent the OpenAI resource from being accessed from the public internet.

## Resources

* [How to use structured outputs](https://learn.microsoft.com/azure/ai-services/openai/how-to/structured-outputs?tabs=python-secure#supported-models)
