import os
import hashlib
import platform

class misc:

    @staticmethod
    def get_hwid():
        try:
            if platform.system().lower() == "windows":
                # استخدم اسم المستخدم كـ HWID بديل بسيط
                return os.getlogin()
            else:
                # في لينكس أو Vercel: نستخدم machine-id
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
        except:
            return "unknown-hwid"

    @staticmethod
    def get_checksum():
        try:
            path = os.path.abspath(__file__)
            if not os.path.exists(path):
                return "checksum-error"

            with open(path, "rb") as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except:
            return "checksum-error"
