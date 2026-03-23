# TaskGenerator-travail

ClickUp Meeting Processor is a FastAPI service that turns meeting summaries into ClickUp tasks using Azure OpenAI, then verifies and applies create/update actions in ClickUp.

## Features

- Generate tasks from meeting summaries using Azure OpenAI
- Verify generated tasks against existing ClickUp tasks
- Apply create/update actions in ClickUp
- Resolve assignees using an Excel username-to-email mapping
- REST API with health and meeting processing endpoints

## Architecture

- Presentation: FastAPI routers in src/presnetation/api
- Application: use cases and services in src/application
- Domain: models, ports, and exceptions in src/domain
- Infrastructure: adapters for ClickUp, Excel, OpenAI, prompts in src/infrastructure

## Requirements

- Python 3.14+ (project currently uses 3.14)
- Virtual environment recommended

Install dependencies:

```
python -m pip install -r requirements.txt
```

## Configuration

Create a .env file (or set environment variables) with the following values:

- CLICKUP_API_TOKEN: ClickUp API token
- EXCEL_MAIL_PATH: Full path to the Excel file with USERNAME and MAIL columns
- AZURE_OPENAI_API_KEY: Azure OpenAI API key
- AZURE_OPENAI_API_VERSION: Azure OpenAI API version
- AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
- AZURE_OPENAI_DEPLOYMENT_NAME: Azure OpenAI deployment name

Example .env:

```
CLICKUP_API_TOKEN=your_clickup_token
EXCEL_MAIL_PATH=path\to\users.xlsx
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
```

## Run the API

From the project root:

```
python -m uvicorn src.presnetation.api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health check

```
GET /health
```

Response:

```
{"status": "ok"}
```

### Process a meeting summary

```
POST /meeting/process
```

Request body:

```
{
  "space_id": "abc123xyz",
  "meeting_summary": "Summary in Arabic"
}
```

Response body:

```
{
  "total": 1,
  "created": 1,
  "updated": 0,
  "results": [
    {
      "action": "create",
      "task_name": "Task A",
      "task_description": "Desc A",
      "task_assigne": "alice",
      "task_status": "todo",
      "task_priority": "high",
      "folder": "dev",
      "task_id": null
    }
  ]
}
```

## Prompts

Prompt templates are stored in:

- src/infrastructure/prompts/templates

The loader expects .prompty files and uses Jinja-like variables with [[ var ]].

## Tests

Current test counts:

- Unit tests: 10
- Integration tests: 3
- Total: 13

Run all tests:

```
python -m pytest
```

Warnings are filtered by pytest.ini.

## Project Structure (High Level)

```
src/
  application/
  domain/
  infrastructure/
  presnetation/
    api/
      routers/
```

## Notes

- The API relies on ClickUp list statuses and priorities pulled from ClickUp.
- Assignee resolution uses Excel matching on usernames to emails.
- If prompts or required inputs are missing, the API raises domain exceptions handled by FastAPI.
