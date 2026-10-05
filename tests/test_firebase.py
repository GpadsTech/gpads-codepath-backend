from app.config.firebase import FirebaseConfig


def test_firebase_connection():

    firebase = FirebaseConfig()

    db = firebase.initialize()

    assert db is not None