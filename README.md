# Introduction
The Thumbnail / File Preview API creates high-resolution thumbnail images from any file you upload to it. 

# Installation
We recommend that you use the provided Dockerfile, as the package requires Libreoffice, Unosever etc. Install Docker before and familiarize yourself with it.
```
 docker-compose build --no-cache
 docker-compose up
```

# Authentication
For authenticating with the API, users must provide a simple API Key. This key can be included in:
Headers: X-API-Key
POST request body (as JSON): key
GET parameters: key
Please ensure that the provided API Key is present in the config.py file for the request to be authenticated, for example
´´´
PRIVATE_API_KEYS = {
    'username1': 'your-api-key-1',
    'username2': 'your-api-key-2'
}
´´´
For example
``` http://127.0.0.1:5000/api/v1/preview?key=YOUR_KEY ```

# How to use

### GET /api/v1/preview/
Shows if the libreoffice and unoserver is running.
Should be the first call to start those. May takes over 20 seconds.

### POST /api/v1/preview/
Uploads a file and returns a JSON include the base64 file. Expecting file as Multipart form data.

### POST /api/v1/preview/upload
Uploads a file and returns a unique identifier for the uploaded file. Expecting file as Multipart form data.

### POST /api/v1/preview/convert
Converts a previously uploaded file to the desired format.

### GET /api/v1/preview/download/
Downloads the converted file based on its unique ID and desired format. Expecting a unique_id and file_type given.

# Misc
## Unoserver
Please have a look to Unoserver documentation https://github.com/unoconv/unoserver/ to lern more about the file conversion.

## Flask skeleton
We used the following Flask skeleton, explaination and Medium link : https://beranger.medium.com/deploy-a-python-flask-server-using-google-cloud-run-d47f728cc864

## Deploy : 
We deploy the application on Google Cloud. Feel free to do the same:
```
gcloud run deploy flask-file-preview --region=europe-west2 --source=$(pwd) --allow-unauthenticated --project=[YOUR_GC_PROJECT_ID]
```