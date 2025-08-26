from fluid_api_agent.main import (
    fluid_api_request,
    batch_fluid_api_request,
)

# Example 1: Basic API Request
# Make a simple API request with default parameters
basic_request = fluid_api_request(
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
)
print("\n=== Basic Request ===")
print(basic_request.model_dump_json(indent=4))

# Example 2: Request with Raw Response
# Get the raw response without any processing
raw_request = fluid_api_request(
    "Generate an API request to get a random joke from https://official-joke-api.appspot.com/random_joke",
    return_raw=True,
)
print("\n=== Raw Request ===")
print(raw_request.model_dump_json(indent=4))

# Example 3: Verbose Request
# Enable detailed logging during request processing
verbose_request = fluid_api_request(
    "Generate an API request to get weather data for New York from OpenWeatherMap",
    verbose=True,
)
print("\n=== Verbose Request ===")
print(verbose_request.model_dump_json(indent=4))

# Example 4: Request with Custom Documentation
# Provide API documentation to improve request generation
docs = """
API Endpoint: https://api.example.com/v1/users
Methods: GET, POST
Authentication: Bearer token required
"""
custom_doc_request = fluid_api_request(
    "Generate a request to get all users",
    documentation=docs,
    verbose=True,
)
print("\n=== Request with Documentation ===")
print(custom_doc_request.model_dump_json(indent=4))

# Example 5: Batch Processing
# Process multiple API requests in sequence
print("\n=== Batch Request ===")
batch_results = batch_fluid_api_request(
    tasks=[
        "Generate an API request to get a random dog fact from https://dogapi.dog/api/v2/facts",
        "Generate an API request to get a random quote from https://api.quotable.io/random",
        "Generate an API request to get Bitcoin price from CoinGecko public API",
    ],
    verbose=True,
)
for i, result in enumerate(batch_results, 1):
    print(f"\nBatch Result {i}:")
    print(result.model_dump_json(indent=4))
