import base64
import json
import time

from flask import Flask, request
from flask_cors import CORS
import os
from api_functions import process_file, get_data
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='/')
CORS(app)

@app.route('/check', methods=['POST', 'GET'])
def check():
    return 'hello'


@app.route('/api/getfile', methods=['POST', 'GET'])
def getfile1():
    # try:
    name = request.form.get('name')
    bytes = request.form.get('bytes')

    file = request.files['file']
    filename = secure_filename(file.filename)

    user_id = str(request.remote_addr)
    if user_id != 'error':
        if os.path.isdir(f'{user_id}'):

            if os.path.exists(f'{user_id}/{filename}'):
                os.remove(f'{user_id}/{filename}')

            file.save(f'{user_id}/{filename}')

        else:
            os.mkdir(f'{user_id}')
            with open(f'{user_id}/{name}', 'xb') as fh:
                file.save(f'{user_id}/{filename}')


        process_file(user_id, filename)

        # os.remove(f'{user_id}/{filename}')

        response = get_data(user_id, filename)
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        return 'error'
    # except:
    #     return '0'

def main():
    # app.run(debug=True, port=3000, host='0.0.0.0')
    app.run(debug=True, port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()