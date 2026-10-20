"""Cifrado de contraseñas con PBKDF2 (hashlib, sin librerías externas)."""
import hashlib
import hmac
import os

ITERACIONES = 200_000


class SeguridadServicio:

    def cifrar(self, contrasena):
        """Devuelve 'pbkdf2$iteraciones$salt$hash' (cabe en VARCHAR(255))."""
        salt = os.urandom(16)
        h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), salt, ITERACIONES)
        return f"pbkdf2${ITERACIONES}${salt.hex()}${h.hex()}"

    def verificar(self, contrasena, guardado):
        """Compara una contraseña escrita con el hash guardado en la base."""
        try:
            _, iteraciones, salt_hex, hash_hex = guardado.split("$")
            h = hashlib.pbkdf2_hmac(
                "sha256", contrasena.encode("utf-8"),
                bytes.fromhex(salt_hex), int(iteraciones),
            )
            return hmac.compare_digest(h.hex(), hash_hex)
        except ValueError:
            return False
