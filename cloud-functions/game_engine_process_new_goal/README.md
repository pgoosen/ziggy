# Game Engine Process New Goal cloud function
This function processes new goals that are added to the goals collection. When a user creates a new goal, the user is rewarded with XP points. 

## Deploy cloud function

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
  gcloud functions deploy game_engine_process_new_goal --entry-point=ProcessAddGoal --runtime=python38 --trigger-event 'providers/cloud.firestore/eventTypes/document.create' --trigger-resource 'projects/YOUR_PROJECT_ID/databases/(default)/documents/goals/{docId}' --region=YOUR_PROJECT_REGION --memory=128MB --timeout=60s --env-vars-file .env.yaml
  ```
Remember to specify your project id and region in the above command.
