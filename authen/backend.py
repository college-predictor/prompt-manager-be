import logging
from enum import Enum

from django.conf import settings

import firebase_admin
import firebase_admin.auth

logger = logging.getLogger(__file__)


class BackendType(Enum):
    GOOGLE = (0, )

    @property
    def i(self):
        return self.value[0]
    
    @classmethod
    def from_val(cls, val):
        for t in BackendType:
            if t.i == val:
                return t
        raise ValueError(f"Invalid value for backend type: {val}")
    

class BackendInitException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class AuthFailedException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class GoogleAuthBackend:
    instance = None

    def __init__(self, config):
        self.type = BackendType.GOOGLE
        self.cred = firebase_admin.credentials.Certificate(config['SA_KEY_FILE'])

        try:
            firebase_admin.initialize_app(self.cred)
        except Exception as e:
            logger.error(f"Error initializing Firebase SDK: {e}", exc_info=1)
            raise BackendInitException()


    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = GoogleAuthBackend({"SA_KEY_FILE": settings.FIREBASE_SA_FILE})
        return cls.instance


    def verify_token(self, token):
        try:
            decoded_token = firebase_admin.auth.verify_id_token(token)

            # if not decoded_token.get('email_verified'):
            #     raise AuthFailedException()
            
        except firebase_admin.auth.InvalidIdTokenError as e:
            logger.error(f"Invalid Firebase Token: {e}", exc_info=1)
            raise AuthFailedException()

        return {
            'name': decoded_token.get('name', 'Anonymous'),
            'email': decoded_token.get('email'),
        }
    