import time
import json
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

credential = json.load(open('credential.json'))
KEY = credential['API_Key']
endpoint = credential['ENDPOINT']

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(KEY))


def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)
    print("API Response:", rawHttpResponse)

    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]
    print("Operation ID:", operationId)

    # SDK call
    result = client.get_read_result(operationId)
    print("Initial result status:", result.status)

    # Try API
    retry = 0
    while retry < maxRetries:
        if result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)
        print(f"Retry {retry + 1}: Status {result.status}")

        retry += 1

    if retry == maxRetries:
        print("Max retries reached, final status:", result.status)
        return "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
        print("Result text:", res_text)
        return res_text
    else:
        print("Final status:", result.status)
        return "error"
