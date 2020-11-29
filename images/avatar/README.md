# Google Storage bucket for Avatar images

#### Considerations

- `[PROJECT_ID]` - Your Google Cloud project ID.
- `[BUCKET_NAME]` - The name of your storage bucket
  - The name is also used in the Slack App environmental variables.
- `[OBJECTS_LOCATION]` - The location where the five avatar images are stored.
  - The images are available in the repo: `/images/avatar/`.

#### Instructions

- Create bucket
```
gsutil mb -p [PROJECT_ID] -c STANDARD -l us-east1 -b on gs://[BUCKET_NAME]
```

- Make bucket public
```
gsutil iam ch allUsers:objectViewer gs://[BUCKET_NAME]
```

- Upload images to bucket
```
gsutil cp -r [OBJECTS_LOCATION] gs://[BUCKET_NAME]/
```