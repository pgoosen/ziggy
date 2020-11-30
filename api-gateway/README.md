# API Gateway

## Setup

#### Important considerations
- [This Quickstart](https://cloud.google.com/api-gateway/docs/quickstart) will be used to setup an API Gateway. Alternatively, the [Google Cloud Console](https://cloud.google.com/api-gateway/docs/quickstart-console) can also be used.
- Choose the API Gateway location in an area close to the Firestore database. (Recommended: us-central1)

#### Instructions
1. Follow [these instructions](https://cloud.google.com/api-gateway/docs/quickstart#creating-an-api) to create an **API**.
2. Follow [these instructions](https://cloud.google.com/api-gateway/docs/quickstart#creating_an_api_config) to create an **API config**.
    - A working example of the config is available in `/api-gateway/openapi2-functions.yaml`.
    - In this example the `API_ID` = `ziggy-api` and the `optional-string` = `gateway`.
    - Replace the addresses of the two paths with the corresponding Cloud Function and Cloud Run URLs
3. Follow [these instructions](https://cloud.google.com/api-gateway/docs/quickstart#creating_a_gateway) to create a **gateway**.
4. Follow [these instructions](https://cloud.google.com/api-gateway/docs/quickstart#securing_access_by_using_an_api_key) to secure access to the gateway by using an API key.
    - This API key should be used in the After-Transaction Card Code as well as the Slack App.


[:arrow_left: Go back to Setup list](/README.md#setup)