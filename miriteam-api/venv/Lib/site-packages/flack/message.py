# coding=utf-8
from abc import ABC
from collections import namedtuple

__all__ = ["PrivateResponse", "IndirectResponse", "Attachment", "Action", ]

PrivateResponse = namedtuple("PrivateResponse", ("feedback"))
IndirectResponse = namedtuple("IndirectResponse", ("feedback", "indirect"))


class SlackObject(ABC):
    keys = {}

    def __init__(self, **kwargs):
        self._struct = {k: v for k, v in kwargs.items() if k in self.keys}

    def __getattr__(self, attr):
        try:
            return self._struct[attr]

        except KeyError:
            raise ValueError(attr)

    @property
    def as_dict(self) -> dict:
        return self._struct


class Attachment(SlackObject):
    keys = {
        "fallback",
        "color",
        "pretext",
        "author_name",
        "author_link",
        "author_icon",
        "title",
        "title_link",
        "text",
        "fields",
        "image_url",
        "thumb_url",
        "callback_id",
        "actions"
    }


class Action(SlackObject):
    keys = {
        "name",
        "text",
        "type",
        "style",
        "value",
        "confirm"
    }
