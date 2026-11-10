#!/usr/bin/env python3
"""
Verificación estática del proyecto WPF (no sustituye a compilar, la complementa).

Comprueba:
  1. Que todos los .xaml son XML bien formado.
  2. Que cada {StaticResource Clave} usada está definida en algún diccionario o en el propio fichero.
  3. Que cada manejador de evento declarado en XAML (Click="X", Loaded="X"...) existe en el .xaml.cs.
  4. Que cada x:Name usado desde el código subyacente (identificador.Algo) está declarado en el XAML.
  5. Que los Storyboard.TargetName apuntan a un x:Name existente en el mismo fichero.

Convención de nombres: el punto 4 reconoce los identificadores que empiezan por los
prefijos Btn (botones), Txt (textos y campos) y Zona (paneles y contenedores).

Uso:  python3 herramientas/verificar_xaml.py [ruta_del_proyecto]
Sale con código 1 si encuentra algún error.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

NS_X = "{http://schemas.microsoft.com/winfx/2006/xaml}"
PREFIJOS = ("Btn", "Txt", "Zona")

# Atributos de XAML que son eventos (se compara solo el nombre tras el último punto,
# así también se reconocen formas como Button.Click="X").
EVENTOS = {
    "Click", "Loaded", "Unloaded", "Initialized", "Activated", "Deactivated", "Closing", "Closed",
    "ContentRendered", "SizeChanged", "TextChanged", "PasswordChanged", "SelectionChanged",
    "Checked", "Unchecked", "ValueChanged", "KeyDown", "KeyUp", "PreviewKeyDown", "PreviewKeyUp",
    "MouseDown", "MouseUp", "MouseLeftButtonDown", "MouseLeftButtonUp", "MouseEnter", "MouseLeave",
    "MouseMove", "MouseWheel", "PreviewMouseDown", "PreviewMouseLeftButtonDown", "GotFocus",
    "LostFocus", "DragEnter", "DragOver", "Drop", "Completed", "Handler",
}
PLANTILLAS = ("ControlTemplate", "DataTemplate", "ItemsPanelTemplate")

RE_STATIC = re.compile(r"\{StaticResource\s+(?:ResourceKey\s*=\s*)?([^}\s]+)\s*\}")
RE_FIND = re.compile(r"(?:Try)?FindResource\(\s*\"([^\"]+)\"\s*\)")
RE_USO_NOMBRE = re.compile(r"\b((?:%s)\w*)\s*\." % "|".join(PREFIJOS))


def local(nombre):
    """Quita el espacio de nombres de una etiqueta o atributo: '{ns}Name' -> 'Name'."""
    return nombre.split("}", 1)[-1]


def quitar_comentarios_y_cadenas(codigo):
    codigo = re.sub(r"/\*.*?\*/", "", codigo, flags=re.S)
    codigo = re.sub(r"//[^\n]*", "", codigo)
    codigo = re.sub(r"@?\"(?:\\.|[^\"\\])*\"", "\"\"", codigo)
    return codigo


def recorrer(elem, dentro_plantilla=False):
    """Genera (elemento, está_dentro_de_una_plantilla)."""
    yield elem, dentro_plantilla
    es_plantilla = local(elem.tag) in PLANTILLAS
    for hijo in elem:
        yield from recorrer(hijo, dentro_plantilla or es_plantilla)


def main():
    raiz_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proyecto = sys.argv[1] if len(sys.argv) > 1 else os.path.join(raiz_repo, "PolestarPrototipo")
    if not os.path.isdir(proyecto):
        sys.exit("No existe la carpeta del proyecto: " + proyecto)

    ficheros = []
    for carpeta, subcarpetas, nombres in os.walk(proyecto):
        subcarpetas[:] = [s for s in subcarpetas if s not in ("bin", "obj", ".vs")]
        ficheros += [os.path.join(carpeta, n) for n in nombres if n.endswith(".xaml")]
    ficheros.sort()

    errores = []
    avisos = []
    print("Proyecto:", proyecto)
    print("Ficheros XAML:", ", ".join(os.path.relpath(f, proyecto) for f in ficheros) or "(ninguno)")

    # ---- 1. XML bien formado --------------------------------------------------------
    arboles = {}
    for f in ficheros:
        try:
            arboles[f] = ET.parse(f).getroot()
        except ET.ParseError as e:
            errores.append("[1] %s: XML mal formado (%s)" % (os.path.basename(f), e))

    # Claves de los diccionarios globales: App.xaml y ficheros cuya raíz es ResourceDictionary
    claves_globales = set()
    claves_locales = {}
    for f, raiz in arboles.items():
        claves = {e.get(NS_X + "Key") for e, _ in recorrer(raiz) if e.get(NS_X + "Key")}
        claves_locales[f] = claves
        if os.path.basename(f) == "App.xaml" or local(raiz.tag) == "ResourceDictionary":
            claves_globales |= claves

    for f, raiz in arboles.items():
        nombre_f = os.path.basename(f)
        texto = open(f, encoding="utf-8").read()
        definidas = claves_globales | claves_locales[f]

        # ---- 2. StaticResource ------------------------------------------------------
        for clave in sorted(set(RE_STATIC.findall(texto))):
            if clave not in definidas:
                errores.append("[2] %s: {StaticResource %s} no está definido" % (nombre_f, clave))

        # Nombres declarados (x:Name o Name), separando los de dentro de plantillas
        nombres = set()
        for e, en_plantilla in recorrer(raiz):
            n = e.get(NS_X + "Name") or e.get("Name")
            if n:
                nombres.add(n)
                if not en_plantilla and not n.startswith(PREFIJOS):
                    avisos.append("%s: x:Name=\"%s\" no usa los prefijos %s" % (nombre_f, n, "/".join(PREFIJOS)))

        # ---- 5. Storyboard.TargetName -----------------------------------------------
        for e, _ in recorrer(raiz):
            objetivo = e.get("Storyboard.TargetName")
            if objetivo and objetivo not in nombres:
                errores.append("[5] %s: Storyboard.TargetName=\"%s\" no existe" % (nombre_f, objetivo))

        # ---- 3 y 4. Código subyacente -------------------------------------------------
        manejadores = []
        for e, _ in recorrer(raiz):
            for atributo, valor in e.attrib.items():
                if local(atributo).split(".")[-1] in EVENTOS:
                    manejadores.append(valor)

        fichero_cs = f + ".cs"
        if not os.path.exists(fichero_cs):
            if manejadores:
                errores.append("[3] %s declara eventos pero no existe %s" % (nombre_f, os.path.basename(fichero_cs)))
            continue
        codigo = quitar_comentarios_y_cadenas(open(fichero_cs, encoding="utf-8").read())

        for m in sorted(set(manejadores)):
            if not re.search(r"\bvoid\s+%s\s*\(" % re.escape(m), codigo):
                errores.append("[3] %s: el manejador %s no existe en %s" % (nombre_f, m, os.path.basename(fichero_cs)))

        for usado in sorted(set(RE_USO_NOMBRE.findall(codigo))):
            if usado not in nombres:
                errores.append("[4] %s: '%s' se usa en el código pero no está declarado en el XAML"
                               % (os.path.basename(fichero_cs), usado))

        # Complemento del punto 2: FindResource("Clave") en el código
        codigo_con_cadenas = open(fichero_cs, encoding="utf-8").read()
        for clave in sorted(set(RE_FIND.findall(codigo_con_cadenas))):
            if clave not in definidas:
                errores.append("[2] %s: FindResource(\"%s\") no está definido"
                               % (os.path.basename(fichero_cs), clave))

    # ---- Resumen ---------------------------------------------------------------------
    print("Recursos definidos en diccionarios globales:", len(claves_globales))
    for a in avisos:
        print("  Aviso:", a)
    if errores:
        print("\nERRORES (%d):" % len(errores))
        for e in errores:
            print("  " + e)
        sys.exit(1)
    print("\nOK: las 5 comprobaciones se superan sin errores.")


if __name__ == "__main__":
    main()
