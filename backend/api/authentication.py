from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings

class DBContextJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that ensures the token was issued for the 
    current active database. If the database name in the token doesn't match 
    the current settings, authentication fails (triggering logout in frontend).
    """
    def get_validated_token(self, raw_token):
        try:
            validated_token = super().get_validated_token(raw_token)
            
            # Get the database identifier from settings
            db_conf = settings.DATABASES['default']
            current_db_id = f"{db_conf.get('HOST', '127.0.0.1')}:{db_conf.get('PORT', '5432')}/{db_conf.get('NAME', 'postgres')}"
            
            # Get the database identifier from the token claims
            token_db_id = validated_token.get('db_name')
            
            # Force logout if database identifier doesn't match OR if it's missing (legacy tokens)
            if token_db_id != current_db_id:
                raise InvalidToken({
                    "detail": f"Database context mismatch (Token: {token_db_id}, Server: {current_db_id}). Please login again.",
                    "code": "db_mismatch"
                })

                
            return validated_token
        except Exception as e:
            # Re-raise InvalidToken if it was our custom check
            if isinstance(e, InvalidToken):
                raise e
            # Otherwise let the parent handle it
            return super().get_validated_token(raw_token)
