# TODO: Add the ability to upload documentation to the agent on the api endpoint
# TODO: Add the ability for api key injection through .ENVs or pass it into the prompt
#

import os
import json
import requests
from loguru import logger
from swarms import Agent
from swarm_models import OpenAIChat
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import aiohttp
import asyncio
from pydantic import BaseModel, ValidationError
from functools import lru_cache
from typing import List

# Load environment variables
load_dotenv()

# Get the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Validate API Key
if not api_key:
    raise ValueError(
        "OpenAI API key is not set. Please check your .env file."
    )

# More extensive and instructive system prompt
API_REQUEST_SYS_PROMPT = """
You are an intelligent API agent. Your sole task is to interpret user instructions and generate a JSON object that defines an API request. 
The JSON must strictly follow this structure:

{
    "method": "HTTP_METHOD", // GET, POST, PUT, DELETE
    "url": "API_ENDPOINT_URL", // Fully qualified API URL
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer <token>", // Optional
        "Additional-Headers": "value" // Optional
    },
    "body": {
        "key1": "value1", // Include key-value pairs for POST, PUT, or DELETE requests
        "key2": "value2"
    }
}

Guidelines:
1. Always use HTTP methods appropriate for the task: GET for fetching data, POST for creating data, PUT for updating data, DELETE for deleting data.
2. Include a valid API URL in the "url" field.
3. Populate the "headers" field with standard headers, such as "Content-Type" and "Authorization" if necessary.
4. For GET requests, leave the "body" field as an empty object: {}.
5. Provide accurate key-value pairs in the "body" for other methods.
6. Do not include any additional text, comments, or explanations outside of the JSON response.
7. Ensure the JSON is valid and properly formatted.

Example Task: "Generate an API request to fetch weather data for New York from https://api.weather.com/v3/weather."
Example Output:
{
    "method": "GET",
    "url": "https://api.weather.com/v3/weather",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer <token>"
    },
    "body": {}
}
Your response must always be a valid JSON object.
"""

# Initialize the LLM model
model = OpenAIChat(
    openai_api_key=api_key, model_name="gpt-4o-mini", temperature=0.1
)

# Initialize the Agent
agent = Agent(
    agent_name="API-Request-Agent",
    system_prompt=API_REQUEST_SYS_PROMPT,
    llm=model,
    max_loops=1,
    saved_state_path="api_request_agent.json",
    context_length=200000,
    return_step_meta=False,
    output_type="string",
    streaming_on=False,
)


# Define API request schema using Pydantic
class APIRequestSchema(BaseModel):
    method: str
    url: str
    headers: dict
    body: dict


def validate_agent_output(output: dict) -> APIRequestSchema:
    """
    Validates the agent's output using Pydantic schema.

    Args:
        output (dict): The output JSON from the agent.

    Returns:
        APIRequestSchema: Validated API request object.
    """
    try:
        return APIRequestSchema(**output)
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise


@lru_cache(maxsize=100)
def get_api_token() -> str:
    """
    Retrieves or refreshes an API token for authentication.

    Returns:
        str: A valid API token.
    """
    logger.info("Fetching API token...")
    # Example token retrieval logic
    response = requests.post(
        "https://auth.example.com/token",
        data={
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "grant_type": "client_credentials",
        },
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    logger.info("API token retrieved successfully.")
    return token


def inject_token(headers: dict) -> dict:
    """
    Injects an authentication token into the headers.

    Args:
        headers (dict): The request headers.

    Returns:
        dict: Updated headers with the token.
    """
    headers["Authorization"] = f"Bearer {get_api_token()}"
    return headers


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
)
async def execute_async_api_call(
    api_request: APIRequestSchema,
) -> dict:
    """
    Executes an asynchronous API call based on the provided request.

    Args:
        api_request (APIRequestSchema): The validated API request object.

    Returns:
        dict: Response from the API.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                api_request.method,
                api_request.url,
                headers=api_request.headers,
                json=api_request.body,
            ) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"API call failed: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
)
def parse_agent_response(response: str) -> dict:
    """
    Parses the agent's response as JSON with retry logic.

    Args:
        response (str): Raw response from the agent.

    Returns:
        dict: Parsed JSON object.
    """
    try:
        logger.info("Parsing agent response...")
        api_request = json.loads(response)
        logger.info(f"Parsed API request: {api_request}")
        return api_request
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode agent response as JSON: {e}")
        raise


async def process_task_with_agent(task: str) -> None:
    """
    Prompts the agent, validates the response, and executes the API request asynchronously.

    Args:
        task (str): The user's task description.

    Returns:
        None
    """
    try:
        logger.info(f"Task received: {task}")

        # Prompt the agent
        response = agent.run(task)
        logger.info(f"Agent response: {response}")

        # Parse and validate the agent's output
        api_request = validate_agent_output(
            parse_agent_response(response)
        )

        # Inject token
        # api_request.headers = inject_token(api_request.headers)

        # Execute the API call
        api_response = await execute_async_api_call(api_request)
        logger.info(f"API response: {api_response}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


def fluid_api_request(task: str) -> None:
    """
    Asynchronously processes a single API request task.

    Args:
        task (str): The task description to be processed by the agent.

    Returns:
        None

    Raises:
        Exception: If any error occurs during task processing
    """
    try:
        logger.info(f"Processing async API request for task: {task}")
        asyncio.run(process_task_with_agent(task))
        logger.success(
            f"Successfully completed API request for task: {task}"
        )
    except Exception as e:
        logger.error(
            f"Failed to process API request for task: {task}. Error: {e}"
        )
        raise


def fluid_api_request_sync(task: str) -> None:
    """
    Synchronously processes a single API request task.

    Args:
        task (str): The task description to be processed by the agent.

    Returns:
        None

    Raises:
        Exception: If any error occurs during task processing
    """
    try:
        logger.info(f"Processing sync API request for task: {task}")
        process_task_with_agent(task)
        logger.success(
            f"Successfully completed sync API request for task: {task}"
        )
    except Exception as e:
        logger.error(
            f"Failed to process sync API request for task: {task}. Error: {e}"
        )
        raise


def batch_fluid_api_request(tasks: List[str]) -> None:
    """
    Processes multiple API request tasks sequentially.

    Args:
        tasks (List[str]): List of task descriptions to be processed.

    Returns:
        None

    Raises:
        Exception: If any error occurs during batch processing
    """
    try:
        logger.info(
            f"Starting batch processing of {len(tasks)} tasks"
        )
        for i, task in enumerate(tasks, 1):
            try:
                logger.info(f"Processing task {i}/{len(tasks)}")
                fluid_api_request(task)
            except Exception as e:
                logger.error(
                    f"Failed to process task {i}/{len(tasks)}: {e}"
                )
                continue
        logger.success("Completed batch processing")
    except Exception as e:
        logger.error(f"Fatal error in batch processing: {e}")
        raise
