from fluid_api_agent.main import (
    fluid_api_request,
)

# Example: Fetch recent Stripe transactions
stripe_request = fluid_api_request(
    "Generate an API request to get the most recent transactions from the Stripe API endpoint https://api.stripe.com/v1/charges, limit to 10 transactions and sort by created date descending",
    documentation="""
    API Endpoint: https://api.stripe.com/v1/charges
    Authentication: Bearer token (Stripe secret key) required in header
    Method: GET
    Parameters:
        - limit: Number of transactions to return
        - created[lt]: Timestamp for transactions before this time
        - created[gt]: Timestamp for transactions after this time
    """,
    verbose=True,
)

print(stripe_request.model_dump_json(indent=4))
