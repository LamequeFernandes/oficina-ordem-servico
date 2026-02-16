from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings  # SECRET_KEY, ALGORITHM

import base64
import json

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def criar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_senha: str) -> bool:
    """Compara a senha com seu hash."""
    return pwd_context.verify(senha, hash_senha)


def criar_token_jwt(usuario_id: int) -> str:
    """Gera um token JWT válido por 24 horas."""
    expira = datetime.utcnow() + timedelta(hours=24)   # type: ignore
    payload = {'sub': str(usuario_id), 'exp': expira, 'iss': settings.JWT_ISSUER}   # type: ignore
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )   # type: ignore


# def decodificar_token_jwt(token: str) -> int | None:
#     """Valida o token e retorna o ID do usuário."""
#     try:
#         print(f"SECRET_KEY: {settings.SECRET_KEY[:10]}...")  # primeiros 10 chars
#         print(f"ALGORITHM: {settings.ALGORITHM}")
#         print(f"JWT_ISSUER: {settings.JWT_ISSUER}")
#         payload = jwt.decode(
#             token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], issuer=settings.JWT_ISSUER   # type: ignore
#         )
#         print(f"Payload decodificado: {payload}")
#         return int(payload.get('sub'))   # type: ignore
#     except JWTError as e:
#         print(f"Erro JWT: {type(e).__name__}: {e}")
#         return None
#     except ValueError as e:
#         print(f"Erro ValueError: {e}")
#         return None

def _decode_jwt_payload_unsafe(token: str) -> dict | None:
    """Decodifica o payload do JWT SEM validar assinatura (apenas para debug)."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # Adiciona padding se necessário
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_json)
    except Exception as e:
        print(f"Erro ao decodificar payload: {e}")
        return None


def decodificar_token_jwt(token: str) -> int | None:
    """Valida o token e retorna o ID do usuário."""
    try:
        print("=" * 50)
        print("DEBUG JWT DECODE")
        print("=" * 50)
        
        # Configurações da API
        print(f"[API] SECRET_KEY: {settings.SECRET_KEY[:15]}...{settings.SECRET_KEY[-5:]}")
        print(f"[API] ALGORITHM: {settings.ALGORITHM}")
        print(f"[API] JWT_ISSUER: '{settings.JWT_ISSUER}'")
        
        # Token recebido
        print(f"\n[TOKEN] Primeiros 50 chars: {token[:50]}...")
        
        # Decodifica payload sem validar (para debug)
        payload_unsafe = _decode_jwt_payload_unsafe(token)
        if payload_unsafe:
            print(f"\n[TOKEN PAYLOAD - SEM VALIDAÇÃO]:")
            print(f"  sub: {payload_unsafe.get('sub')}")
            print(f"  iss: '{payload_unsafe.get('iss')}'")
            print(f"  exp: {payload_unsafe.get('exp')}")
            
            # Verifica expiração
            exp = payload_unsafe.get('exp')
            if exp:
                exp_dt = datetime.utcfromtimestamp(exp)
                now = datetime.utcnow()
                print(f"  exp (datetime): {exp_dt}")
                print(f"  now (datetime): {now}")
                print(f"  expirado: {now > exp_dt}")
            
            # Compara issuer
            token_iss = payload_unsafe.get('iss', '')
            api_iss = settings.JWT_ISSUER
            print(f"\n[ISSUER COMPARISON]:")
            print(f"  Token issuer: '{token_iss}' (len={len(str(token_iss))})")
            print(f"  API issuer:   '{api_iss}' (len={len(str(api_iss))})")
            print(f"  Match: {token_iss == api_iss}")
            print(f"  Token issuer bytes: {[ord(c) for c in str(token_iss)]}")
            print(f"  API issuer bytes:   {[ord(c) for c in str(api_iss)]}")
        
        # Tenta decodificar normalmente
        print(f"\n[DECODE ATTEMPT]...")
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM], 
            issuer=settings.JWT_ISSUER
        )
        print(f"[SUCCESS] Payload: {payload}")
        return int(payload.get('sub'))
        
    except JWTError as e:
        print(f"\n[ERRO JWT] {type(e).__name__}: {e}")
        
        # Tenta sem validar issuer para ver se é esse o problema
        try:
            payload_no_iss = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM],
                options={"verify_iss": False}
            )
            print(f"[INFO] Decode SEM validar issuer funcionou! Payload: {payload_no_iss}")
            print("[CAUSA] O problema é o ISSUER!")
        except JWTError as e2:
            print(f"[INFO] Decode sem issuer também falhou: {e2}")
            
            # Tenta sem validar assinatura
            try:
                payload_no_sig = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_signature": False, "verify_iss": False}
                )
                print(f"[INFO] Decode SEM validar assinatura funcionou! Payload: {payload_no_sig}")
                print("[CAUSA] O problema é a SECRET_KEY ou ALGORITHM!")
            except JWTError as e3:
                print(f"[INFO] Decode sem assinatura também falhou: {e3}")
        
        return None
    except ValueError as e:
        print(f"\n[ERRO ValueError]: {e}")
        return None
