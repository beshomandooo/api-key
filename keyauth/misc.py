  import os
  import hashlib
  import platform

  class misc:

      @staticmethod
      def get_hwid():
          if platform.system() == "Windows":
              return os.getenv("COMPUTERNAME")
          else:
              try:
                  with open("/etc/machine-id", "r") as f:
                      return f.read().strip()
              except FileNotFoundError:
                  return "unknown-hwid"

      @staticmethod
      def get_checksum():
          path = os.path.abspath(__file__)
          if not os.path.exists(path):
              return "unknown-checksum"

          md5_hash = hashlib.md5()
          with open(path, "rb") as a_file:
              content = a_file.read()
              md5_hash.update(content)
          return md5_hash.hexdigest()
