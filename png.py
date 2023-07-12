"""
El módulo png permite escribir archivos PNG en formato indexado.

Ejemplo de uso:

paleta = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0)
]

imagen = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

import png
png.escribir('archivo.png', paleta, imagen)
"""

import struct
import zlib

PNG_ENCABEZADO = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"

PNG_PROFUNDIDAD_BITS = 8  # 8 bits por pixel
PNG_TIPO_COLOR = 3  # indexado por paleta
PNG_COMPRESION = 0  # zlib/deflate
PNG_FILTRO = 0  # filtro basico (ninguno)
PNG_ENTRELAZADO = 0  # sin entrelazado

PNG_TIPO_FILTRO = 0  # sin filtro

def _generar_chunk(tipo, datos):
    length = struct.pack("!I", len(datos))
    crc = zlib.crc32(tipo + datos)
    return length + tipo + datos + struct.pack("!I", crc)


def _generar_ihdr(ancho, alto):
    datos = struct.pack("!IIBBBBB",
        ancho,
        alto,
        PNG_PROFUNDIDAD_BITS,
        PNG_TIPO_COLOR,
        PNG_COMPRESION,
        PNG_FILTRO,
        PNG_ENTRELAZADO
    )
    return _generar_chunk(b"IHDR", datos)


def _generar_plte(paleta):
    datos = b""
    for r, g, b in paleta:
        datos += struct.pack("!BBB", r, g, b)
    return _generar_chunk(b"PLTE", datos)


def _generar_idat(matriz):
    datos = b""
    for fila in matriz:
        datos += bytes([PNG_TIPO_FILTRO] + fila)
    return _generar_chunk(b"IDAT", zlib.compress(datos))


def _generar_iend():
    return _generar_chunk(b"IEND", b"")

def escribir(ruta, paleta, imagen):
    """
    Escribe un archivo en formato PNG indexado.

    Argumentos:
        ruta: la ruta del archivo a escribir (se sobreescribe si ya existe)
        paleta: una lista de tuplas (r, g, b), siendo r, g, b números entre 0 y 255 inclusive.
        imagen: una matriz (lista de filas) de números enteros; cada número representa un pixel
                de la imagen, y debe ser un índice válido de la `paleta`.
    """
    assert len(set(len(fila) for fila in imagen)) == 1, 'todas las filas deben ser de la misma longitud'

    ihdr = _generar_ihdr(len(imagen[0]), len(imagen))
    plte = _generar_plte(paleta)
    idat = _generar_idat(imagen)
    iend = _generar_iend()

    with open(ruta, 'wb') as salida:
        salida.write(PNG_ENCABEZADO)
        salida.write(ihdr)
        salida.write(plte)
        salida.write(idat)
        salida.write(iend)
