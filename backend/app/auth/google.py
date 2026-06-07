"""
Google OAuth 2.0 Authentication Handler
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthConfig:
    """Configuração do Google OAuth 2.0"""

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
    GOOGLE_SCOPES = ["openid", "email", "profile"]

    @classmethod
    def get_auth_url(cls) -> Optional[str]:
        """Gera a URL de autenticação do Google"""
        if not cls.GOOGLE_CLIENT_ID:
            logger.warning("GOOGLE_CLIENT_ID não configurado")
            return None

        params = {
            "client_id": cls.GOOGLE_CLIENT_ID,
            "redirect_uri": cls.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(cls.GOOGLE_SCOPES),
            "access_type": "offline",
        }

        return f"{cls.GOOGLE_AUTH_URL}?{urlencode(params)}"


class GoogleOAuthHandler:
    """Handler para autenticação com Google"""

    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """
        Troca authorization code por access token

        Args:
            code: Authorization code recebido do Google

        Returns:
            Dict com access_token, id_token, etc ou None em caso de erro
        """
        try:
            payload = {
                "code": code,
                "client_id": GoogleOAuthConfig.GOOGLE_CLIENT_ID,
                "client_secret": GoogleOAuthConfig.GOOGLE_CLIENT_SECRET,
                "redirect_uri": GoogleOAuthConfig.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }

            response = requests.post(
                GoogleOAuthConfig.GOOGLE_TOKEN_URL,
                data=payload,
                timeout=10
            )
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao trocar código por token: {str(e)}")
            return None

    @staticmethod
    def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações do usuário usando o access token

        Args:
            access_token: Access token do Google

        Returns:
            Dict com dados do usuário (id, email, name, picture) ou None
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                GoogleOAuthConfig.GOOGLE_USER_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao obter info do usuário: {str(e)}")
            return None

    @staticmethod
    def authenticate_with_google(code: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário com Google
        Fluxo completo: code -> token -> user info

        Args:
            code: Authorization code do Google

        Returns:
            Dict com dados do usuário ou None em caso de erro
        """
        # 1. Trocar código por token
        token_data = GoogleOAuthHandler.exchange_code_for_token(code)
        if not token_data or "access_token" not in token_data:
            logger.error("Falha ao obter access token")
            return None

        access_token = token_data.get("access_token")

        # 2. Obter info do usuário
        user_info = GoogleOAuthHandler.get_user_info(access_token)
        if not user_info:
            logger.error("Falha ao obter info do usuário")
            return None

        return {
            "google_id": user_info.get("id"),
            "email": user_info.get("email"),
            "nome": user_info.get("name", ""),
            "foto": user_info.get("picture", ""),
            "access_token": access_token,
            "id_token": token_data.get("id_token"),
        }
