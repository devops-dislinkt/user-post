from flask import jsonify, request, current_app, Blueprint, g
# from app import app, posts_col
from pymongo.errors import DuplicateKeyError
from kafka.errors import KafkaError
from bson.objectid import ObjectId
import json
from datetime import datetime
from app import mongo_api
from app.kafka_utils import create_producer
from os import environ

api = Blueprint('api', __name__)


producer = create_producer()

@api.post('/add')
def create():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json=  {
                        "id": "post2",
                        "username": "user1",
                        "title": "Post title",
                        "content": "text content",
                        "images": ["img1","img2"],
                        "links": ["link1", "link2"],
                        "like": [],
                        "dislike": [],
                        "comments": [{"username": "user2","comment": "comment2"},{"username": "user10","comment": "comment10"}]
                    }
    """
    user: str = request.headers.get("user")
    try:
        request.json['date'] = datetime.today().replace(microsecond=0)
        post = mongo_api.collection('posts').insert_one(request.json)

        if (producer):
            producer.send(environ['KAFKA_TOPIC'], {'username': user, 'post_title': request.json['title'], 'post_id': str(post.inserted_id) })
    except DuplicateKeyError:
        return jsonify("username not unique"), 400
    except KafkaError as err:
         print("kafka producer - Exception during sending message to producer - {}".format(err))

    return jsonify(str(post.inserted_id))

@api.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from collection as JSON.
    """
    try:
        posts_documents = mongo_api.collection('posts').find()
        posts: list[dict] = [post_document for post_document in posts_documents]
        for post in posts: post['_id'] = str(post['_id'])
        return jsonify(posts), 200
    except Exception as e:
        return f"An Error Occurred: {e}"
        
@api.route('/find', methods=['GET'])
def find():
    """
        delete() : Fetches one documents from collection as JSON.
        e.g. = http://localhost/find?id=post1
    """
    try:
        doc_id = request.args.get('id')        
        document = mongo_api.collection('posts').find_one({ "_id": ObjectId(doc_id)}) 
        document['_id'] = str(document['_id'])
        return jsonify(document), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/like', methods=['POST'])
def like_post():
    """
        like_post() : Add username in post 'likes' array filed.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1"
                    }
    """
    # TODO like twice
    try:
        post_id = request.json['post_id']
        username = request.json['username'] 

        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$push': {'like': username}})
        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$pull': {'dislike': username}})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/dislike', methods=['POST'])
def dislike_post():
    """
        dislike_post() : Add username in post 'dislikes' array filed.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1"
                    }
    """
    # TODO dislike twice
    try:
        post_id = request.json['post_id']
        username = request.json['username']

        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$push': {'dislike': username}})
        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$pull': {'like': username}})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/comment', methods=['POST'])
def post_comment():
    """
        post_comment() : Add a comment to the post.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1",
                        "comment" : "comment text"
                    }
    """
    try:
        post_id = request.json['post_id']
        username = request.json['username']
        comment = request.json['comment']
        
        comment_obj = {
                        "username": username,
                        "comment": comment, 
                        'date': datetime.today().replace(microsecond=0)
                      }
        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': comment_obj}})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/comment', methods=['DELETE'])
def delete_comment():
    """
        delete_comment() : Deletes a comment.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1",
                        "comment" : "comment text"
                    }
    """
    try:
        post_id = request.json['post_id']
        username = request.json['username']
        comment = request.json['comment']
        
        comment_obj = {"username": username,"comment": comment}
        mongo_api.collection('posts').update_one({'_id': ObjectId(post_id)}, {'$pull': {'comments': comment_obj}})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from collection.
        e.g. = http://localhost/delete?id=post1
    """
    try:
        doc_id = request.args.get('id')        
        mongo_api.collection('posts').delete_one({ "_id": ObjectId(doc_id)}) 

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@api.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json=  {
                        "id": "post1",
                        "title": "NEW post title",
                        "content": "NEW text content",
                    }
    """
    try:
        doc_id = request.json['id']
        
        myquery = { "_id": ObjectId(doc_id) }
        request.json.pop('id', None)

        newvalues = { "$set": request.json }

        mongo_api.collection('posts').update_one(myquery, newvalues)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

# allow all origin
@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response