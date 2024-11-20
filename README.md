# FluidAPI: Natural Language API Requests

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

Welcome to **FluidAPI**, a revolutionary framework that allows you to interact with APIs using **natural language**. No more JSON, headers, or complex formats—simply describe your request in plain English, and FluidAPI will do the rest.

Powered by the **Swarms Framework** and created by [Kye Gomez](https://github.com/kyegomez), FluidAPI redefines how developers interact with APIs.

---

## 🌟 Features

- **Natural Language API Requests**: Just describe your task, and FluidAPI generates and executes the request for you.
- **Powered by AI Agents**: Built on the robust [Swarms Framework](https://github.com/kyegomez/swarms), enabling dynamic and intelligent API handling.
- **Effortless Integration**: Replace complex API workflows with simple, human-friendly commands.
- **Retry and Reliability**: Automatic retries and error handling for seamless performance.
- **Dynamic Authentication**: Handles token management and injects them automatically.

---

## 🚀 Installation

Install the `fluid-api` package via pip:

```bash
pip install fluid-api
```

---

## 🔧 Getting Started

### 1. Import and Initialize FluidAPI
```python
from fluid_api.main import fluid_api_request, batch_fluid_api_request
```

### 2. Make a Natural Language Request
Simply describe your request in natural language:

```python
from fluid_api.main import fluid_api_request, batch_fluid_api_request

print(fluid_api_request("Generate an API request to get a random cat fact from https://catfact.ninja/fact"))

print(batch_fluid_api_request([
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact",
    "Generate an API request to get a random dog fact from https://dogapi.dog/api/v2/facts", 
    "Generate an API request to get a random joke from https://official-joke-api.appspot.com/random_joke"
]))

```

FluidAPI will:
1. Interpret your request.
2. Generate and execute the appropriate API call.
3. Return the API's response.

---

## ✨ Examples

### Fetch Data
```python
response = api_agent.run("Get a list of cat facts from https://catfact.ninja/fact")
print(response)
```

### Post Data
```python
response = api_agent.run("Send a POST request to https://api.example.com/users with name='John Doe' and email='john.doe@example.com'")
print(response)
```

### Authentication
FluidAPI automatically handles token management. For APIs requiring authentication, simply include it in your description:
```python
response = api_agent.run("Retrieve my GitHub repositories from https://api.github.com/user/repos using my GitHub token")
print(response)
```

---

## ⚙️ Configuration

### Environment Variables
FluidAPI uses environment variables for sensitive data:
- `OPENAI_API_KEY`: Your OpenAI API key.

Set these variables in your `.env` file:
```env
OPENAI_API_KEY=your-openai-api-key
WORKSPACE_DIR="agent_workspace"

```

---

## 📦 Advanced Features

### Retry Logic
FluidAPI includes built-in retry logic to handle transient failures automatically. You can configure retry settings directly in the agent.

### Caching
Frequent requests are optimized with caching to improve performance.

---

## 🛠 Development

### Clone the Repository
```bash
git clone https://github.com/The-Swarm-Corporation/fluidapi.git
cd fluidapi
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💡 How It Works

FluidAPI leverages the **Swarms Framework** to:
1. Parse natural language instructions.
2. Dynamically construct API requests.
3. Execute requests and handle responses intelligently.

Learn more about the Swarms Framework [here](https://github.com/kyegomez/swarms).

---

# Todo
- [ ] Add documentation
- [ ] Add tests
- [ ] Add examples

----

## 🤝 Contributing

We welcome contributions! To get started:
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request.

---

## 📝 License

FluidAPI is licensed under the MIT License. See the [LICENSE](https://github.com/The-Swarm-Corporation/fluidapi/blob/main/LICENSE) file for details.

---

## 🌍 Connect with Us

- **Author**: [Kye Gomez](https://github.com/kyegomez)
- **Project**: [The-Swarm-Corporation/FluidAPI](https://github.com/The-Swarm-Corporation/fluidapi)
- **Pip Package**: [fluid-api](https://pypi.org/project/fluid-api/)

---

**Transform the way you interact with APIs. With FluidAPI, it's as simple as saying what you want.**
