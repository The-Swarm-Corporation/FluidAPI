# TODO: Add the ability to upload documentation to the agent on the api endpoint
# TODO: Add the ability for api key injection through .ENVs or pass it into the prompt
#

import os
import json
from loguru import logger
from swarms import Agent
from swarm_models import OpenAIChat
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import aiohttp
import asyncio
from pydantic import BaseModel, ValidationError
from pathlib import Path
from typing import List, Union, Dict, Any, Optional


# Add these new constants after the existing ones
SUPPORTED_DOC_EXTENSIONS = {".txt", ".md", ".mdx"}
VERBOSE = False  # Default verbose setting


# Add this function to handle documentation loading
def load_documentation(
    doc_paths: Union[str, List[str]], verbose: bool = False
) -> str:
    """
    Loads documentation from one or more files and combines them into a single string.

    Args:
        doc_paths: Single path or list of paths to documentation files
        verbose: Whether to enable verbose logging

    Returns:
        str: Combined documentation text
    """
    if isinstance(doc_paths, str):
        doc_paths = [doc_paths]

    combined_docs = []

    for path in doc_paths:
        file_path = Path(path)
        if verbose:
            logger.info(f"Loading documentation from {file_path}")

        if not file_path.exists():
            if verbose:
                logger.error(
                    f"Documentation file not found: {file_path}"
                )
            continue

        if file_path.suffix.lower() not in SUPPORTED_DOC_EXTENSIONS:
            if verbose:
                logger.warning(
                    f"Unsupported file type {file_path.suffix} for {file_path}"
                )
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_docs.append(content)
                if verbose:
                    logger.info(
                        f"Successfully loaded {len(content)} characters from {file_path}"
                    )
        except Exception as e:
            if verbose:
                logger.error(f"Error reading {file_path}: {e}")

    return "\n\n".join(combined_docs)


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


# Modify the Agent initialization to accept documentation
def initialize_agent(
    documentation: Optional[str] = None, verbose: bool = False
) -> Agent:
    """
    Initialize the API Request Agent with optional documentation.

    Args:
        documentation: Optional API documentation to inject
        verbose: Whether to enable verbose logging

    Returns:
        Agent: Configured API request agent
    """
    system_prompt = API_REQUEST_SYS_PROMPT
    if documentation:
        system_prompt += f"\n\nAPI Documentation:\n{documentation}"

    if verbose:
        logger.info("Initializing agent with custom documentation")

    return Agent(
        agent_name="API-Request-Agent",
        system_prompt=system_prompt,
        llm=model,
        max_loops=1,
        saved_state_path="api_request_agent.json",
        context_length=200000,
        return_step_meta=False,
        output_type="string",
        streaming_on=verbose,  # Enable streaming for verbose mode
    )


# Define API request schema using Pydantic
class APIRequestSchema(BaseModel):
    method: str
    url: str
    headers: dict
    body: dict


class APIResponseSchema(BaseModel):
    request: APIRequestSchema
    response: Union[Dict[str, Any], str]
    status_code: int
    elapsed_time: float
    metadata: Dict[str, Any]


def validate_agent_output(
    output: dict, verbose: bool = False
) -> APIRequestSchema:
    """
    Validates the agent's output using Pydantic schema.

    Args:
        output (dict): The output JSON from the agent.
        verbose (bool): Whether to enable verbose logging

    Returns:
        APIRequestSchema: Validated API request object.
    """
    try:
        return APIRequestSchema(**output)
    except ValidationError as e:
        if verbose:
            logger.error(f"Validation error: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
)
async def execute_async_api_call(
    api_request: APIRequestSchema,
    return_raw: bool = False,
    verbose: bool = False,
) -> APIResponseSchema:
    """
    Executes an asynchronous API call based on the provided request.

    Args:
        api_request (APIRequestSchema): The validated API request object.
        return_raw (bool): Whether to return response as raw string
        verbose (bool): Whether to enable verbose logging

    Returns:
        APIResponseSchema: Response object containing request, response and metadata
    """
    try:
        start_time = asyncio.get_event_loop().time()
        async with aiohttp.ClientSession() as session:
            async with session.request(
                api_request.method,
                api_request.url,
                headers=api_request.headers,
                json=api_request.body,
            ) as response:
                elapsed = asyncio.get_event_loop().time() - start_time
                response.raise_for_status()

                if return_raw:
                    response_data = await response.text()
                else:
                    response_data = await response.json()

                return APIResponseSchema(
                    request=api_request,
                    response=response_data,
                    status_code=response.status,
                    elapsed_time=elapsed,
                    metadata={
                        "content_type": response.content_type,
                        "content_length": response.content_length,
                        "headers": dict(response.headers),
                    },
                )
    except aiohttp.ClientError as e:
        if verbose:
            logger.error(f"API call failed: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
)
def parse_agent_response(
    response: str, verbose: bool = False
) -> dict:
    """
    Parses the agent's response as JSON with retry logic.

    Args:
        response (str): Raw response from the agent.
        verbose (bool): Whether to enable verbose logging

    Returns:
        dict: Parsed JSON object.
    """
    try:
        if verbose:
            logger.info("Parsing agent response...")
        api_request = json.loads(response)
        if verbose:
            logger.info(f"Parsed API request: {api_request}")
        return api_request
    except json.JSONDecodeError as e:
        if verbose:
            logger.error(
                f"Failed to decode agent response as JSON: {e}"
            )
        raise


