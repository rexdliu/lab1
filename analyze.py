import time
import json
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

credential = json.load(open('credential.json'))
KEY = credential['API_Key']
endpoint = credential['ENDPOINT']
try:
    with open('credential.json', 'r') as f:
        credential = json.load(f)
        KEY = credential['API_Key']
        endpoint = credential['ENDPOINT']
except Exception as e:
    print(f"Error loading credentials: {e}")
    exit(1)

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(KEY))


def read_image(uri):
    try:
        # Call API with URL
        read_response = client.read(url=uri, language="en", raw=True)
        # Get the operation location (URL with an ID at the end)
        read_operation_location = read_response.headers["Operation-Location"]
        # Take the ID off and use to get results
        operation_id = read_operation_location.split("/")[-1]
    except Exception as e:
        print(f"Error initiating read operation: {e}")
        return "error"

    # Wait for the operation to complete
    while True:
        read_result = client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Extract text if operation succeeded
    if read_result.status == OperationStatusCodes.succeeded:
        res_text = ""
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                res_text += line.text + " "
        print("Result text:", res_text.strip())
        return res_text.strip()
    else:
        print("Operation failed with status:", read_result.status)
        return "error"



def test_ocr_api():
    # Sample image URL to test the OCR API functionality
    sample_image_url = "https://jeroen.github.io/images/testocr.png"

    # Calling the OCR API
    try:
        ocr_result = client.recognize_printed_text_in_stream(sample_image_url)
        print("OCR API call successful. Result:")
        print(ocr_result)
        return ocr_result
    except Exception as e:
        print("Error calling OCR API:", e)
        return None
    #run the analyze independently to test whether I am wrong. Because I don't know which step I am wrong in app.py
if __name__ == "__main__":
    test_image_url = "https://jeroen.github.io/images/testocr.png"
    result = read_image(test_image_url)
    print(f"OCR Result: {result}")
