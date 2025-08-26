# FluidAPI: Natural Language API Requests

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

## Overview

**FluidAPI** is an enterprise-grade framework that enables natural language interaction with APIs. Eliminate the complexity of JSON formatting, header management, and complex request structures by simply describing your requirements in plain English. FluidAPI automatically handles the rest.

Built on the robust **Swarms Framework** and developed by [Kye Gomez](https://github.com/kyegomez), FluidAPI revolutionizes API integration workflows for enterprise applications.

---

## Key Features

- **Natural Language Processing**: Transform natural language descriptions into fully functional API requests
- **AI-Powered Execution**: Leverages the [Swarms Framework](https://github.com/kyegomez/swarms) for intelligent and dynamic API handling
- **Seamless Integration**: Replace complex API workflows with intuitive, human-readable commands
- **Enterprise Reliability**: Built-in retry mechanisms and comprehensive error handling for production environments
- **Dynamic Authentication Management**: Automated token management and secure credential injection
- **Batch Processing**: Execute multiple API requests sequentially with intelligent error handling
- **Flexible Response Handling**: Choose between processed JSON responses or raw API responses

---

## Installation

Install the `fluid-api-agent` package using pip:

```bash
pip install fluid-api-agent
```

---

## Quick Start

### Basic Implementation

```python
from fluid_api_agent.main import fluid_api_request

# Basic API Request Example
basic_request = fluid_api_request(
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
)

print(basic_request)
```

### Advanced Implementation with Class-Based Approach

```python
from fluid_api_agent.main import FluidAPI

# Initialize FluidAPI with custom configuration
fluid_api = FluidAPI(
    model_name="gpt-4.1",
    verbose=True,
    return_raw=False
)

# Execute API request
response = fluid_api.run(
    "Generate an API request to get weather data for New York from OpenWeatherMap"
)

print(response.model_dump_json(indent=4))
```

---

## Core Components

### 1. FluidAPI Class

The main class that provides a flexible interface for API requests:

```python
from fluid_api_agent.main import FluidAPI

# Initialize with custom settings
fluid_api = FluidAPI(
    model_name="gpt-4.1",        # LLM model to use
    documentation="API docs...",  # Optional API documentation
    verbose=True,                 # Enable detailed logging
    output_type="final",          # Output format
    return_raw=False              # Return raw or processed response
)

# Methods available:
# - run(task): Synchronous execution
# - fluid_api_request(task): Asynchronous execution
# - load_documentation(paths): Load API documentation from files
```

### 2. Data Models

**APIRequestSchema**: Defines the structure of API requests
```python
class APIRequestSchema(BaseModel):
    method: str      # HTTP method (GET, POST, PUT, DELETE)
    url: str         # API endpoint URL
    headers: dict    # Request headers
    body: dict       # Request body
```

**APIResponseSchema**: Contains the complete API response
```python
class APIResponseSchema(BaseModel):
    request: APIRequestSchema           # Original request
    response: Union[Dict[str, Any], str]  # API response data
    status_code: int                   # HTTP status code
    elapsed_time: float                # Request execution time
    metadata: Dict[str, Any]           # Additional response metadata
```

---

## Usage Examples

### Basic API Requests

```python
from fluid_api_agent.main import fluid_api_request

# Simple GET request
cat_fact = fluid_api_request(
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
)

# POST request with data
user_creation = fluid_api_request(
    "Generate an API request to create a new user with name 'John Doe' and email 'john@example.com'"
)
```

### Advanced Configuration

```python
from fluid_api_agent.main import fluid_api_request

# With custom model and verbose logging
weather_data = fluid_api_request(
    "Generate an API request to get weather data for London from OpenWeatherMap",
    model_name="gpt-4",
    verbose=True,
    return_raw=False
)

# With API documentation
docs = """
API Endpoint: https://api.example.com/v1/users
Methods: GET, POST, PUT, DELETE
Authentication: Bearer token required
Rate Limit: 100 requests per minute
"""

user_request = fluid_api_request(
    "Generate a request to get all users with pagination (page 1, limit 10)",
    documentation=docs,
    verbose=True
)
```

### Batch Processing

```python
from fluid_api_agent.main import batch_fluid_api_request

# Process multiple API requests sequentially
batch_results = batch_fluid_api_request(
    tasks=[
        "Generate an API request to get Bitcoin (BTC) price from CoinGecko public API",
        "Generate an API request to get Solana (SOL) price from CoinGecko public API", 
        "Generate an API request to get Ethereum (ETH) price from CoinGecko public API",
        "Generate an API request to get a random quote from https://api.quotable.io/random",
        "Generate an API request to get a random dog fact from https://dogapi.dog/api/v2/facts"
    ],
    verbose=True,
    return_raw=False
)

# Process results
for i, result in enumerate(batch_results.split('\n\n'), 1):
    print(f"\n=== Batch Result {i} ===")
    print(result)
```

### Class-Based Batch Processing

```python
from fluid_api_agent.main import FluidAPI

# Initialize FluidAPI instance
fluid_api = FluidAPI(
    model_name="gpt-4.1",
    verbose=True,
    return_raw=False
)

# Define batch tasks
tasks = [
    "Generate an API request to get current Bitcoin price",
    "Generate an API request to get latest news from NewsAPI",
    "Generate an API request to get weather forecast for Tokyo"
]

# Process batch tasks
responses = []
for task in tasks:
    try:
        response = fluid_api.run(task)
        responses.append(response)
        print(f"✓ Completed: {task}")
    except Exception as e:
        print(f"✗ Failed: {task} - {e}")

# Process all responses
for i, response in enumerate(responses, 1):
    print(f"\n=== Response {i} ===")
    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_time:.2f}s")
    print(f"Data: {response.response}")
```

### Documentation Integration

```python
from fluid_api_agent.main import FluidAPI

# Load documentation from files
fluid_api = FluidAPI(
    model_name="gpt-4.1",
    verbose=True
)

# Load single documentation file
docs = fluid_api.load_documentation("api_documentation.md")

# Load multiple documentation files
docs = fluid_api.load_documentation([
    "api_overview.md",
    "endpoints.md", 
    "authentication.md"
])

# Use loaded documentation for requests
response = fluid_api.run(
    "Generate an API request to authenticate and get user profile",
    documentation=docs
)
```

---

## Error Handling & Retry Logic

FluidAPI includes built-in retry mechanisms and comprehensive error handling:

```python
from fluid_api_agent.main import FluidAPI

try:
    fluid_api = FluidAPI(verbose=True)
    response = fluid_api.run("Generate an API request to external service")
    
except ValidationError as e:
    print(f"Invalid API request format: {e}")
    
except aiohttp.ClientError as e:
    print(f"API call failed: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

**Retry Configuration**: Automatically retries failed requests with exponential backoff (3 attempts, 2-10 second intervals).

---

## Configuration

### Environment Variables

FluidAPI utilizes environment variables for secure credential management:

```env
OPENAI_API_KEY=your-openai-api-key
WORKSPACE_DIR="agent_workspace"
```

### Supported Documentation Formats

FluidAPI supports loading documentation from various file formats:
- `.txt` - Plain text files
- `.md` - Markdown files  
- `.mdx` - Extended Markdown files

---

## Performance Optimization

### Caching

```python
from fluid_api_agent.main import FluidAPI

# Agent initialization is cached for performance
fluid_api = FluidAPI(verbose=True)

# Multiple requests use the same cached agent instance
response1 = fluid_api.run("First request")
response2 = fluid_api.run("Second request")  # Uses cached agent
```

### Batch Processing Benefits

- **Sequential Execution**: Process multiple requests efficiently
- **Error Isolation**: Individual task failures don't affect others
- **Progress Tracking**: Monitor batch execution with verbose logging
- **Resource Management**: Optimized memory and connection handling

---

## Enterprise Features

### Security

- **Credential Management**: Secure API key handling through environment variables
- **Input Validation**: Pydantic-based request/response validation
- **Error Sanitization**: Safe error messages for production environments

### Monitoring & Logging

```python
from fluid_api_agent.main import FluidAPI

# Enable comprehensive logging
fluid_api = FluidAPI(verbose=True)

# Monitor request execution
response = fluid_api.run("API request task")
print(f"Request completed in {response.elapsed_time:.2f} seconds")
print(f"Response status: {response.status_code}")
print(f"Response metadata: {response.metadata}")
```

### Scalability

- **Async Support**: Built-in asynchronous execution capabilities
- **Connection Pooling**: Efficient HTTP connection management
- **Memory Optimization**: Intelligent resource allocation and cleanup

---

## Development Setup

### Repository Cloning

```bash
git clone https://github.com/The-Swarm-Corporation/fluidapi.git
cd fluidapi
```

### Dependency Installation

```bash
pip install -r requirements.txt
```

### Running Examples

```bash
# Basic examples
python examples/example.py

# Batch processing examples  
python examples/batched_example.py

# OpenAI integration examples
python examples/openai_example.py
python examples/openai_example_v2.py

# Stripe API examples
python examples/stripe.py
```

---

## Architecture

FluidAPI leverages the **Swarms Framework** to provide:

1. **Natural Language Parsing**: Advanced NLP capabilities for request interpretation
2. **Dynamic Request Construction**: Intelligent API request generation
3. **Intelligent Response Processing**: Automated response handling and error management
4. **Flexible Execution Models**: Both synchronous and asynchronous processing
5. **Extensible Documentation**: Support for custom API documentation integration

For comprehensive information about the Swarms Framework, visit [here](https://github.com/kyegomez/swarms).

---

## API Reference

### Main Functions

- `fluid_api_request(task, **kwargs)`: Quick single request execution
- `batch_fluid_api_request(tasks, **kwargs)`: Batch processing of multiple requests

### FluidAPI Class Methods

- `run(task)`: Synchronous task execution
- `fluid_api_request(task)`: Asynchronous task execution  
- `load_documentation(paths)`: Load and combine documentation files
- `initialize_agent()`: Initialize the underlying Swarms agent

### Configuration Options

- `model_name`: LLM model selection (default: "gpt-4.1")
- `documentation`: Custom API documentation string
- `verbose`: Enable detailed logging (default: False)
- `output_type`: Agent output format (default: "final")
- `return_raw`: Return raw API responses (default: False)

---

## Development Roadmap

- [x] Core FluidAPI class implementation
- [x] Batch processing capabilities
- [x] Documentation integration
- [x] Comprehensive error handling
- [x] Async/sync execution modes
- [ ] REST API wrapper
- [ ] WebSocket support
- [ ] Rate limiting and throttling
- [ ] Advanced caching strategies
- [ ] Performance benchmarking tools
- [ ] Extended unit and integration test suite

---

## Contributing

We welcome contributions from the community. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive docstrings for new functions
- Include unit tests for new features
- Update documentation for API changes

---

## License

FluidAPI is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete terms and conditions.

---

## Contact Information

- **Lead Developer**: [Kye Gomez](https://github.com/kyegomez)
- **Repository**: [The-Swarm-Corporation/FluidAPI](https://github.com/The-Swarm-Corporation/fluidapi)
- **Package Distribution**: [fluid-api-agent](https://pypi.org/project/fluid-api-agent/)
- **Discord**: [Join our community](https://discord.gg/agora-999382051935506503)

---

## Examples Directory

For comprehensive usage examples, explore the `examples/` directory:

- **[example.py](examples/example.py)** - Basic usage examples
- **[batched_example.py](examples/batched_example.py)** - Batch processing examples
- **[openai_example.py](examples/openai_example.py)** - OpenAI integration examples
- **[openai_example_v2.py](examples/openai_example_v2.py)** - Advanced OpenAI examples
- **[stripe.py](examples/stripe.py)** - Stripe API integration examples

---

**Transform your API integration experience. With FluidAPI, complex API workflows become simple, natural language commands.**

*Built with ❤️ by the Swarms community*
