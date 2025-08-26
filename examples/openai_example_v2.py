from fluid_api_agent.main import (
    fluid_api_request,
)

# Example: Call OpenAI's GPT-3 API to generate text
openai_request = fluid_api_request(
    "Generate an API request to create a chat completion using OpenAI's API endpoint https://api.openai.com/v1/chat/completions, the api key is HERE:",
    documentation="""
    API Endpoint: https://api.openai.com/v1/chat/completions
    Authentication: Bearer token (OpenAI API key) required in header
    Method: POST
    """,
    verbose=True,
)

print(openai_request.model_dump_json(indent=4))
