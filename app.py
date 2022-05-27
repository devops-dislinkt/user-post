# Required imports
import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
posts_col_ref = db.collection('posts')

@app.route('/add', methods=['POST'])
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
        id = request.json['id']
        posts_col_ref.document(id).set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/like', methods=['POST'])
def like_post():
    """
        like_post() : Add username in post 'likes' array filed.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1"
                    }
    """
    try:
        post_id = request.json['post_id']
        username = request.json['username']

        post_ref = posts_col_ref.document(post_id)
        post_ref.update({'like': firestore.ArrayUnion([username])})
        post_ref.update({'dislike': firestore.ArrayRemove([username])})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/dislike', methods=['POST'])
def dislike_post():
    """
        dislike_post() : Add username in post 'dislikes' array filed.
        e.g. json=  {
                        "post_id" : "post1",
                        "username" : "username1"
                    }
    """
    try:
        post_id = request.json['post_id']
        username = request.json['username']

        post_ref = posts_col_ref.document(post_id)
        post_ref.update({'dislike': firestore.ArrayUnion([username])})
        post_ref.update({'like': firestore.ArrayRemove([username])})

        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/comment', methods=['POST'])
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
        
        post_ref = posts_col_ref.document(post_id)
        comment_obj = {"username": username,"comment": comment}
        post_ref.update({'comments': firestore.ArrayUnion([comment_obj])})
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/comment', methods=['DELETE'])
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
        
        post_ref = posts_col_ref.document(post_id)
        comment_obj = {"username": username,"comment": comment}
        post_ref.update({'comments': firestore.ArrayRemove([comment_obj])})
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
    """
    try:
        # Check if ID was passed to URL query
        doc_id = request.args.get('id')
        if doc_id:
            document = posts_col_ref.document(doc_id).get()
            return jsonify(document.to_dict()), 200
        else:
            all_documents = [doc.to_dict() for doc in posts_col_ref.stream()]
            return jsonify(all_documents), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection.
        e.g. = http://localhost/delete?id=post1
    """
    try:
        # Check for ID in URL query
        doc_id = request.args.get('id')
        posts_col_ref.document(doc_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json=  {
                        "id": "post1",
                        "title": "NEW post title",
                        "content": "NEW text content",
                    }
    """
    try:
        id = request.json['id']
        posts_col_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)