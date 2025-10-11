from enum import IntEnum
import firebase_admin
from firebase_admin import credentials, auth
from app.config import settings

class AuthType(IntEnum):
    GOOGLE = 0

class AuthInitException(Exception):
    pass

class AuthFailedException(Exception):
    pass

class GoogleAuthBackend:
    _instance = None

    def __init__(self, config):
        self.type = AuthType.GOOGLE
        self.cred = credentials.Certificate(config['SA_KEY_FILE'])
        try:
            firebase_admin.initialize_app(credential=self.cred)
        except ValueError:
            # already initialized
            pass
        except Exception as e:
            raise AuthInitException("Firebase init failed") from e

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GoogleAuthBackend({"SA_KEY_FILE": settings.FIREBASE_SA_FILE})
        return cls._instance

    def verify_token(self, token):
        print("\n[Firebase] ====== Token Verification Started ======")
        print(f"[Firebase] Service account file: {settings.FIREBASE_SA_FILE}")
        
        try:
            print("[Firebase] Attempting to verify token...")
            decoded = auth.verify_id_token(token)
            print("[Firebase] Token decoded successfully")
            print(f"[Firebase] Email verified status: {decoded.get('email_verified')}")
            
            if not decoded.get('email_verified'):
                print("[Firebase] ERROR: Email not verified")
                raise AuthFailedException("Email not verified")
                
            user_data = {
                'name': decoded.get('name', 'Anonymous'),
                'email': decoded.get('email'),
                'uid': decoded.get('uid'),
            }
            print(f"[Firebase] Verification successful for user: {user_data['email']}")
            return user_data
            
        except auth.InvalidIdTokenError as e:
            print(f"[Firebase] ERROR: Invalid token - {str(e)}")
            raise AuthFailedException("Invalid token") from e
        except auth.ExpiredIdTokenError as e:
            print(f"[Firebase] ERROR: Token expired - {str(e)}")
            raise AuthFailedException("Token expired") from e
        except auth.RevokedIdTokenError as e:
            print(f"[Firebase] ERROR: Token revoked - {str(e)}")
            raise AuthFailedException("Token revoked") from e
        except Exception as e:
            print(f"[Firebase] ERROR: Verification failed - {str(e)}")
            raise AuthFailedException("Token verification failed") from e
