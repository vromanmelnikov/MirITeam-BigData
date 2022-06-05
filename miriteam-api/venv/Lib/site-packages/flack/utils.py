# coding=utf-8
__all__ = ["slack_username", ]


def slack_username(user_id: str) -> str:
    """ Generate a slack username macro """

    return "<@{}>".format(user_id)
