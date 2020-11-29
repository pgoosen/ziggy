# Google Cloud Firestore

All data for the application is stored in Firestore.

## Setup

#### Important considerations
- Choose the database **location** in the same area where the Cloud Functions and Cloud Run instances will be created. (Recommended: us-east1)
- Create the Firestore instance in **native** mode.

#### Instructions
- Follow [these instructions](https://cloud.google.com/firestore/docs/quickstart-servers#create_a_in_native_mode_database) to create a Firestore instance in your GCP project.
