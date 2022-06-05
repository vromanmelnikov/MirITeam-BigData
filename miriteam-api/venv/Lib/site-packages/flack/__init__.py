# coding=utf-8
import logging
import time
import json
from functools import wraps
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from typing import Union, Callable

from requests import post
from flask import (
    Flask, Blueprint, current_app,
    request, jsonify, abort,
)
from werkzeug.exceptions import HTTPException

from .message import Attachment, PrivateResponse, IndirectResponse
from .exceptions import ConfigError

__all__ = ["Flack", ]

logger = logging.getLogger(__name__)

SLACK_TRIGGER = namedtuple("trigger", ("callback", "user"))

CALLER = namedtuple("caller", ("id", "name", "team"))
CHANNEL = namedtuple("channel", ("id", "name", "team"))

thread_executor = ThreadPoolExecutor(1)


def _send_message(url: str, message: str) -> bool:
    """ Send a simple message """
    logger.debug("Sending message to: {}, contents: {}".format(url, message))

    # This should prevent out-of-order issues, which slack really doesn't like
    time.sleep(0.5)
    response = post(url, json=message)

    if response.status_code == 404:
        logger.error("Slack url has expired, aborting.")
        return False

    else:
        return True


def get_form_data(fn: Callable) -> Callable:
    """ Extracts a form-encded payload from request """

    @wraps(fn)
    def inner(*args, **kwargs):
        data = request.form.to_dict()
        kwargs["data"] = data

        return fn(*args, **kwargs)

    return inner


def get_json_data(fn: Callable) -> Callable:
    """ Extracts a json payload from request """

    @wraps(fn)
    def inner(*args, **kwargs):
        data = json.loads(request.form["payload"])
        kwargs["data"] = data

        return fn(*args, **kwargs)

    return inner


def validate_token(fn: Callable) -> Callable:
    """ Validates payload tokens """

    @wraps(fn)
    def inner(*args, **kwargs):
        request_token = kwargs.get("data", {}).get("token")
        flack_token = current_app.config["FLACK_TOKEN"]

        if not flack_token:
            raise ConfigError("A token must be defined")

        elif request_token != flack_token:
            logger.error("Invalid Token")
            abort(403)

        else:
            return fn(*args, **kwargs)

    return inner


def wrap_errors(fn: Callable) -> Callable:
    """ Ensures exceptions are presented in a way slack understands """

    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)

        except HTTPException:
            # No need to alter an HTTP response
            raise

        except Exception as e:
            logger.exception("Caught: %r, coercing to HTTP 500.", e)
            abort(500)

    return inner


