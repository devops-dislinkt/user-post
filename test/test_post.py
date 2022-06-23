import os
import pytest
from app import create_app, mongo_api
from flask.testing import FlaskClient
from app import mongo_api


def seed_db():
    """setup database before tests starts executing"""

    # insert dummy data for tests
    mongo_api.collection("user_post").insert_many(
        [
            {
                "_id": "62b466a139eb0ef844e336cc",
                "username": "user1",
                "title": "Post title",
                "content": "text content",
                "images": ["img1", "img2"],
                "links": ["link1", "link2"],
                "like": [],
                "dislike": [],
                "comments": [],
            },
            {
                "id": "62b466a139eb0ef844e336cC",
                "username": "user2",
                "title": "Post title2",
                "content": "text content2",
                "images": [],
                "links": [],
                "like": [],
                "dislike": [],
                "comments": [
                    {"username": "user2", "comment": "comment2"},
                    {"username": "user10", "comment": "comment10"},
                ],
            },
        ]
    )


@pytest.fixture(scope="module")
def client() -> FlaskClient:
    """
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    """
    # setup

    app = create_app("test")
    mongo_api.collection("user_post").drop()

    seed_db()

    with app.test_client() as client:
        yield client

    mongo_api.collection("user_post").drop()


class TestClassCreatePost:
    """Test case for creating new post"""

    def test_create_post(self, client: FlaskClient):
        response = client.post(
            "/api/post/add",
            json={
                "_id": "post4",
                "username": "user1",
                "title": "Post title",
                "content": "text content",
                "images": ["img1", "img2"],
                "links": ["link1", "link2"],
                "like": [],
                "dislike": [],
                "comments": [
                    {"username": "user2", "comment": "comment2"},
                    {"username": "user10", "comment": "comment10"},
                ],
            },
        )

        assert response.status_code == 200

    def test_delete_post(self, client: FlaskClient):

        response = client.delete("/api/post/delete?id=post4")
        assert response.status_code == 200

    # def test_find_post(self, client: FlaskClient):
    #     response = client.get("/api/post/1b")
    #     assert response.status_code == 200
    #     print('ovdeeee', response.data)
    #     assert response.data['_id'] == '1'

    def test_like_post(self, client: FlaskClient):
        like_obj = {"post_id": "62b466a139eb0ef844e336cc", "username": "username1"}
        response = client.post("/api/post/like", json=like_obj)
        print(response.data)

        assert response.status_code == 200

    def test_dislike_post(self, client: FlaskClient):
        dislike_obj = {"post_id": "62b466a139eb0ef844e336cc", "username": "username1"}
        response = client.post("/api/post/dislike", json=dislike_obj)

        assert response.status_code == 200

    def test_comment_post(self, client: FlaskClient):
        comment_obj = {
            "post_id": "post1",
            "username": "username1",
            "comment": "comment text",
        }
        response = client.post("/api/post/comment", json=comment_obj)

        assert response.status_code == 200

    def test_delete_comment_post(self, client: FlaskClient):
        comment_obj = {
            "post_id": "post1",
            "username": "username1",
            "comment": "comment text",
        }
        response = client.post("/api/post/comment", json=comment_obj)
        response_delete = client.delete("/api/post/comment", json=comment_obj)

        assert response.status_code == 200
        assert response_delete.status_code == 200

    def test_update_post(self, client: FlaskClient):
        post_obj = {
            "id": "post1",
            "title": "NEW post title",
            "content": "NEW text content",
        }
        response = client.put("/api/post/update", json=post_obj)

        assert response.status_code == 200
