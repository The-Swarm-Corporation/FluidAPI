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
from fluid_api_agent.main import (
    fluid_api_request,
)

# Basic API Request Example
basic_request = fluid_api_request(
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
)

print(basic_request.model_dump_json(indent=4))
```

### Advanced Implementation

```python
from fluid_api_agent.main import (
    fluid_api_request,
    batch_fluid_api_request,
)

# Basic API Request
# Execute a simple API request with default parameters
basic_request = fluid_api_request(
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
)
print("\n=== Basic Request ===")
print(basic_request.model_dump_json(indent=4))

# Raw Response Request
# Retrieve unprocessed response data
raw_request = fluid_api_request(
    "Generate an API request to get a random joke from https://official-joke-api.appspot.com/random_joke",
    return_raw=True
)
print("\n=== Raw Request ===") 
print(raw_request.model_dump_json(indent=4))

# Verbose Request Processing
# Enable comprehensive logging during request execution
verbose_request = fluid_api_request(
    "Generate an API request to get weather data for New York from OpenWeatherMap",
    verbose=True
)
print("\n=== Verbose Request ===")
print(verbose_request.model_dump_json(indent=4))

# Custom Documentation Integration
# Enhance request generation with specific API documentation
docs = """
API Endpoint: https://api.example.com/v1/users
Methods: GET, POST
Authentication: Bearer token required
"""
custom_doc_request = fluid_api_request(
    "Generate a request to get all users",
    documentation=docs,
    verbose=True
)
print("\n=== Request with Documentation ===")
print(custom_doc_request.model_dump_json(indent=4))

# Batch Processing
# Execute multiple API requests sequentially
print("\n=== Batch Request ===")
batch_results = batch_fluid_api_request(
    tasks=[
        "Generate an API request to get a random dog fact from https://dogapi.dog/api/v2/facts",
        "Generate an API request to get a random quote from https://api.quotable.io/random",
        "Generate an API request to get Bitcoin price from CoinGecko public API"
    ],
    verbose=True
)
for i, result in enumerate(batch_results, 1):
    print(f"\nBatch Result {i}:")
    print(result.model_dump_json(indent=4))

```

### Execution Flow

FluidAPI executes the following workflow:
1. **Request Interpretation**: Analyzes and processes natural language input
2. **API Generation**: Constructs appropriate API calls based on requirements
3. **Response Handling**: Processes and returns API responses

---

### Additional Examples

Refer to the [example.py](example.py) file for comprehensive usage examples.

---

## Configuration

### Environment Variables

FluidAPI utilizes environment variables for secure credential management:

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered request processing

Configure these variables in your `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key
WORKSPACE_DIR="agent_workspace"
```

---

## Enterprise Features

### Retry Mechanisms

FluidAPI incorporates intelligent retry logic to handle transient failures automatically. Retry configurations can be customized directly within the agent settings.

### Performance Optimization

Frequent requests are optimized through intelligent caching mechanisms to enhance performance and reduce API latency.

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

---

## Architecture

FluidAPI leverages the **Swarms Framework** to provide:

1. **Natural Language Parsing**: Advanced NLP capabilities for request interpretation
2. **Dynamic Request Construction**: Intelligent API request generation
3. **Intelligent Response Processing**: Automated response handling and error management

For comprehensive information about the Swarms Framework, visit [here](https://github.com/kyegomez/swarms).

---

## Development Roadmap

- [ ] Comprehensive API documentation
- [ ] Unit and integration test suite
- [ ] Extended usage examples
- [ ] Performance benchmarking tools

---

## Contributing

We welcome contributions from the community. To contribute:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed descriptions

---

## License

FluidAPI is licensed under the MIT License. See the [LICENSE](https://github.com/The-Swarm-Corporation/fluidapi/blob/main/LICENSE) file for complete terms and conditions.

---

## Contact Information

- **Lead Developer**: [Kye Gomez](https://github.com/kyegomez)
- **Repository**: [The-Swarm-Corporation/FluidAPI](https://github.com/The-Swarm-Corporation/fluidapi)
- **Package Distribution**: [fluid-api](https://pypi.org/project/fluid-api/)

---

**Transform your API integration experience. With FluidAPI, complex API workflows become simple, natural language commands.**
