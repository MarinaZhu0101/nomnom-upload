from flask import Flask, send_file, abort, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import io
import os
# from PIL import Image
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from PIL import Image
import google.generativeai as genai
import PIL

app = Flask(__name__)

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
CORS(app)

# Initialize the S3 client AKIA6ODU2WFB5LY5KCVI
# s3 = boto3.client('s3') cb5Qw7tDmgOC2txaN9yiVeDbRMwkjVHNsp9eex8w
s3 = boto3.client('s3', region_name='eu-west-1',
                  aws_access_key_id=os.getenv('aws_access_key_id'), 
                  aws_secret_access_key=os.getenv('aws_secret_access_key'))

@app.route('/fetch-image')
def fetch_image():
    bucket_name = request.args.get('bucket_name')
    image_key = request.args.get('image_key')

    if not bucket_name or not image_key:
        return abort(400, description="Bucket name and image key are required")

    try:
        # Fetch the image from the S3 bucket
        print("Getting object...")
        s3_response = s3.get_object(Bucket=bucket_name, Key=image_key)
        print("s3 blabliblub response success!")
        image_data = s3_response['Body'].read()
        
        # Create an in-memory bytes buffer to send the image
        image = Image.open(io.BytesIO(image_data))
        
        # Extract
        text, text_02, text_03 = extract_text(image, image_key)
        
        # Return multiple pieces of information as JSON
        response_data = {
            "extracted_text": text,
            "extracted_text_02": text_02,
            "extracted_text_03": text_03,

        }
        
        return jsonify(response_data)

        # return jsonify({'text': text})
        return text
    except NoCredentialsError:
        return abort(403, description="Credentials not available")
    except PartialCredentialsError:
        return abort(403, description="Incomplete credentials")
    except s3.exceptions.NoSuchKey:
        return abort(404, description="Image not found")
    except s3.exceptions.BucketNotFound:
        return abort(404, description="Bucket not found")
    except Exception as e:
        return abort(500, description=f"An error occurred: {str(e)}")

# def extract_information_from_image(directory):
    counter = 0

    for filename in os.listdir(directory):
        IMG_PATH = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(IMG_PATH):
            print(IMG_PATH)

            # IMG_PATH = "/Users/kieutrangnguyenvu/Downloads/ocr/images/pizza-menu.png"

            img = PIL.Image.open(IMG_PATH)

            # response = model.generate_content(["Extract the menu information and put it into a structured JSON table with following structure: { '_id': 'ObjectId', 'category': 'string', 'name': 'string', 'description': 'string', 'price': 'number'}. For 'category', insert either main dish, starters or dessert and if not given, just dish. ", img], stream=True)

            print(f"{counter + 1} out of {len(os.listdir(directory))}")
            response = model.generate_content(["Extract the text information and put it into a simple structured JSON table with following structure: " + ' "categories": [ {"name": "Starters", "dishes": [ { "name": "string", "description": "string", "price": "number", "note": "string" }, { "name": "string", "description": "string" (if legible), "price": "number", "note": "string" } ] }, { "name": "Main Dishes", "dishes": [ { "name": "string", "description": "string", "price": "number" }, { "name": "string", "description": "string", "price": "number" }]}]. The default for "note" is empty, if there is information about add-ons or similar things, then insert "Add-ons available." ' , img], stream=True)

            response.resolve()

            print(response.text)

            counter += 1

        else:
            break

def extract_text(source, filename):

    # IMG_PATH = "/Users/kieutrangnguyenvu/Downloads/ocr/images/pizza-menu.png"

    # img = PIL.Image.open(source)

    # response = model.generate_content(["Extract the menu information and put it into a structured JSON table with following structure: { '_id': 'ObjectId', 'category': 'string', 'name': 'string', 'description': 'string', 'price': 'number'}. For 'category', insert either main dish, starters or dessert and if not given, just dish. ", img], stream=True)

    # print(f"{counter + 1} out of {len(os.listdir(directory))}")

    format = '''{"restaurants": [{"name": "" (stays empty),"cuisine": "" (stays empty),"tags": [] (stays empty),"menu": {"categories": [{"name": "Starters" (or any other expressive category/heading),"dishes": [{"name": "string","description": "string" (if legible),"price": "number","note": "string" (for example vegan, vegetarian, gluten-free etc.)},{"name": "string","description": "string","price": "number","note": "string"}]},{"name": "Main Dishes","dishes": [{"name": "string","description": "string","price": "number","note": "string"},{"name": "string","description": "string","price": "number","note":
    "string"}]}]}}]}'''

    format_02 = '''{
    "restaurants": [
        {
            "name": "",
            "cuisine": "" ,
            "tags": [],
            "menu": {
                "categories": [
                    {
                        "name": "Starters" ,
                        "dishes": [
                            {
                                "name": "string",
                                "description": "string",
                                "price": "number",
                                "note": "string"
                            },
                            {
                                "name": "string",
                                "description": "string",
                                "price": "number",
                                "note": "string"
                            }
                        ]
                    },
                    {
                        "name": "Main Dishes",
                        "dishes": [
                            {
                                "name": "string",
                                "description": "string",
                                "price": "number",
                                "note": "string"
                            },
                            {
                                "name": "string",
                                "description": "string",
                                "price": "number",
                                "note": "string"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}'''

    # response = model.generate_content(["Extract the text information and put it into a simple structured JSON table with following structure: " + ' "categories": [ {"name": "Starters", "dishes": [ { "name": "string", "description": "string", "price": "number", "note": "string" }, { "name": "string", "description": "string" (if legible), "price": "number", "note": "string" } ] }, { "name": "Main Dishes", "dishes": [ { "name": "string", "description": "string", "price": "number" }, { "name": "string", "description": "string", "price": "number" }]}]. The default for "note" is empty, if there is information about add-ons or similar things, then insert "Add-ons available." ' , img], stream=True)

    first_response = model.generate_content(["Extract the text information and put it into a simple but valid structured JSON table with following structure: " + format_02 + '. Please include "categories" as an attribute. The default for "note" is empty. If there is information about things you can add extra to your dish or add-ons in general or toppings or similar things that do not have a price, ignore it. Ignore "build your own meal, dish, food" things. ' , source], stream=True)

    first_response.resolve()

    # second = model.generate_content('Check the following json structure. The last few brackets are missing, please make sure that it ends with }]}]} }]}: ' + first_response.text  + ' Return only the fixed json structure.')

    # print(response.text)

    # response = '"}'.join(first_response.text.split('"}')[:-1]) + '"}]}]} }]}'
    response = '"}'.join(first_response.text.split('"}')[:-1]) + '"}]}]}]}]}'

    response_02 = '"}'.join(first_response.text.split('"}')[:-1]) + '"}]}]} }]}' 

    response_03 = '"}'.join(first_response.text.split('"}')[:-1]) + '"}]}]}]}'

    # print(response)

    # response.resolve()

    # response = second_response.text[:-2] + "}" + second_response.text[-2:]

    return (response.strip("```json\n").strip("```"), response_02.strip("```json\n").strip("```"), response_03.strip("```json\n").strip("```"))

if __name__ == '__main__':
    app.run(debug=True)
