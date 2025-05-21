
# ملف keyauth/api.py المبسط
from keyauth.exceptions import KeyauthError

class User:
    def __init__(self):
        self.username = None
        self.ip = None
        self.hwid = None
        self.expires = None

class Keyauth:
    def __init__(self, name, owner_id, secret, version, file_hash):
        self.name = name
        self.owner_id = owner_id
        self.secret = secret
        self.version = version
        self.file_hash = file_hash
        self.user = User()

    def license(self, license_key):
        if not license_key.startswith("bylTry"):
            raise KeyauthError("Invalid license key")
        self.user.username = "besho"
        self.user.ip = "127.0.0.1"
        self.user.hwid = "dummy-hwid"
        self.user.expires = "2025-12-31"