async def process_task_with_agent(
    task: str,
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
) -> APIResponseSchema:
    """
    Prompts the agent, validates the response, and executes the API request asynchronously.

    Args:
        task (str): The user's task description.
        documentation (str): Optional API documentation
        return_raw (bool): Whether to return response as raw string
        verbose (bool): Whether to enable verbose logging

    Returns:
        APIResponseSchema: Response object containing request, response and metadata
    """
    try:
        if verbose:
            logger.info(f"Task received: {task}")

        # Prompt the agent
        agent = initialize_agent(documentation, verbose=verbose)
        response = agent.run(task)
        if verbose:
            logger.info(f"Agent response: {response}")

        # Parse and validate the agent's output
        api_request = validate_agent_output(
            parse_agent_response(response, verbose), verbose
        )

        # Execute the API call
        api_response = await execute_async_api_call(
            api_request, return_raw, verbose
        )
        if verbose:
            logger.info(f"API response: {api_response}")
        return api_response

    except Exception as e:
        if verbose:
            logger.error(f"An error occurred: {e}")
        raise


def fluid_api_request(
    task: str,
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
) -> APIResponseSchema:
    """
    Asynchronously processes a single API request task.

    Args:
        task (str): The task description to be processed by the agent.
        documentation (str): Optional API documentation
        return_raw (bool): Whether to return response as raw string
        verbose (bool): Whether to enable verbose logging

    Returns:
        APIResponseSchema: Response object containing request, response and metadata

    Raises:
        Exception: If any error occurs during task processing
    """
    try:
        if verbose:
            logger.info(
                f"Processing async API request for task: {task}"
            )
        response = asyncio.run(
            process_task_with_agent(
                task, documentation, return_raw, verbose
            )
        )
        if verbose:
            logger.success(
                f"Successfully completed API request for task: {task}"
            )
        return response
    except Exception as e:
        if verbose:
            logger.error(
                f"Failed to process API request for task: {task}. Error: {e}"
            )
        raise


def fluid_api_request_sync(
    task: str,
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
) -> APIResponseSchema:
    """
    Synchronously processes a single API request task.

    Args:
        task (str): The task description to be processed by the agent.
        documentation (str): Optional API documentation
        return_raw (bool): Whether to return response as raw string
        verbose (bool): Whether to enable verbose logging

    Returns:
        APIResponseSchema: Response object containing request, response and metadata

    Raises:
        Exception: If any error occurs during task processing
    """
    try:
        if verbose:
            logger.info(
                f"Processing sync API request for task: {task}"
            )
        response = process_task_with_agent(
            task, documentation, return_raw, verbose
        )
        if verbose:
            logger.success(
                f"Successfully completed sync API request for task: {task}"
            )
        return response
    except Exception as e:
        if verbose:
            logger.error(
                f"Failed to process sync API request for task: {task}. Error: {e}"
            )
        raise


def batch_fluid_api_request(
    tasks: List[str],
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
) -> List[APIResponseSchema]:
    """
    Processes multiple API request tasks sequentially.

    Args:
        tasks (List[str]): List of task descriptions to be processed.
        documentation (str): Optional API documentation
        return_raw (bool): Whether to return responses as raw strings
        verbose (bool): Whether to enable verbose logging

    Returns:
        List[APIResponseSchema]: List of response objects containing requests, responses and metadata

    Raises:
        Exception: If any error occurs during batch processing
    """
    try:
        if verbose:
            logger.info(
                f"Starting batch processing of {len(tasks)} tasks"
            )
        responses = []
        for i, task in enumerate(tasks, 1):
            try:
                if verbose:
                    logger.info(f"Processing task {i}/{len(tasks)}")
                response = fluid_api_request(
                    task, documentation, return_raw, verbose
                )
                responses.append(response)
            except Exception as e:
                if verbose:
                    logger.error(
                        f"Failed to process task {i}/{len(tasks)}: {e}"
                    )
                continue
        if verbose:
            logger.success("Completed batch processing")
        return responses
    except Exception as e:
        if verbose:
            logger.error(f"Fatal error in batch processing: {e}")
        raise
