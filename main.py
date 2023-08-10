import os
from flask import Flask, jsonify, Response, g, request
import config
import json
import time
import uuid
import threading
import requests as req
import logging
from utils.logging_setup import configure_logger
from blueprints.preview import preview


def create_app():
  app = Flask(__name__)
  configure_logger(app)

  app.register_blueprint(preview, url_prefix="/api/v1/preview")

  # Error 404 handler
  @app.errorhandler(404)
  def resource_not_found(e):
    return jsonify(error=str(e)), 404
  # Error 405 handler
  @app.errorhandler(405)
  def resource_not_found(e):
    return jsonify(error=str(e)), 405
  # Error 401 handler
  @app.errorhandler(401)
  def custom_401(error):
    return Response("API Key required.", 401)
  
  @app.route("/version", methods=["GET"], strict_slashes=False)
  def version():
    response_body = {
        "success": 1,
    }
    return jsonify(response_body)
  
  @app.route("/ping")
  def hello_world():
     return "pong"
  
  @app.before_request
  def before_request_func():
    execution_id = uuid.uuid4()
    g.start_time = time.time()
    g.execution_id = execution_id

    logging.info("ROUTE CALLED %s", request.url)

  @app.before_request
  def ensure_api_key():
    # Retrieve API key from headers
    api_key = request.headers.get('X-API-Key')

    # If not in headers, check in POST data
    if not api_key and request.method == "POST":
        data = request.get_json(silent=True)
        if data and 'key' in data:
            api_key = data['key']

    # If not in POST data, check in GET parameters
    if not api_key:
        api_key = request.args.get('key')

    # Identify the user based on the API key
    api_keys = config.PRIVATE_API_KEYS
    user = next((username for username, key in api_keys.items() if key == api_key), None)

    if not user:
        return jsonify(error="API Key required or invalid."), 401

    # Store the user in Flask's g object
    g.user = user

    logging.info("USER VERIFIED %s", user)

  @app.after_request
  def after_request(response):
    if response and response.get_json():
        data = response.get_json()

        data["time_request"] = int(time.time())
        data["version"] = config.VERSION

        # Add the user to the response        
        # Check if 'user' attribute exists in Flask's g object
        if hasattr(g, 'user'):
            data["user"] = g.user
        else:
            data["user"] = "Anonymous"  # or whatever default you want to provide

        response.set_data(json.dumps(data))
    return response
  
  def send_callback(execution_id, callback_url, data):
    try:
        req.post(callback_url, json=data)
    except Exception as e:
        logging.error("Failed to send callback to %s. Error: %s", callback_url, e)

  @app.after_request
  def initiate_callback(response):
    # Fetch the callback URL
    callback_url = request.headers.get('X-Callback-URL')
    if not callback_url:
        callback_url = request.args.get('callback')
    if not callback_url and request.method == "POST":
        data = request.get_json(silent=True)
        if data and 'callback' in data:
            callback_url = data['callback']

    if callback_url:
    # Extract response data
      if response.is_json:
          result_data = response.get_json()
          # Initiate the callback thread
          threading.Thread(target=send_callback, args=(g.execution_id, callback_url, result_data)).start()
      else:
          # If it's not JSON, handle as needed, maybe send a default message or the plain content
          threading.Thread(target=send_callback, args=(g.execution_id, callback_url, response.data.decode())).start()

    return response
  
  @app.after_request
  def after_request_func(response):
    logging.info("CLOSED %s", request.url)
    return response

  return app
  
app = create_app()

if __name__ == "__main__":
  #    app = create_app()
  logging.info("Starting app...")
  app.run(host="0.0.0.0", port=5000)