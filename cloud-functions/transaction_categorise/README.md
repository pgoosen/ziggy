# TransactionCategorise cloud function
This function attempts to categorise new transactions in the transactions collection in the database. 

The function is triggered by a create event on the transactions collection. The new document is processed and a budget category is added to the transaction if possible. The budget categories are defined in `./merhcnat/merchant.py`. Categories can be updated or changed as desired by adding new categories to `lookups.py` in the game_engine and updating the merchant information in `./merhcnat/merchant.py`. 

Example of a merchant with a predefined category:
```json
"7996": {
    "name": "Amusement Parks/Carnivals",
    "category": "254b5b60-7483-4833-8132-c12d3705fb54"
}
```

## Deploy cloud function

### Setup before deploying
1. Create a PubSub topic for new transactions notifications.
2. Create a `.env.yaml` file similar to `.env.yaml.sample` and add your project id and the pub sub topic id for new transactions.
3. Make sure the `requirements.txt` is up to date.
4. [Setup Google Cloud SDK](https://cloud.google.com/sdk/docs/install) if you haven't done so already.

### Deployment using `gcloud` ([Google cloud SDK](https://cloud.google.com/sdk/docs/install))
Make sure correct project is selected if not specified in `deploy` command:

1. Check your project:
  ```
  gcloud config get-value project
  ```

2. Set the project:
  ```
  gcloud config set project <PROJECT_ID>
  ```

3. Deploy function:
  ```
  gcloud functions deploy transaction_categorise --entry-point=CategoriseTransaction --runtime=python38 --trigger-event 'providers/cloud.firestore/eventTypes/document.create' --trigger-resource 'projects/YOUR_PROJECT_ID/databases/(default)/documents/transactions/{docId}' --region=YOUR_PROJECT_REGION --memory=128MB --timeout=60s --env-vars-file .env.yaml
  ```
Remember to specify your project id and region in the above command.






[:arrow_left: Go back to Setup list](/README.md#setup)
