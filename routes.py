from flask import Flask
from flask import request
app = Flask(__name__)

#make sure to disable this flag 
app.debug = True

@app.route('/', methods=['GET'])
def getRecord():
    #GET /users/<userid>
    #Returns the matching user record or 404 if none exists.
    return "User Record"

@app.route('/', methods=['POST'])
def postRecord():
    #POST /users
    #Creates a new user record using valid user record (JSON).
    #POSTs to existing users should be treated as errors
    #Read JSON input : data = request.get_data()
    #Parse out JSON
    #put into DB
    data = request.get_data()
    return "Record Posted", data

@app.route('/', methods=['DELETE'])
def deleteUser()
    #DELETE /users/<userid>
    #Deletes user record. Returns 404 if the user doesn't exist
    data = request.get_data()
    return "User Deleted", data


if __name__=='__main__':
    app.run()
"""
#Use app.route('/', methods=DESIRED) for splitting methods
@app.route('/', methods=['PUT', 'POST'])
def hello_world():
    if request.method == 'POST' or request.method == 'PUT':
        data = request.get_data()
        print data
        print type(data)
        return data
    else:
        return 'Hello World \n'
"""
