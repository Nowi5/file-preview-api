import os
import uuid
import shutil
import config
from flask import Blueprint, jsonify, request, g, send_from_directory
from urllib.parse import urljoin, urlparse
import logging
import requests as req
import re
import base64
from utils.uno_utils import start_unoserver, check_server_started, convert_document

preview = Blueprint(name="preview", import_name=__name__)

@preview.route("/", methods=["GET"])
def review_status():
    try:
        handle_start_unoserver()
        return jsonify({
            "success": 1
        })
    except Exception as error:
        return jsonify({"success": 0, "message": f"Error: {error}"}), 400

@preview.route("/", methods=["POST"])
def generate_preview():
    try:
        handle_start_unoserver()
        # Upload
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"success": 0, "message": "No valid file provided!"}), 400
        if not allowed_file(file.filename):
            return jsonify({"success": 0, "message": "File type not allowed!"}), 400

        unique_id, _ = save_uploaded_file(file)

        # Convert
        convert_to = request.form.get('convert_to')
        if not convert_to:
            convert_to = 'png'

        input_file, output_file_path = handle_conversion(unique_id, convert_to)

        # Convert file to base64 and return in JSON response
        with open(output_file_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            "success": 1,
            "data": {
                "unique_id": unique_id,
                "convert_to": convert_to,
                "input_filename": input_file,
                "file_base64": encoded_string,
                "message": "File converted successfully!"
            }
        })
    except Exception as error:
        return jsonify({"success": 0, "message": f"Error: {error}"}), 400

@preview.route("/upload", methods=["POST"])
def upload_file_endpoint():
    try:
        # Handle file upload and saving
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"success": 0, "message": "No valid file provided!"}), 400
        if not allowed_file(file.filename):
            return jsonify({"success": 0, "message": "File type not allowed!"}), 400

        unique_id, _ = save_uploaded_file(file)

        return jsonify({
            "success": 1,
            "data": {
                "unique_id": unique_id
            }
        })
    except Exception as error:
        return jsonify({"success": 0, "message": f"Error: {error}"}), 400


@preview.route("/convert", methods=["POST"])
def convert_uploaded_file():
    
    try:
        # Start the server
        handle_start_unoserver()

        content_type = request.headers.get("Content-Type")
        # Handle JSON data
        if "application/json" in content_type:
            data = request.get_json()
            unique_id = data.get('unique_id')
            convert_to = data.get('convert_to')        
        # Handle FormData
        elif "multipart/form-data" in content_type:
            unique_id = request.form.get('unique_id')
            convert_to = request.form.get('convert_to')       
        else:
            return jsonify({"success": 0, "message": "Unsupported Content-Type"}), 400

        input_file, output_file_path = handle_conversion(unique_id, convert_to)

        return jsonify({
            "success": 1,
            "data": {
                "unique_id": unique_id,
                "convert_to": convert_to,
                "input_filename": input_file,
                "message": "File converted successfully!"
            }
        })

    except Exception as error:
        return jsonify({"success": 0, "message": f"Error: {error}"}), 400


@preview.route("/download", methods=["GET"])
def download_file():
    try:
        unique_id = request.args.get('unique_id')
        file_type = request.args.get('file_type')
        
        # Check if the necessary parameters are provided
        if not unique_id:
            return jsonify({"success": 0, "message": "Missing required parameter 'unique_id'!"}), 400
        
        if not file_type:
            file_type = 'png'

        folder_path = os.path.join("data", unique_id, "output")  # Add the "output" folder to the path

        if not os.path.exists(folder_path):
            return jsonify({"success": 0, "message": "Invalid unique ID!"}), 400

        file_path = os.path.join(folder_path, f"output.{file_type}")

        if not os.path.exists(file_path):
            return jsonify({"success": 0, "message": "File not found!"}), 400

        return send_from_directory(folder_path, f"output.{file_type}", as_attachment=True)

    except Exception as error:
        return jsonify({"success": 0, "message": f"Error: {error}"}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save the uploaded file and return its unique ID and path."""
    unique_id = str(uuid.uuid4())
    folder_path = os.path.join("data", unique_id)
    
    # Create an input subdirectory inside the unique_id folder
    input_folder_path = os.path.join(folder_path, "input")
    os.makedirs(input_folder_path, exist_ok=True)

    file_path = os.path.join(input_folder_path, file.filename)
    file.save(file_path)

    return unique_id, file_path


def handle_conversion(unique_id, convert_to):
    """Convert the file and return the output file path."""
    folder_path = os.path.join("data", unique_id)
    
    input_folder_path = os.path.join(folder_path, "input")
    # Check and grab the first file from the input folder
    input_file = os.listdir(input_folder_path)[0]
    input_file_path = os.path.join(input_folder_path, input_file)

    if not os.path.exists(input_folder_path) or not os.listdir(input_folder_path):
        logging.error("Input folder does not exist or is empty: %s", input_folder_path)
        raise Exception(f"Input folder does not exist or is empty: {input_folder_path}")

    # Add the creation of the output directory here.
    output_directory = os.path.join(folder_path, "output")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Adjust the output_file_path to consider the new output directory.
    output_file_path = os.path.join(output_directory, f"output.{convert_to}")

    if not os.path.exists(folder_path):
        logging.error("Folder does not exists: %s", folder_path)
        raise Exception(f"Folder does not exists: {folder_path}")
    
    convert_document(input_file_path, output_file_path, convert_to=convert_to)

    return input_file, output_file_path

def handle_start_unoserver():
    try:
        start_unoserver()
    except Exception as e:
        error_message = str(e)
        if "timed out after 10 seconds" in error_message:
            raise Exception("Server initialization ongoing. Please try again later.") from None
        else:
            raise Exception(f"An unexpected error occurred: {error_message}") from None
