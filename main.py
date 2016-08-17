#!/usr/bin/env python

import os
import urllib
import jinja2
import webapp2
import logging

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'])

def parent_entity():
  return ndb.Key('Uploads', 'uploads')

class Upload(ndb.Model):
  itemkey = ndb.StringProperty(indexed=True)
  author = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)
  blob = ndb.BlobKeyProperty()

class MainPage(webapp2.RequestHandler):
  def get(self):

    # Load latest X items
    uploads_query = Upload.query(ancestor=parent_entity()).order(-Upload.date)
    uploads = uploads_query.fetch(50)

    template_values = {
      'uploads': uploads
    , 'upload_url': blobstore.create_upload_url('/upload')
    }

    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.write('{"upload_url": "' + upload_url + '"}')

  def post(self):
    # Init response
    mainPage = MainPage()

    # Uploaded file
    upload_files = self.get_uploads()

    if (len(upload_files)):
      blob_info = upload_files[0]

      # Init Upload object data
      upload = Upload(parent=parent_entity())

      # Populate Upload object with data
      upload.itemkey = self.request.get('itemkey')
      upload.author = self.request.get('author')
      upload.blob = blob_info.key()
      upload.put()

      # if success
      self.response.write('{"success": true}')
    else:
      # file upload error
      self.response.write('{"success": false}')

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))

    if resource == "None":
      self.response.write('No images for given key')
    else:
      blob_info = blobstore.BlobInfo.get(resource)
      self.send_blob(blob_info)

class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))

    if resource == "None":
      self.response.write('No key given')
    else:
      image_query = Upload.query(ancestor=parent_entity()).order(-Upload.date).filter(Upload.itemkey == resource)
      image = image_query.get()

      if image:
        # Set cache headers
        self.response.cache_control = 'public'
        self.response.cache_control.max_age = 3600 * 24 * 7 # one week
        self.send_blob(blobstore.BlobInfo.get(image.blob))
      else:
        self.response.write('No images for given key')

class HasHandler(webapp2.RequestHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))

    if resource == "None":
      self.response.write('{"available": false}')
    else:
      image_query = Upload.query(ancestor=parent_entity()).order(-Upload.date).filter(Upload.itemkey == resource)
      image = image_query.get()
      print image

      if image:
        # Return a part of blob key as image hash
        self.response.write('{"available": true, "hash": "' + str(image.blob)[0:10] + '"}')
      else:
        self.response.write('{"available": false}')

application = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/upload', UploadHandler),
  ('/download/([^/]+)?', DownloadHandler), # Used only for front view
  ('/view/([^/]+)?', ViewHandler),
  ('/has/([^/]+)?', HasHandler),
], debug=True)
