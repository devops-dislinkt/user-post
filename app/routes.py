from flask import jsonify, request, current_app, Blueprint, g
# from app import app, posts_col
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
import json
from datetime import datetime
from app import mongo_api

api = Blueprint('api', __name__)

@api.route('/add', methods=['POST'])
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
    try:
         request.json['date'] = datetime.today().replace(microsecond=0)
         mongo_api.collection('posts').insert_one(request.json)                
    except DuplicateKeyError:
        return jsonify("username not unique"), 400
    return jsonify({"success": True}), 200

@api.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
    """
    try:
        posts_documents = mongo_api.collection('posts').find()
        posts: list[dict] = [post_document for post_document in posts_documents]
        for post in posts: post['_id'] = str(post['_id'])
        return jsonify(posts), 200
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