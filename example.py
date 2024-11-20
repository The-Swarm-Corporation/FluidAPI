from fluid_api.main import fluid_api_request, batch_fluid_api_request

print(fluid_api_request("Generate an API request to get a random cat fact from https://catfact.ninja/fact"))

print(batch_fluid_api_request([
    "Generate an API request to get a random cat fact from https://catfact.ninja/fact",
    "Generate an API request to get a random dog fact from https://dogapi.dog/api/v2/facts", 
    "Generate an API request to get a random joke from https://official-joke-api.appspot.com/random_joke"
]))
