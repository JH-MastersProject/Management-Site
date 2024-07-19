import string

import qrcode
import secrets
import binascii
import hashlib

VERSION = 1.0


class QR:

    def __init__(self, id= "", token="") -> None:
        if id=="":
            self.id = QR.__generate_token()
        else:
            self.id = id
        if token=="":
            self.token = QR.__generate_token()
        else:
            self.token=token
        self.qr_string, self.qr = self.__generate_qr()

    @staticmethod
    def __generate_token(num_bytes=32):
        """Generates random hex string

        Args:
            num_bytes (int, optional): Number of bytes. Defaults to 32.

        Returns:
            string: Random hex string
        """
        return secrets.token_hex(num_bytes)

    def __generate_qr(self):
        """Generates a qrcode tied to the token. Appends version to the beginning

        Args:
            token (string): token

        Returns:
            qrcode.image.pil.PilImage: QR Code object
        """
        version = str(binascii.hexlify(f"qrauth{VERSION}".encode("ascii")))
        token = version + self.id + self.token
        qr = qrcode.make(token)
        return token, qr

    @staticmethod
    def get_image(data):
        return qrcode.make(data)

    @staticmethod
    def hash(token):
        """Computes sha256 hash of a string

        Args:
            token (String): string to hash

        Returns:
            _Hash: sha256 hash of string
        """
        return hashlib.sha256(token.encode("ascii")).hexdigest()

    @staticmethod
    def validate(data):
        # check if code is valid
        try:
            _, version, data = data.split("'")
            valid_hex = all(c in set(string.hexdigits) for c in data)
            if len(data) != 128 or not valid_hex:
                raise ValueError()
            else:
                return True
        except ValueError as e:
            return False

    @staticmethod
    def getID(data):
        try:
            if not QR.validate(data):
                raise ValueError()
            _, version, data = data.split("'")
            id = data[:64]
            return id
        except ValueError:
            return None

    @staticmethod
    def get_hashed_token(data):
        _, version, data = data.split("'")
        return QR.hash(data)


class AdvancedQR(QR):
    def __init__(self):
        super().__init__()
