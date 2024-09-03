import uuid
from datetime import datetime

from database.db_init import db
from database.models import ContractUpdateToken


def create_new_token(**kwargs) -> str:
    """
    :param kwargs:
    :return: str
    This is a helper function to create a new token
    """
    new_token = ContractUpdateToken(
        token=str(uuid.uuid4()),
        created_at=datetime.now(),
        **kwargs
    )
    db.session.add(new_token)
    db.session.commit()
    return new_token.token
