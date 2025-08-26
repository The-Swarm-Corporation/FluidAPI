import asyncio
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
from loguru import logger
from pydantic import BaseModel, ValidationError
from swarms import Agent
from tenacity import retry, stop_after_attempt, wait_exponential


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


# Add these new constants after the existing ones
SUPPORTED_DOC_EXTENSIONS = {".txt", ".md", ".mdx"}
VERBOSE = False  # Default verbose setting


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


class FluidAPI:
    def __init__(
        self,
        model_name: str = "gpt-4.1",
        documentation: Optional[str] = None,
        verbose: bool = False,
        output_type: str = "final",
        return_raw: bool = False,
    ):
        self.model_name = model_name
        self.documentation = documentation
        self.verbose = verbose
        self.output_type = output_type
        self.return_raw = return_raw

    # Add this function to handle documentation loading
    def load_documentation(
        self, doc_paths: Union[str, List[str]], verbose: bool = False
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

            if (
                file_path.suffix.lower()
                not in SUPPORTED_DOC_EXTENSIONS
            ):
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

    @lru_cache(maxsize=1)
    def initialize_agent(
        self,
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
        if self.documentation:
            system_prompt += (
                f"\n\nAPI Documentation:\n{self.documentation}"
            )

        if self.verbose:
            logger.info(
                "Initializing agent with custom documentation"
            )

        return Agent(
            agent_name="API-Request-Agent",
            system_prompt=system_prompt,
            agent_description="You are an intelligent API agent. Your sole task is to interpret user instructions and generate a JSON object that defines an API request. The JSON must strictly follow this structure: {method: HTTP_METHOD, url: API_ENDPOINT_URL, headers: {Content-Type: application/json, Authorization: Bearer <token>, Additional-Headers: value}, body: {key1: value1, key2: value2}}",
            model_name=self.model_name,
            max_loops=1,
            context_length=200000,
            return_step_meta=False,
            output_type=self.output_type,
        )

    async def process_task_with_agent(
        self,
        task: str,
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
            if self.verbose:
                logger.info(f"Task received: {task}")

            # Prompt the agent
            agent = self.initialize_agent()
            response = agent.run(task)
            if self.verbose:
                logger.info(f"Agent response: {response}")

            # Parse and validate the agent's output
            api_request = validate_agent_output(
                parse_agent_response(response, self.verbose),
                self.verbose,
            )

            # Execute the API call
            api_response = await execute_async_api_call(
                api_request, self.return_raw, self.verbose
            )
            if self.verbose:
                logger.info(f"API response: {api_response}")
            return api_response

        except Exception as e:
            if self.verbose:
                logger.error(f"An error occurred: {e}")
            raise

    def fluid_api_request(
        self,
        task: str,
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
            if self.verbose:
                logger.info(
                    f"Processing async API request for task: {task}"
                )
            response = asyncio.run(
                self.process_task_with_agent(
                    task=task,
                )
            )
            if self.verbose:
                logger.success(
                    f"Successfully completed API request for task: {task}"
                )
            return response
        except Exception as e:
            if self.verbose:
                logger.error(
                    f"Failed to process API request for task: {task}. Error: {e}"
                )
            raise

    def run(
        self,
        task: str,
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
            if self.verbose:
                logger.info(
                    f"Processing sync API request for task: {task}"
                )
            response = self.process_task_with_agent(
                task=task,
            )
            if self.verbose:
                logger.success(
                    f"Successfully completed sync API request for task: {task}"
                )
            return response
        except Exception as e:
            if self.verbose:
                logger.error(
                    f"Failed to process sync API request for task: {task}. Error: {e}"
                )
            raise


def fluid_api_request(
    task: str,
    model_name: str = "gpt-4.1",
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
    *args,
    **kwargs,
) -> str:
    """
    Generate and execute an API request from a natural language task description.

    This function uses the FluidAPI agent to interpret a natural language
    instruction and generate a structured API request, then executes it and
    returns the response.

    Args:
        task (str): The natural language description of the API task to perform.
        model_name (str, optional): The LLM model to use for the agent.
            Defaults to "gpt-4.1".
        documentation (str, optional): Optional API documentation to help the agent
            understand the API's structure and requirements.
        return_raw (bool, optional): If True, return the raw response from the API.
            Defaults to False.
        verbose (bool, optional): If True, enable verbose logging. Defaults to False.
        *args: Additional positional arguments passed to the FluidAPI agent.
        **kwargs: Additional keyword arguments passed to the FluidAPI agent.

    Returns:
        str: A JSON-formatted string representing the API response, including
            the request, response, and metadata.

    Raises:
        Exception: If any error occurs during task processing.
    """
    agent = FluidAPI(
        model_name=model_name,
        documentation=documentation,
        return_raw=return_raw,
        verbose=verbose,
        *args,
        **kwargs,
    )
    output = agent.fluid_api_request(task)
    return output.model_dump_json(indent=4)


def batch_fluid_api_request(
    tasks: List[str],
    documentation: str = None,
    return_raw: bool = False,
    verbose: bool = False,
) -> str:
    """
    Process multiple natural language API request tasks sequentially.

    This function takes a list of natural language task descriptions, generates
    and executes API requests for each, and returns their responses.

    Args:
        tasks (List[str]): List of natural language API task descriptions.
        documentation (str, optional): API documentation to assist the agent for all tasks.
        return_raw (bool, optional): If True, return raw responses as strings.
            Defaults to False.
        verbose (bool, optional): If True, enable verbose logging. Defaults to False.

    Returns:
        List[str]: List of JSON-formatted strings representing each API response.

    Raises:
        Exception: If any error occurs during batch processing.
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
        return "\n\n".join(responses)
    except Exception as e:
        if verbose:
            logger.error(f"Fatal error in batch processing: {e}")
        raise
