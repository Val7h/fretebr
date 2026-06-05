from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_password, hash_password
from app.crud.frete import (
    create_frete,
    get_frete,
    list_fretes,
    update_frete,
    delete_frete,
    get_motorista_fretes
)
from app.crud.match import (
    create_match,
    get_match,
    list_matches,
    update_match_status,
    cancel_match,
    delete_match
)
from app.crud.message import (
    create_message,
    get_message,
    get_messages_by_match,
    delete_message
)

__all__ = [
    # User CRUD
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "verify_password",
    "hash_password",
    # Frete CRUD
    "create_frete",
    "get_frete",
    "list_fretes",
    "update_frete",
    "delete_frete",
    "get_motorista_fretes",
    # Match CRUD
    "create_match",
    "get_match",
    "list_matches",
    "update_match_status",
    "cancel_match",
    "delete_match",
    # Message CRUD
    "create_message",
    "get_message",
    "get_messages_by_match",
    "delete_message"
]
