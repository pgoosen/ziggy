# Game Engine Daily cloud function
This function processes daily tasks for the game.

The function is triggered by an cron job (Cloud Scheduler) that publishes a message to a Pub/Sub topic. The function then processes the tasks specified in the message. These tasks include increase the avatar health daily, activating or deactivating goals, processing completed goals, and retrieving transactions from PrimeSaver accounts using the Investec OpenAPI.

## Deploy cloud function


### Add cloud scheduler cron job
A cloud scheduler is required to trigger the cloud function daily. In order to do this, follow the instructions [here](https://cloud.google.com/scheduler/docs/creating).

* The name for the job: SCHEDULER_JOB_NAME
* The schedule: `0 6 * * * `
* The target: `Pub/Sub`
* Topic: MY_SCHEDULER_TOPIC


### Setup before deploying
1. Create a PubSub topic for avatar update notifications (AVATAR_TOPIC) if one hasn't been created yet. This topic is used in the `.env.yaml` file created in step 2.
2. Create a `.env.yaml` file similar to `.env.yaml.sample` and add your project id and the pub sub topic id for avatar updates.
3. Copy the game_engine wheel from `../game_engine/dist` to `./dist`
4. Update the game_engine version in `requirements.txt` and `Pipfile`
5. [Setup Google Cloud SDK](https://cloud.google.com/sdk/docs/install) if you haven't done so already.


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
gcloud functions deploy game_engine_daily --entry-point=ProcessDailyTasks --runtime=python38 --trigger-topic MY_SCHEDULER_TOPIC --region=YOUR_PROJECT_REGION --memory=128MB --timeout=60s --env-vars-file .env.yaml
  ```
Remember to specify your project id and region in the above command.


[:arrow_left: Go back to Setup list](/README.md#setup)