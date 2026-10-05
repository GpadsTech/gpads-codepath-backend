import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()


class FirebaseConfig:
    """
    Responsável exclusivamente pela inicialização do Firebase Admin SDK.

    Esta classe fornece acesso ao Firestore para as demais camadas
    da aplicação.

    Responsabilidade única:
    - Carregar as credenciais do Firebase.
    - Inicializar o Firebase Admin SDK.
    - Disponibilizar a instância do Firestore.
    """

    def __init__(self):
        self._firestore = None

    def initialize(self):
        """
        Inicializa o Firebase Admin SDK.

        A inicialização ocorre apenas uma vez, mesmo que este método
        seja chamado novamente durante o ciclo de vida da aplicação.
        """

        if not firebase_admin._apps:

            credentials_path = os.getenv(
                "FIREBASE_CREDENTIALS_PATH"
            )

            if not credentials_path:
                raise ValueError(
                    "FIREBASE_CREDENTIALS_PATH não foi configurado."
                )

            base_dir = Path(__file__).resolve().parent.parent.parent

            credentials_file = base_dir / credentials_path

            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"Credencial do Firebase não encontrada: "
                    f"{credentials_file}"
                )

            credential = credentials.Certificate(
                str(credentials_file)
            )

            firebase_admin.initialize_app(
                credential
            )

        self._firestore = firestore.client()

        return self._firestore

    @property
    def firestore(self):
        """
        Retorna a instância do Firestore.

        O Firebase deve ser inicializado antes da utilização.
        """

        if self._firestore is None:
            raise RuntimeError(
                "Firebase ainda não foi inicializado."
            )

        return self._firestore