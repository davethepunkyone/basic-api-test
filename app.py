from flask import Flask, request
import json


class Entry:
    """This class is used to manage entries into the system."""
    def __init__(self, entry_id, name, code):
        self.entry_id = entry_id
        self.name = name
        self.code = code

    def as_dict(self) -> dict:
        """This returns the entry as a dict object."""
        return {self.entry_id: {"name": self.name, "code": self.code}}


# This sets up the app and default list of values to work with.
app = Flask(__name__)
entry1 = Entry("A1", "Test Entry 1", 7357)
entry2 = Entry("B1", "Test Entry 2", 1234)
list_of_values = [entry1, entry2]


@app.route('/', methods=['GET'])
def hello_world() -> app.response_class:
    """This is the default test when navigating to the url."""
    data = {"message": "This is a test message."}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/entries', methods=['GET'])
def get_entries() -> app.response_class:
    """This returns all the currently stored entries.
    Accepted methods:
     - GET = Returns all the entries from the list."""
    dict_to_use = dict()
    for entry in list_of_values:
        dict_to_use.update(entry.as_dict())

    response = app.response_class(
        response=json.dumps(dict_to_use),
        status=200,
        mimetype='application/json')
    response.headers['Count-Of-Entries'] = len(list_of_values)
    return response


@app.route('/entries/<val>', methods=['GET', 'DELETE'])
def get_entry(val) -> app.response_class:
    """This gets the current entry and completes an action dependent on the
    method used.
    Accepted methods:
     - GET = Returns the entry identified from the list.
     - DELETE = Removes the entry identified from the list."""
    dict_to_use = dict()
    for entry_to_check in list_of_values:
        if entry_to_check.entry_id == val:
            dict_to_use.update(entry_to_check.as_dict())
            if request.method == "DELETE":
                list_of_values.remove(entry_to_check)

    if len(dict_to_use) == 0:
        data = {"error": "Invalid Entry",
                "error_details": {
                    "description": "The entry value provided is not valid.",
                    "code:": 404,
                    "invalid_value_provided": val}}
        response = app.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json'
        )
        return response
    else:
        if request.method == 'GET':
            response = app.response_class(
                response=json.dumps(dict_to_use),
                status=200,
                mimetype='application/json'
            )
            return response
        elif request.method == "DELETE":
            response = app.response_class(
                status=204,
                mimetype='application/json'
            )
            return response


@app.route('/add', methods=['POST'])
def add_entry():
    """This takes an entry and puts it into the list of entries.
    Accepted methods:
     - POST = This puts the entry in the list if valid. Entry components must
     be passed in the request body with the following keys:
     entry_id (must be unique), name, code (must be int)."""
    if "entry_id" not in request.form:  # No entry ID provided
        response = app.response_class(
            response=json.dumps(return_invalid_entry_details("No entry_id "
                                                             "has been "
                                                             "provided.")),
            status=400,
            mimetype='application/json'
        )
        return response

    if "name" not in request.form:  # No name provided
        response = app.response_class(
            response=json.dumps(return_invalid_entry_details("No name has been"
                                                             " provided.")),
            status=400,
            mimetype='application/json'
        )
        return response

    if "code" not in request.form:  # No code provided
        response = app.response_class(
            response=json.dumps(return_invalid_entry_details("No code has been"
                                                             " provided.")),
            status=400,
            mimetype='application/json'
        )
        return response

    if not request.form["code"].isnumeric():  # Checks the code is numeric
        response = app.response_class(
            response=json.dumps(return_invalid_entry_details("The code "
                                                             "provided is not "
                                                             "numeric.")),
            status=400,
            mimetype='application/json'
        )
        return response

    for entry_to_check in list_of_values:  # Checks the ID isn't already in use
        if entry_to_check.entry_id == request.form["entry_id"]:
            response = app.response_class(
                response=json.dumps(return_invalid_entry_details("The ID "
                                                                 "provided is "
                                                                 "already in "
                                                                 "use.")),
                status=400,
                mimetype='application/json'
            )
            return response

    new_entry = Entry(request.form["entry_id"], request.form["name"],
                      int(request.form["code"]))
    list_of_values.append(new_entry)

    response = app.response_class(
        response=json.dumps(new_entry.as_dict()),
        status=201,
        mimetype='application/json'
    )
    response.headers['Location'] = "http://127.0.0.1:5000/entries/" + \
                                   new_entry.entry_id
    return response


def return_invalid_entry_details(desc: str) -> dict:
    """This takes a description and returns a dict configured in the default
    format."""
    return {"error": "Invalid Entry Details Provided",
            "error_details": {
                "description": desc,
                "code:": 400}}


@app.errorhandler(404)
def not_found(error):
    """This returns a 404 in the event a random URL is provided."""
    data = {"error": error.name,
            "error_details": {
                "description": error.description,
                "code:": error.code}}

    response = app.response_class(
        response=json.dumps(data),
        status=404,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run()
