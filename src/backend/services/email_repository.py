from typing import Any, List


class EmailRepository:
    @staticmethod
    async def get_user_emails(user_id: str) -> List[Any]:
        return []

    @staticmethod
    async def delete_all_for_user(user_id: str) -> None:
        return None
