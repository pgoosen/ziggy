# Investec after-transaction code

This code (`main.js`) and environmental file (`env.json`) should be deployed to the Investec programmable card environment.

## Environmental variables:
- The enviromental variables in the `env.json` file include, `transactionApi`, `username` and `password`.
- The `username` and `password` are also used in the `transaction_add` Cloud Function for request verification.
- The `transactionApi` variable specifies the API Gateway path to the function and should include the API key used with the Gateway.
For example:
`"transactionApi": "https://[GATEWAY_URL]/transaction/add?key=[API_KEY_VALUE]"`
