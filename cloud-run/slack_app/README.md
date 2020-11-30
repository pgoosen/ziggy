# Slack 

## Setup
https://api.slack.com/apps/
1. Create new app
2. Interactivity & Shortcuts 
    - ON
    - Request URL
    - Shortcuts > Global (list_goals + create_goal + ...)
3. OAuth & Permissions
    - Install app to workspace
4. Create Slack channel
    - Add app to channel
5. Add app to channel 
6. Permissions
    - chat:write
    - incoming-webhook

## Build modals
https://app.slack.com/block-kit-builder/
https://api.slack.com/reference/block-kit/block-elements#input

## API
https://api.slack.com/reference/interaction-payloads/views#view_submission_fields
https://api.slack.com/methods/views.open/code

## Python SDK
https://slack.dev/python-slack-sdk/web/index.html#messaging

# Dev environment

## Packages
pip install -r requirements.txt

## Functions framework
...

# Deployment

## Cloud Run Service + FunctionsFramework (replaced Cloud Function due to cold-start issue)
gcloud builds submit --tag gcr.io/[GCP_PROJECT_ID]/ziggy --project [GCP_PROJECT_ID]

gcloud run deploy ziggy --image gcr.io/[GCP_PROJECT_ID]/ziggy --region us-central1 --project [GCP_PROJECT_ID] --platform managed --max-instances 1 --concurrency 4 --set-env-vars "PYTHONUNBUFFERED=TRUE,SLACK_BOT_TOKEN=xoxb-[SLACK_BOT_TOKEN],SLACK_VERIFICATION_TOKEN=[SLACK_VERIFICATION_TOKEN],SLACK_SIGNING_SECRET=[SLACK_SIGNING_SECRET],SLACK_CHANNEL_ID=[SLACK_CHANNEL_ID],BUCKET_PATH=[BUCKET_URL]/Level{REPLACE_LEVEL}.png"

## PubSub general
echo "create service account"
gcloud iam service-accounts create runinvoker \
    --display-name "Cloud Run Pub/Sub Invoker"

echo "create iam binding"
gcloud projects add-iam-policy-binding [GCP_PROJECT_ID] \
    --member=serviceAccount:service-[GCP_PROJECT_NUMBER]@gcp-sa-pubsub.iam.gserviceaccount.com \
    --role=roles/iam.serviceAccountTokenCreator

echo "iam roles"
gcloud beta run services add-iam-policy-binding ziggy \
    --member=serviceAccount:runinvoker@[GCP_PROJECT_ID].iam.gserviceaccount.com \
    --role=roles/run.invoker

## PubSub - Transactions
echo "create topic"
gcloud pubsub topics create new-transactions

echo "create subscription"
gcloud beta pubsub subscriptions create gcr-ziggy_new-transactions \
    --topic new-transactions \
    --push-endpoint=[SERVICE_URL]/?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2F[GCP_PROJECT_ID]%2Ftopics%2Fnew-transactions \
    --push-auth-service-account=runinvoker@[GCP_PROJECT_ID].iam.gserviceaccount.com

## PubSub - Avatar update
echo "create topic"
gcloud pubsub topics create avatar-change

echo "create subscription"
gcloud beta pubsub subscriptions create gcr-ziggy_avatar-change \
    --topic avatar-change \
    --push-endpoint=[SERVICE_URL]/?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2F[GCP_PROJECT_ID]%2Ftopics%2Favatar-change \
    --push-auth-service-account=runinvoker@[GCP_PROJECT_ID].iam.gserviceaccount.com