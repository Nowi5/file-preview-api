import requests
import logging
from flask import g

def generic_api_requests(method, url, payload={}, params={}):
    logging.info("CURRENT REQUEST : ", method, url, payload)

    try:
        response = requests.request(
            method,
            url,
            json=payload,
            params=params,
        )

        json_response = response.json()

        logging.info("RESPONSE SUCCESS")

        return 1, json_response

    except Exception as e:
        logging.error("RESPONSE ERROR :", e)
        return 0, e
