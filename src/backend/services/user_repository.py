from typing import Any, Dict


class UserRepository:
    @staticmethod
    async def get_user_info(user_id: str) -> Dict[str, Any]:
        return {}

    @staticmethod
    async def delete_user(user_id: str) -> None:
        return None
