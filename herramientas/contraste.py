#!/usr/bin/env python3
"""
Comprobación del contraste de colores (WCAG 2.1, criterio 1.4.3, nivel AA).

Lee los colores definidos en PolestarPrototipo/App.xaml y calcula el contraste de cada
combinación texto/fondo que se usa en la interfaz. Mínimo exigido: 4,5:1 para texto normal.

Además, a título informativo, revisa los elementos gráficos que no son texto (bordes de
campos, línea de pantalla activa, anillos de foco) frente al mínimo de 3:1 del criterio 1.4.11.

Uso:  python3 herramientas/contraste.py
Sale con código 1 si alguna combinación de texto no llega a 4,5:1.
"""

import os
import sys
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_XAML = os.path.join(RAIZ, "PolestarPrototipo", "App.xaml")
NS_X = "{http://schemas.microsoft.com/winfx/2006/xaml}"

# (color del texto, color del fondo, dónde se usa)
TEXTO = [
    ("ColorTexto", "ColorFondo", "Títulos sobre el fondo de la ventana"),
    ("ColorTexto", "ColorBlanco", "Texto de tarjetas, etiquetas y campos"),
    ("ColorTextoSecundario", "ColorFondo", "Subtítulos de sección"),
    ("ColorTextoSecundario", "ColorBlanco", "Descripciones de tarjeta, ayuda del correo"),
    ("ColorAcento", "ColorBlanco", "Precios"),
    ("ColorBlanco", "ColorAcento", "Botón principal y etiqueta OFERTA"),
    ("ColorBlanco", "ColorAcentoOscuro", "Botón principal al pasar el ratón"),
    ("ColorBlanco", "ColorCabecera", "Menú"),
    ("ColorNaranja", "ColorCabecera", "Menú al pasar el ratón"),
    ("ColorTextoSobreOscuro", "ColorCabecera", "Nombre del cliente en la cabecera"),
    ("ColorTextoSobreOscuro", "ColorTexto", "Pie de página"),
    ("ColorBlanco", "ColorBanner", "Título del banner y etiqueta NUEVO"),
    ("ColorTextoSobreOscuro", "ColorBanner", "Texto del banner"),
    ("ColorNaranja", "ColorBanner", "Antetítulo CAMPAÑA DE INVIERNO"),
    ("ColorError", "ColorFondoError", "Mensaje de error"),
    ("ColorTexto", "ColorFondoError", "Texto escrito en un campo con error"),
]

# Controles desactivados: WCAG los exime, pero se comprueban igualmente (informativo)
DESACTIVADOS = [
    ("ColorTextoSecundario", "ColorBorde", "Botón desactivado (acceso bloqueado)"),
    ("ColorTextoSecundario", "ColorFondoImagen", "Campo desactivado (acceso bloqueado)"),
]

# Elementos que no son texto (criterio 1.4.11, mínimo 3:1)
NO_TEXTO = [
    ("ColorBordeCampo", "ColorBlanco", "Borde de los campos de texto"),
    ("ColorAcento", "ColorBlanco", "Borde del campo con el foco"),
    ("ColorError", "ColorFondoError", "Borde del campo con error"),
    ("ColorNaranja", "ColorCabecera", "Línea naranja de la pantalla activa"),
    ("ColorBlanco", "ColorCabecera", "Recuadro de foco del menú y del logotipo"),
    ("ColorBlanco", "ColorAcento", "Anillo de foco del botón principal"),
]


def leer_colores(ruta):
    colores = {}
    for e in ET.parse(ruta).getroot().iter():
        if e.tag.split("}")[-1] == "SolidColorBrush" and e.get(NS_X + "Key"):
            valor = e.get("Color", "").lstrip("#")
            if len(valor) == 8:          # #AARRGGBB -> se ignora la transparencia
                valor = valor[2:]
            colores[e.get(NS_X + "Key")] = valor.upper()
    return colores


def luminancia(hexa):
    """Luminancia relativa según la definición de WCAG 2.1."""
    canales = []
    for i in (0, 2, 4):
        c = int(hexa[i:i + 2], 16) / 255
        canales.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = canales
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def fmt(numero):
    return ("%.2f" % numero).replace(".", ",")


def revisar(titulo, combinaciones, colores, minimo):
    print("\n" + titulo)
    print("  %-22s %-18s %8s  %-6s %s" % ("Texto / elemento", "Fondo", "Ratio", "", "Uso"))
    fallos = 0
    for frente, fondo, uso in combinaciones:
        if frente not in colores or fondo not in colores:
            print("  FALTA el color %s o %s en App.xaml" % (frente, fondo))
            fallos += 1
            continue
        r = contraste(colores[frente], colores[fondo])
        ok = r >= minimo
        fallos += 0 if ok else 1
        print("  %-22s %-18s %6s:1  %-6s %s" % (frente, fondo, fmt(r), "OK" if ok else "FALLA", uso))
    return fallos


def main():
    if not os.path.exists(APP_XAML):
        sys.exit("No se encuentra " + APP_XAML)
    colores = leer_colores(APP_XAML)
    print("Colores leídos de App.xaml:", len(colores))
    for clave, valor in colores.items():
        print("  %-22s #%s" % (clave, valor))

    fallos = revisar("TEXTO (WCAG 1.4.3 AA, mínimo 4,5:1)", TEXTO, colores, 4.5)
    revisar("CONTROLES DESACTIVADOS (exentos; informativo, 4,5:1)", DESACTIVADOS, colores, 4.5)
    revisar("ELEMENTOS QUE NO SON TEXTO (WCAG 1.4.11, informativo, 3:1)", NO_TEXTO, colores, 3.0)

    if fallos:
        print("\n%d combinación(es) de texto no cumplen 4,5:1." % fallos)
        sys.exit(1)
    print("\nOK: todas las combinaciones de texto cumplen el nivel AA (4,5:1).")


if __name__ == "__main__":
    main()
