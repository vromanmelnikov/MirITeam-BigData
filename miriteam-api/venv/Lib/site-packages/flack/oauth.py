# coding=utf-8
import logging
from functools import wraps
from collections import namedtuple
from typing import Callable

from requests import post, HTTPError
from flask import request, render_template, abort
from flask import current_app as app

from .exceptions import OAuthConfigError, OAuthError

__all__ = ["render_button", "callback", ]

logger = logging.getLogger(__name__)

DEFAULT_OAUTH_SCOPE = "commands,users:read,channels:read,chat:write:bot"

OAuthCredentials = namedtuple(
    "oauth_credentials",
    ("team_id", "access_token", "scope")
)


def render_button() -> str:
    """ Generates an HTML button for adding the app to a workspace """

    if not app.config.get("FLACK_CLIENT_ID"):
        raise OAuthConfigError("Requires client id")

    logger.debug("Rendering oauth button")
    return render_template(
        "oauth_button.tpl",
        client_id=app.config["FLACK_CLIENT_ID"],
        auth_scope=app.config.get("FLACK_SCOPE", DEFAULT_OAUTH_SCOPE)
    )


def _oauth_callback_response(code: str) -> OAuthCredentials:
    """ Request OAuth credentials from Slack """

    try:
        logger.debug(u"Requesting OAuth Credentials")
        response = post("https://slack.com/api/oauth.access", data={
            "code": code,
            "client_id": app.config["FLACK_CLIENT_ID"],
            "client_secret": app.config["FLACK_CLIENT_SECRET"]
        })
        response.raise_for_status()

        oauth_response = response.json()
        logger.info(u"Received new OAuth credentials for team: %s, scope: %s",
                    oauth_response["team_id"], oauth_response["scope"])

        return OAuthCredentials(team_id=oauth_response["team_id"],
                                 access_token=oauth_response["access_token"],
                                 scope=oauth_response["scope"])

    except HTTPError:
        raise OAuthError("Slack rejected the request")


def callback(fn: Callable) -> Callable:
    """ Registers an OAuth Callback handler """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info(u"OAuth callback triggered")

        code = request.args.get("code")
        if not code:
            abort(400, "Bad request")

        try:
            credentials = _oauth_callback_response(code)
            kwargs.update(credentials=credentials)

        except OAuthError:
            logger.exception("OAuth callback rejected")
            abort(500, "Internal error")

        except Exception:
            logger.exception("Unknown error")
            abort(500, "Internal error")

        return fn(*args, **kwargs)

    return wrapper
