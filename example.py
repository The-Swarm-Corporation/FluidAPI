from fluid_api_agent.main import (
    fluid_api_request,
    batch_fluid_api_request,
)

# All natural language requests are supported
print(
    fluid_api_request(
        "Generate an API request to get a random cat fact from https://catfact.ninja/fact"
    )
)

print(
    batch_fluid_api_request(
        [
            "Generate an api request to get a joke from reddit",
            "Generate an api request to an weather data provider to fetch the data for today in palo alto that doesn't need authentication",
            "Generate an api request to get a random dog fact from https://dogapi.dog/api/v2/facts",
            "Generate an API request to get a random joke from https://official-joke-api.appspot.com/random_joke",
        ]
    )
)
