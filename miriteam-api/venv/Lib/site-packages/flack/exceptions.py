# coding=utf-8
__all__ = ["ConfigError", "OAuthConfigError", "OAuthError"]


class ConfigError(Exception):
    pass


class OAuthConfigError(Exception):
    pass


class OAuthError(Exception):
    pass
