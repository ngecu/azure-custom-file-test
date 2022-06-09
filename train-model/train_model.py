import os 
from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from flask import Flask, render_template, request
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename

from flask_cors import CORS,cross_origin


UPLOAD_FOLDER = '/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__,template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app,support_credentials=True)

	
@app.route('/upload', methods=['POST'])
def fileUpload():
    target=os.path.join(UPLOAD_FOLDER,'test_docs')
    if not os.path.isdir(target):
        os.mkdir(target)
    logger.info("welcome to upload`")
    file = request.files['file'] 
    filename = secure_filename('test1.jpg')
    destination="/".join([target, filename])
    file.save(destination)
    session['uploadFilePath']=destination
    response="Whatever you wish too return"
    return response

		
 

@app.route('/testModel',methods=['GET'])
def home():
    model_id = request.args.get('model_id')
    x = test_model(model_id)

    return {"results":x}

@app.route('/trainModel',methods=['GET'])
def my_profile():

    endPoint = request.args.get('endPoint')
    key = request.args.get('key')
    sasURI = request.args.get('sasURI')


    print("end Point is ",endPoint)
    print("end Point is ",key)
    print("end Point is ",sasURI)

    response_body = main()

    print("response is ",response_body)


    return response_body


def main(): 
        
    try: 
    
        # Get configuration settings 
        load_dotenv()
        form_endpoint = os.getenv('FORM_ENDPOINT')
        form_key = os.getenv('FORM_KEY')
        trainingDataUrl = os.getenv('STORAGE_URL')

        # Authenticate Form Training Client
        form_recognizer_client = FormRecognizerClient(form_endpoint, AzureKeyCredential(form_key))
        form_training_client = FormTrainingClient(form_endpoint, AzureKeyCredential(form_key))

        # Train model 
        poller = form_training_client.begin_training(trainingDataUrl, use_training_labels=False)
        model = poller.result()

        train_response = {
            "modelID":model.model_id,
            "status":model.status,

        }

        print("Model ID: {}".format(model.model_id))
        print("Status: {}".format(model.status))
        print("Training started on: {}".format(model.training_started_on))
        print("Training completed on: {}".format(model.training_completed_on))


        return train_response


    except Exception as ex:
        print(ex)


def test_model(model_id): 
        
    try: 
    
        # Get configuration settings 
        load_dotenv()
        form_endpoint = os.getenv('FORM_ENDPOINT')
        form_key = os.getenv('FORM_KEY')
        
        # Create client using endpoint and key
        form_recognizer_client = FormRecognizerClient(form_endpoint, AzureKeyCredential(form_key))
        form_training_client = FormTrainingClient(form_endpoint, AzureKeyCredential(form_key))

        # Model ID from when you trained your model.
        # model_id = os.getenv('MODEL_ID')

        # Test trained model with a new form 
        with open('test1.jpg', "rb") as f: 
            poller = form_recognizer_client.begin_recognize_custom_forms(
                model_id=model_id, form=f)

        result = poller.result()

        x = []

        for recognized_form in result:
            print("Form type: {}".format(recognized_form.form_type))
            for name, field in recognized_form.fields.items():
                print("Field '{}' has label '{}' with value '{}' and a confidence score of {}".format(
                    name,
                    field.label_data.text if field.label_data else name,
                    field.value,
                    field.confidence
                ))
                x.append("Field '{}' has label '{}' with value '{}' and a confidence score of {}".format(
                    name,
                    field.label_data.text if field.label_data else name,
                    field.value,
                    field.confidence
                ))

        return x
        
    except Exception as ex:
        print(ex)

# if __name__ == '__main__': 
#     main()