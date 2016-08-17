# A simple server for uploading and serving files/images

## How to use

* Make a GET on '/upload' - it will return a JSON `{upload_url: 'https://....'} with the upload URL you can use
* Make a POST to the URL from previous request with following data:
    * author - String
    * itemkey - String
    * file - File
* If successful it will return `{success: true}`

* In order to get an uploaded file do a GET request to `https://yourdomain/view/{itemkey}` where `{itemkey}` is the attribute you passed on POST
* Also you can check if a file with a given key is available by making a GET request to `https://yourdomain/has/{itemkey}`. It will return a JSON `{available: true, hash: 'hash string'} or `{available: false}`

## N.B.

This server uses blobstore, while Google currently recomends using new Cloud Storage. You can use [GoogleCloudPlatform/appengine-gcs-client](https://github.com/GoogleCloudPlatform/appengine-gcs-client) for that.

If you want to serve images a better way to do that is to use Images API and its [get_serving_url](https://cloud.google.com/appengine/docs/python/images/#using_if_lang_is_java_getservingurl_endif_if_lang_is_python_get_serving_url_endif) method. It is very fast, and allows images scaling and croping on the fly.
