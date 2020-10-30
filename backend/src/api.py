import os
from flask import Flask, request, jsonify, abort, flash
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}})


CORS(app,resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
'''
The after_request decorator is used to set Access-Control-Allow
'''
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
    return response



'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES


@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message': "Hello, World" 
    })


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    try:
        all_drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in all_drinks]
        })
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        abort(404)
        


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@cross_origin()
@requires_auth('get:drinks-detail')
def retrieve_details(payload):
    try:
        all_drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in all_drinks]
        })
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_new_drink(payload):
    body = request.get_json()
    drink = Drink(title=body.get("title"), recipe=json.dumps(body.get("recipe")))
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):

    body = request.get_json()

    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            raise ValueError("Entry not found")
        if "title" in body:
            drink.title = body.get("title")
        if "recipe" in body:
            drink.recipe = json.dumps(body.get("recipe"))
        
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(404)
    
    # return jsonify({
    #         "success": True,
    #         "drinks": []
    #     })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            raise ValueError("Entry not found")
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception:
        abort(404)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(401)
def authorization_header_missing(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authorization issue"
    }), 401
