import os

class Config(object):
	SECRET_KEY = os.environ.get("SECRET_KEY") or "fallback-secret-key-which-you-cannot-guess"