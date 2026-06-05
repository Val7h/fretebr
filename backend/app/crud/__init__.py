from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_password, hash_password
from app.crud.frete import (
    create_frete,
    get_frete,
    list_fretes,
    update_frete,
    delete_frete,
    get_motorista_fretes
)

__all__ = [
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "verify_password",
    "hash_password",
    "create_frete",
    "get_frete",
    "list_fretes",
    "update_frete",
    "delete_frete",
    "get_motorista_fretes"
]
