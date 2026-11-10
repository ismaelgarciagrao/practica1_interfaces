#!/usr/bin/env python3
"""
Genera las imágenes PNG del prototipo (carpeta PolestarPrototipo/Imagenes):
  - logo.png: logotipo PROVISIONAL (símbolo geométrico original + texto). No es el logotipo oficial.
  - polestar*.png: siluetas de coche ORIGINALES y genéricas, una por color de carrocería.

Son marcadores de posición: en la versión final se sustituirían por el logotipo y las fotos
oficiales de la marca, respetando sus condiciones de uso. Basta con reemplazar los ficheros.

Requiere Python 3 y Pillow. Uso: python3 herramientas/generar_imagenes.py
Tipografía del logotipo: DejaVu Sans ExtraLight (licencia libre Bitstream Vera / DejaVu).
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta Pillow. Instálalo con:  pip install pillow")

# Carpeta de salida: <raíz del repositorio>/PolestarPrototipo/Imagenes
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "PolestarPrototipo", "Imagenes")

ESCALA = 4  # se dibuja 4 veces más grande y se reduce al final (bordes suaves)

# Colores de la paleta de App.xaml que se usan en las imágenes
NARANJA = (0xE8, 0x86, 0x2A, 255)  # ColorNaranja
BLANCO = (0xFF, 0xFF, 0xFF, 255)   # ColorBlanco


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def bezier(p0, p1, p2, pasos=24):
    """Puntos de una curva de Bézier cuadrática (p0 -> p2 con control p1)."""
    puntos = []
    for i in range(pasos + 1):
        t = i / pasos
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        puntos.append((x, y))
    return puntos


def escalar(puntos):
    return [(x * ESCALA, y * ESCALA) for x, y in puntos]


def oscurecer(color, factor):
    return tuple(int(c * factor) for c in color[:3]) + (255,)


def buscar_fuente(nombre, tam):
    """Busca la tipografía en las rutas habituales de Linux, Windows y macOS."""
    rutas = [
        "/usr/share/fonts/truetype/dejavu/" + nombre,
        "/usr/share/fonts/dejavu/" + nombre,
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", nombre),
        os.path.expanduser("~/Library/Fonts/" + nombre),
        nombre,
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tam)
    print("  Aviso: no se encontró", nombre, "-> se usa DejaVuSans.ttf de Pillow")
    return ImageFont.truetype("DejaVuSans.ttf", tam)


# ----------------------------------------------------------------------------
# Logotipo provisional
# ----------------------------------------------------------------------------
def generar_logo():
    ancho, alto = 520, 96
    img = Image.new("RGBA", (ancho * ESCALA, alto * ESCALA), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Símbolo original: una órbita (anillo) con una "estrella polar" (punto) encima.
    cx, cy, r = 48, 48, 30
    d.ellipse(escalar([(cx - r, cy - r), (cx + r, cy + r)]), outline=NARANJA, width=5 * ESCALA)
    # Punto blanco sobre el anillo, arriba a la derecha
    px, py, pr = cx + 21, cy - 21, 9
    d.ellipse(escalar([(px - pr, py - pr), (px + pr, py + pr)]), fill=BLANCO)
    # Línea de horizonte que atraviesa el anillo
    d.line(escalar([(cx - r - 6, cy + 6), (cx + r + 6, cy + 6)]), fill=NARANJA, width=3 * ESCALA)

    # Texto con espaciado entre letras
    fuente = buscar_fuente("DejaVuSans-ExtraLight.ttf", 44 * ESCALA)
    x = 104 * ESCALA
    for letra in "POLESTAR":
        caja = d.textbbox((0, 0), letra, font=fuente)
        d.text((x, 22 * ESCALA - caja[1] + 4 * ESCALA), letra, font=fuente, fill=BLANCO)
        x += (caja[2] - caja[0]) + 12 * ESCALA

    img = img.resize((ancho, alto), Image.LANCZOS)
    img.save(os.path.join(SALIDA, "logo.png"))
    print("  logo.png")


# ----------------------------------------------------------------------------
# Siluetas de coche (vista lateral, mirando a la derecha)
# ----------------------------------------------------------------------------
CARROCERIAS = {
    # techo: altura del techo; cintura: línea bajo las ventanillas;
    # libre: altura libre al suelo; rueda: radio; cabina: (inicio, techo_ini, techo_fin, parabrisas)
    "berlina": dict(techo=104, cintura=160, libre=34, rueda=40, cabina=(105, 205, 340, 445)),
    "suv":     dict(techo=82,  cintura=148, libre=44, rueda=45, cabina=(70, 150, 380, 445)),
    "coupe":   dict(techo=92,  cintura=152, libre=40, rueda=44, cabina=(85, 190, 330, 445)),
    "gt":      dict(techo=112, cintura=165, libre=30, rueda=40, cabina=(110, 220, 320, 430)),
}

SUELO = 262


def dibujar_coche(color, tipo):
    p = CARROCERIAS[tipo]
    ancho, alto = 600, 300
    capa_sombra = Image.new("RGBA", (ancho * ESCALA, alto * ESCALA), (0, 0, 0, 0))
    ImageDraw.Draw(capa_sombra).ellipse(
        escalar([(55, SUELO - 10), (545, SUELO + 10)]), fill=(0, 0, 0, 55))

    capa = Image.new("RGBA", (ancho * ESCALA, alto * ESCALA), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    trasera, delantera = 40, 560
    bajo = SUELO - p["libre"]
    cintura, techo = p["cintura"], p["techo"]
    rueda_t, rueda_d = 150, 455
    r = p["rueda"]
    contorno = oscurecer(color, 0.6)

    # Cuerpo inferior (de la trasera al morro)
    cuerpo = []
    cuerpo += bezier((trasera + 10, bajo), (trasera - 4, bajo - 10), (trasera, cintura + 20))
    cuerpo += bezier((trasera, cintura + 20), (trasera + 2, cintura), (trasera + 30, cintura - 2))
    cuerpo += [(delantera - 70, cintura + 4)]
    cuerpo += bezier((delantera - 70, cintura + 4), (delantera - 5, cintura + 12), (delantera, cintura + 45))
    cuerpo += bezier((delantera, cintura + 45), (delantera + 2, bajo - 4), (delantera - 12, bajo))
    d.polygon(escalar(cuerpo), fill=color, outline=contorno, width=2 * ESCALA)

    # Cabina (parte acristalada)
    c0, c1, c2, c3 = p["cabina"]
    cabina = []
    cabina += bezier((c0, cintura + 2), (c1 - 40, techo - 2), (c1, techo))
    cabina += [(c2, techo)]
    cabina += bezier((c2, techo), (c2 + 50, techo + 2), (c3, cintura + 4))
    d.polygon(escalar(cabina), fill=color, outline=contorno, width=2 * ESCALA)

    # Ventanillas: la misma forma, un poco más pequeña, en color cristal
    cristal = (40, 48, 56, 255)
    ventana = []
    ventana += bezier((c0 + 22, cintura - 3), (c1 - 30, techo + 6), (c1 + 4, techo + 8))
    ventana += [(c2 - 2, techo + 8)]
    ventana += bezier((c2 - 2, techo + 8), (c2 + 40, techo + 10), (c3 - 22, cintura - 1))
    d.polygon(escalar(ventana), fill=cristal)
    # Pilar central
    medio = (c1 + c2) / 2 + 10
    d.rectangle(escalar([(medio - 5, techo + 4), (medio + 5, cintura)]), fill=color)

    # Línea de luz delantera y trasera
    d.line(escalar([(delantera - 42, cintura + 18), (delantera - 8, cintura + 26)]),
           fill=(250, 250, 245, 255), width=4 * ESCALA)
    d.line(escalar([(trasera + 2, cintura + 12), (trasera + 26, cintura + 8)]),
           fill=(200, 40, 30, 255), width=4 * ESCALA)

    # Pasos de rueda (se "recortan" haciendo transparente esa zona) y ruedas
    for cx in (rueda_t, rueda_d):
        cy = SUELO - r
        hueco = r + 7
        d.ellipse(escalar([(cx - hueco, cy - hueco), (cx + hueco, cy + hueco)]), fill=(0, 0, 0, 0))
        d.ellipse(escalar([(cx - r, cy - r), (cx + r, cy + r)]), fill=(28, 28, 30, 255))
        llanta = r * 0.62
        d.ellipse(escalar([(cx - llanta, cy - llanta), (cx + llanta, cy + llanta)]),
                  fill=(150, 152, 155, 255), outline=(90, 92, 95, 255), width=2 * ESCALA)
        buje = r * 0.18
        d.ellipse(escalar([(cx - buje, cy - buje), (cx + buje, cy + buje)]), fill=(60, 60, 62, 255))

    img = Image.alpha_composite(capa_sombra, capa)
    return img.resize((ancho, alto), Image.LANCZOS)


# nombre de fichero -> (color de carrocería, tipo de carrocería)
COCHES = {
    "polestar_plata.png":  ((168, 172, 176, 255), "berlina"),
    "polestar_negro.png":  ((38, 39, 42, 255), "berlina"),
    "polestar_azul.png":   ((44, 66, 98, 255), "suv"),
    "polestar_blanco.png": ((246, 246, 244, 255), "coupe"),
    "polestar_cobre.png":  ((152, 96, 60, 255), "gt"),
    "polestar_verde.png":  ((62, 84, 72, 255), "suv"),
}


def main():
    os.makedirs(SALIDA, exist_ok=True)
    print("Generando imágenes en", SALIDA)
    generar_logo()
    for nombre, (color, tipo) in COCHES.items():
        dibujar_coche(color, tipo).save(os.path.join(SALIDA, nombre))
        print("  " + nombre)
    print("Hecho.")


if __name__ == "__main__":
    main()
