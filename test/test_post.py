import os
import pytest
from app import create_app, mongo_api
from flask.testing import FlaskClient

def setup_db():
    '''setup database before tests starts executing'''
    # reroute traffic to test database
    mongo_api.database = mongo_api.connection[os.environ['TEST_DB']]
    # empty test db just in case
    mongo_api.connection.drop_database(os.environ['TEST_DB'])

    # insert dummy data for tests
    mongo_api.collection('user_post').insert_many([
        {
            "_id": "post1",
            "username": "user1",
            "title": "Post title",
            "content": "text content",
            "images": ["img1","img2"],
            "links": ["link1", "link2"],
            "like": [],
            "dislike": [],
            "comments": []
        },
        {
            "id": "post2",
            "username": "user2",
            "title": "Post title2",
            "content": "text content2",
            "images": [],
            "links": [],
            "like": [],
            "dislike": [],
            "comments": [{"username": "user2","comment": "comment2"},{"username": "user10","comment": "comment10"}]
        },
    ])

def teardown_db():
    '''destroy testing database and all of its content after tests finished.'''
    mongo_api.connection.drop_database(os.environ['TEST_DB'])

@pytest.fixture(scope='module')
def client() -> FlaskClient:
    '''
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    '''
    # setup
    app = create_app('test')
    setup_db()
    
    with app.test_client() as client:
        yield client
    
    # teardown
    teardown_db()

class TestClassCreatePost:
    '''Test case for creating new post'''

    def test_create_post(self, client: FlaskClient):
        response = client.post('/api/add', json={
                        "_id": "post4",
                        "username": "user1",
                        "title": "Post title",
                        "content": "text content",
                        "images": ["img1","img2"],
                        "links": ["link1", "link2"],
                        "like": [],
                        "dislike": [],
                        "comments": [{"username": "user2","comment": "comment2"},{"username": "user10","comment": "comment10"}]
                    })
        after = client.get('/api/list')
        posts_after = len(after)
        assert 3 == posts_after
        assert after.status_code == 200
    
    def test_delete_post(self, client: FlaskClient):
        before = client.get('/api/list')
        posts_before = len(before)
        print(f"posts_before = {posts_before}")        
        response = client.delete('/api/delete?id=post4')
        after = client.get('/api/list')
        posts_after = len(after)
        assert posts_before - 1 == posts_after
        assert after.status_code == 200
        assert before.status_code == 200
    
    def test_find_post(self, client: FlaskClient):
        response = client.get('/api/find?id=post1')
        assert response.status_code == 200
        assert response.data['_id'] == "post1"

    def test_like_post(self, client: FlaskClient):
        like_obj = {"_id" : "post1", "username" : "username1"}
        response = client.post('/api/like', json=like_obj)
        post = client.get('/api/find?id=post1')

        assert response.status_code == 200
        assert post.status_code == 200
        assert like_obj in post.data['like']

    def test_dislike_post(self, client: FlaskClient):
        dislike_obj = {"_id" : "post1", "username" : "username1"}
        response = client.post('/api/dislike', json=dislike_obj)
        post = client.get('/api/find?id=post1')

        assert response.status_code == 200
        assert post.status_code == 200
        assert dislike_obj in post.data['dislike']

    def test_comment_post(self, client: FlaskClient):
        comment_obj =  {"_id" : "post1", "username" : "username1", "comment" : "comment text"}
        response = client.post('/api/comment', json=comment_obj)
        post = client.get('/api/find?id=post1')

        assert response.status_code == 200
        assert post.status_code == 200
        assert comment_obj in post.data['comments']

    def test_delete_comment_post(self, client: FlaskClient):
        comment_obj =  {"_id" : "post1", "username" : "username1", "comment" : "comment text"}
        response = client.post('/api/comment', json=comment_obj)
        response_delete = client.delete('/api/comment', json=comment_obj)
        post = client.get('/api/find?id=post1')

        assert response.status_code == 200
        assert response_delete.status_code == 200
        assert post.status_code == 200
        assert comment_obj not in post.data['comments']

    def test_update_post(self, client: FlaskClient):
        post_obj = {"_id": "post1", "title": "NEW post title", "content": "NEW text content"}
        response = client.post('/api/update', json=post_obj)
        post = client.get('/api/find?id=post1')

        assert response.status_code == 200
        assert post.status_code == 200
        assert post.data['title'] == "NEW post title"
        assert post.data['content'] == "NEW text content"