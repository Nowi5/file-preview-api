import subprocess
import time
import logging
import socket
import config
from flask import g

def is_unoserver_running(interface="localhost", port="2002"):
    """Check if the server is already running by trying to establish a socket connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((interface, int(port)))
            return True
        except (ConnectionRefusedError, socket.timeout):
            return False

def check_server_started(interface="localhost", port="2002", timeout=30):
    """Check if the server has started by trying to establish a socket connection."""
    logging.info("Waiting for Unoserver to start...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((interface, int(port)))
                logging.info("Successfully connected to unoserver.")
                return True
            except ConnectionRefusedError:
                time.sleep(1)
    logging.error(f"Timed out waiting for unoserver to start after {timeout} seconds.")
    return False
    
def convert_document(input_file, output_file, convert_to=None, filter_name=None, interface="localhost", port="2002"):
    
    logging.info(f"Converting document {str(input_file)} ...")

    command = [config.PYTHON_PATH, "-m", "unoserver.converter"]
    if convert_to:
        command.extend(["--convert-to", convert_to])
    if filter_name:
        command.extend(["--filter", filter_name])
    command.extend(["--interface", interface])
    command.extend(["--port", port])
    command.extend([input_file, output_file])

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"Failed to convert document. Error: {stderr.decode('utf-8')}")
            return False
        else:
            logging.info(f"Document {input_file} converted successfully to {output_file}.")
            return True

    except Exception as e:
        logging.error(f"Exception occurred while converting document: {str(e)}")
        return False

def start_unoserver(interface="localhost", port=2002, executable_path=None):
    
    if is_unoserver_running(interface=interface, port=port):
        logging.info("Unoserver is already running.")
        return True
    
    # Construct the command to start the unoserver using the specified Python interpreter.
    cmd = [config.PYTHON_PATH, "-m", "unoserver.server", "--interface", interface, "--port", str(port)]

    if executable_path:
        cmd.extend(["--executable", executable_path])
    
    try:
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        # Optionally, wait for a few seconds to allow the server to start. 
        # This step can be adjusted or removed based on your needs.
        time.sleep(5) 

        # Optionally, check the first few lines of output (useful for debugging).
        output, _ = process.communicate(timeout=10)  # This line captures output for the given timeout.
        if "some expected output" in output.decode('utf-8'):
            logging.info("Started unoserver successfully.")
            return True
        else:
            logging.warning("Unexpected output from unoserver. You might want to check this.")
            return False

    except Exception as e:        
        logging.error(f"Failed to start unoserver. Error: {str(e)}")
        raise Exception(f"Failed to start unoserver. Error: {str(e)}")