class Flack:
    triggers = {}
    commands = {}
    actions = {}

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """ Initialize and register blueprint """

        self.app = app

        self.app.config.setdefault("FLACK_TOKEN", "")
        self.app.config.setdefault("FLACK_URL_PREFIX", "/flack")
        self.app.config.setdefault("FLACK_DEFAULT_NAME", "flack")

        blueprint = Blueprint('slack_flask',
                              __name__,
                              template_folder="templates")

        blueprint.add_url_rule("/webhook", methods=['POST'],
                               view_func=self.dispatch_webhook)
        blueprint.add_url_rule("/command", methods=['POST'],
                               view_func=self.dispatch_command)
        blueprint.add_url_rule("/action", methods=['POST'],
                               view_func=self.dispatch_action)

        app.register_blueprint(blueprint,
                               url_prefix=self.app.config["FLACK_URL_PREFIX"])

    def _indirect_response(self, message: str, url: str) -> None:
        """ Send the response to a separate endpoint """
        indirect_response = {
            "text": "",
            "attachments": [],
            "response_type": "in_channel"
        }

        _, indirect = message

        if isinstance(indirect, Attachment):
            indirect_response["attachments"].append(indirect.as_dict)

        else:
            indirect_response["text"] = indirect

        logger.debug("Dispathing indirect response: %r to %s",
                     indirect_response, url)
        thread_executor.submit(_send_message, url, indirect_response)

    def _response(
        self,
        message: Union[
            None, str, IndirectResponse, PrivateResponse, Attachment
        ],
        response_url: str = None,
        user: str = None,
    ) -> Union[str, dict]:
        """ Generate the HTTP response to an incoming request from Slack """

        response = {
            "username": user or self.app.config["FLACK_DEFAULT_NAME"],
            "text": "",
            "attachments": [],
            "response_type": "in_channel",
            "replace_original": False
        }

        if message is None:
            # No feedback
            return ""

        elif isinstance(message, Attachment):
            response["attachments"].append(message.as_dict)

        elif isinstance(message, IndirectResponse):
            self._indirect_response(message, response_url)

            if not message.feedback:
                # This suppresses any feedback.
                return ""

            elif message.feedback is True:
                # This echoes the users input to the channel
                return jsonify({"response_type": "in_channel"})

            else:
                response["text"] = message.feedback
                response["response_type"] = "ephemeral"

        elif isinstance(message, PrivateResponse):
            response["text"] = message.feedback
            response["response_type"] = "ephemeral"

        else:
            response["text"] = message

        logger.debug("Generated response: %r", response)
        return jsonify(response)

    @get_form_data
    @validate_token
    @wrap_errors
    def dispatch_webhook(self, data: dict) -> Union[str, dict]:
        """ Parse and dispatch a webhook request """
        try:
            prefix = len(data["trigger_word"])
            data["text"] = data["text"][prefix:].strip()
            callback, user = self.triggers[data["trigger_word"]]

        except KeyError:
            logger.error("Unknown trigger: %s", data.get("trigger_word"))
            logger.error("Known triggers: %s", self.triggers.keys())
            abort(400)

        logger.info("Running trigger: '{}' with: '{}'".format(
            data["trigger_word"], data["text"]))

        response = callback(
            text=data["text"],
            user=CALLER(
                data["user_id"],
                data["user_name"],
                data["team_id"]
            )
        )

        return self._response(response, user=user)

    @get_form_data
    @validate_token
    @wrap_errors
    def dispatch_command(self, data: dict) -> Union[str, dict]:
        """ Parse and dispatch a command request """
        try:
            callback = self.commands[data["command"]]

        except KeyError:
            logger.error("Unknown command: %s", data.get("command"))
            abort(400)

        logger.info("Running command: '{}' with: '{}'".format(
            data["command"], data["text"]))

        response = callback(
            text=data["text"],
            trigger=data.get("trigger_id"),
            user=CALLER(
                data["user_id"],
                data["user_name"],
                data["team_id"]
            ),
            channel=CHANNEL(
                data["channel_id"],
                data["channel_name"],
                data["team_id"]
            )
        )

        return self._response(response, response_url=data["response_url"])

    @get_json_data
    @validate_token
    @wrap_errors
    def dispatch_action(self, data: dict) -> Union[str, dict]:
        """ Parse and dispatch an action """

        if not len(data["actions"]):
            raise AttributeError("No action supplied")

        try:
            # We're only handling basic, single-action payloads at this point
            action = data["actions"][0]
            callback = self.actions[action["action_id"]]

        except KeyError:
            logger.error("Unknown action spec: %r", data.get("actions"))
            abort(400)

        logger.info("Running action: %s with value: %s",
                    action["action_id"], action["value"])

        response = callback(
            value=action["value"],
            trigger=data.get("trigger_id"),
            message_ts=data.get("message", {}).get("ts"),
            user=CALLER(
                data["user"]["id"],
                data["user"]["username"],
                data["user"]["team_id"]
            ),
            channel=CHANNEL(
                data["channel"]["id"],
                data["channel"]["name"],
                data["team"]["id"]
            )
        )

        return self._response(response, response_url=data["response_url"])

    def trigger(self, trigger_word: str, **kwargs: str) -> Callable:
        """ Register a trigger word handler """

        if not trigger_word:
            raise AttributeError("invalid invocation")

        kwargs.setdefault("as_user", self.app.config["FLACK_DEFAULT_NAME"])

        def decorator(fn):
            logger.debug("Register trigger: {}".format(trigger_word))

            self.triggers[trigger_word] = SLACK_TRIGGER(
                callback=fn,
                user=kwargs["as_user"])

            return fn

        return decorator

    def command(self, name: str) -> Callable:
        """ Register a slash-command handler """

        if not name:
            raise AttributeError("invalid invocation")

        def decorator(fn):
            logger.debug("Register command: {}".format(name))
            self.commands[name] = fn
            return fn

        return decorator

    def action(self, name: str) -> Callable:
        """ Register a handler for actions """

        if not name:
            raise AttributeError("invalid invocation")

        def decorator(fn):
            logger.debug("Register action: {}".format(name))
            self.actions[name] = fn
            return fn

        return decorator
