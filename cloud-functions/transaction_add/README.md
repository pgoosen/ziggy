# Transaction Add -  Google Cloud Function
This functions ingests transaction data from Investec after-transaction event and adds it to the database.


## Environmental variables:
- Create a `.env.yaml` file based of `.env.yaml.sample`.
- The enviromental variables in the `.env.yaml` file include, `VALID_USERNAME` and `VALID_PASSWORD`.
- The `VALID_USERNAME` and `VALID_PASSWORD` are also used in the Card code for request verification.

## Deployment using `gcloud`
- Make sure correct project is selected if not specified in `deploy` command:

  Check:
  ```
  gcloud config get-value project
  ```

  Set:
  ```
  gcloud config set project <PROJECT_ID>
  ```

- Deploy function:
  ```
  gcloud functions deploy transaction_add --entry-point=AddTransaction --runtime=python38 --trigger-http --region=us-east1 --memory=128MB --timeout=60s --env-vars-file .env.yaml
  ```