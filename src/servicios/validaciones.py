"""Validaciones reutilizables por los servicios (textos, teléfono, correo, NIT, código).

Todas devuelven el valor ya limpio (sin espacios de más) o lanzan ReglaDominioError
con un mensaje claro para el usuario."""
import re

from dominio.excepciones.regla_dominio_error import ReglaDominioError

_LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
_HAY_LETRA = re.compile("[" + _LETRAS + "]")
_SOLO_LETRAS = re.compile("^[" + _LETRAS + "][" + _LETRAS + " .'\\-]*$")
_ESPACIOS = re.compile(r"[ \t]+")

# Teléfono colombiano de 10 dígitos: celular (empieza por 3) o fijo con indicativo (60 + 8).
# Si quieren aceptar cualquier número de 10 dígitos, cambien esta expresión por r"^\d{10}$".
_TELEFONO = re.compile(r"^(3[0-9]{9}|60[0-9]{8})$")
_NIT = re.compile(r"^[0-9]{9,10}(-[0-9])?$")
_CORREO = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")
_CODIGO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-_.]*$")
_SOLO_NUMEROS = re.compile(r"^[0-9]+$")


def _minuscula(etiqueta):
    return etiqueta[0].lower() + etiqueta[1:]


def limpiar(valor, multilinea=False):
    """Quita espacios sobrantes. En una línea también elimina los saltos de línea."""
    bruto = (valor or "").replace("\r", "")
    if not multilinea:
        return " ".join(bruto.split())
    lineas = [_ESPACIOS.sub(" ", linea).strip() for linea in bruto.split("\n")]
    return "\n".join(linea for linea in lineas if linea)


def texto(valor, etiqueta, minimo=2, maximo=200, requiere_letra=True, multilinea=False):
    """Texto obligatorio. 'etiqueta' lleva el artículo: «El nombre», «La dirección»."""
    limpio = limpiar(valor, multilinea)
    if not limpio:
        raise ReglaDominioError(f"Escribe {_minuscula(etiqueta)}.")
    if len(limpio) < minimo:
        raise ReglaDominioError(f"{etiqueta} debe tener al menos {minimo} caracteres.")
    if len(limpio) > maximo:
        raise ReglaDominioError(f"{etiqueta} admite máximo {maximo} caracteres.")
    if requiere_letra and not _HAY_LETRA.search(limpio):
        raise ReglaDominioError(f"{etiqueta} debe contener letras, no solo números o símbolos.")
    return limpio


def solo_letras(valor, etiqueta, minimo=3, maximo=50):
    """Texto obligatorio que solo admite letras, espacios, punto, guion y apóstrofo."""
    limpio = texto(valor, etiqueta, minimo, maximo, requiere_letra=False)
    if not _SOLO_LETRAS.match(limpio):
        raise ReglaDominioError(
            f"{etiqueta} solo admite letras, espacios, punto y guion (sin números).")
    return limpio


def seleccion(valor, etiqueta):
    """Una opción de una lista desplegable debe estar elegida."""
    if valor is None:
        raise ReglaDominioError(f"Selecciona {_minuscula(etiqueta)}.")
    return valor


def telefono(valor):
    """Obligatorio, exactamente 10 dígitos. Acepta espacios o guiones al escribirlo."""
    bruto = (valor or "").strip()
    if not bruto:
        raise ReglaDominioError("Escribe el teléfono.")
    numero = re.sub(r"[ \-]", "", bruto)
    if not _SOLO_NUMEROS.match(numero):
        raise ReglaDominioError("El teléfono solo debe tener números (sin letras ni símbolos).")
    if len(numero) != 10:
        raise ReglaDominioError(
            f"El teléfono debe tener exactamente 10 dígitos (tiene {len(numero)}).")
    if not _TELEFONO.match(numero):
        raise ReglaDominioError(
            "El teléfono debe empezar por 3 (celular, ej. 3101234567) "
            "o por 60 (fijo con indicativo, ej. 6013456789).")
    return numero


def correo(valor):
    """Obligatorio, sin espacios, con formato usuario@dominio.ext. Se guarda en minúsculas."""
    limpio = (valor or "").strip().lower()
    if not limpio:
        raise ReglaDominioError("Escribe el correo electrónico.")
    if len(limpio) > 100:
        raise ReglaDominioError("El correo admite máximo 100 caracteres.")
    if not _CORREO.match(limpio):
        raise ReglaDominioError(
            "El correo no tiene un formato válido (ej. ventas@empresa.com), sin espacios.")
    return limpio


def nit(valor):
    """9 o 10 dígitos y, opcionalmente, guion con el dígito de verificación."""
    limpio = (valor or "").strip().replace(".", "").replace(" ", "")
    if not limpio:
        raise ReglaDominioError("Escribe el NIT.")
    if not _NIT.match(limpio):
        raise ReglaDominioError(
            "El NIT debe tener 9 o 10 dígitos y, si quieres, el guion con el dígito "
            "de verificación (ej. 900123456-7).")
    return limpio


def codigo(valor, etiqueta="El código", minimo=2, maximo=30):
    """Código sin espacios: letras, números, guion, guion bajo y punto. Se guarda en mayúsculas."""
    limpio = (valor or "").strip().upper()
    if not limpio:
        raise ReglaDominioError(f"Escribe {_minuscula(etiqueta)}.")
    if len(limpio) < minimo:
        raise ReglaDominioError(f"{etiqueta} debe tener al menos {minimo} caracteres.")
    if len(limpio) > maximo:
        raise ReglaDominioError(f"{etiqueta} admite máximo {maximo} caracteres.")
    if not _CODIGO.match(limpio):
        raise ReglaDominioError(
            f"{etiqueta} solo admite letras, números, guion, guion bajo y punto, sin espacios.")
    return limpio
