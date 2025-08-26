from fluid_api_agent.main import batch_fluid_api_request

print("\n=== Batch Request ===")
batch_results = batch_fluid_api_request(
    tasks=[
        "Generate an API request to get Bitcoin (BTC) price from CoinGecko public API",
        "Generate an API request to get Solana (SOL) price from CoinGecko public API",
        "Generate an API request to get Ethereum (ETH) price from CoinGecko public API",
    ],
    verbose=True,
)
for i, result in enumerate(batch_results, 1):
    print(f"\nBatch Result {i}:")
    print(result.model_dump_json(indent=4))
