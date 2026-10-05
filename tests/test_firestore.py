from app.config.firebase import FirebaseConfig


def test_firestore_connection():

    firebase = FirebaseConfig()

    db = firebase.initialize()

    document = db.collection(
        "system"
    ).document(
        "connection_test"
    )

    document.set({
        "status": "ok",
        "message": "Firebase conectado com sucesso"
    })

    result = document.get()

    assert result.exists

    data = result.to_dict()

    assert data["status"] == "ok"