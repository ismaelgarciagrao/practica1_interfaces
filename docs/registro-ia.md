# Registro de uso de inteligencia artificial

## 1. Herramienta

| Campo | Valor |
|---|---|
| Herramienta | Claude, de Anthropic, en la aplicación claude.ai |
| Modelo | Claude Opus 5.5 |
| Fecha | 10 de noviembre de 2026 |
| Objetivo | Generar una primera versión del prototipo y de la documentación a partir del enunciado. |

## 2. Prompts utilizados (en orden)

| # | Prompt (literal) | Qué hizo la IA |
|---|---|---|
| 1 | `@instrucciones.md` (adjunto) Crea una primera versión de la práctica siguiendo estrictamente las instrucciones dadas en el documento adjunto. En él te doy unos objetivos, una descripción del proyecto, instrucciones a seguir, el flujo de navegación del proyecto, qué debes añadir en el registro de la IA, y cómo debe organizar el proyecto. A partir de esta primera versión, revisaré y modificaré el proyecto a mi gusto. | Leyó las instrucciones y generó el proyecto WPF completo (4 ficheros de código, `.csproj` y `.sln`), los 3 scripts de Python, las imágenes provisionales, el diagrama de navegación, la documentación con el plan de pruebas y este registro. Ejecutó `verificar_xaml.py` y `contraste.py` (ambos sin errores), probó el verificador con una copia del proyecto con errores provocados y revisó visualmente las imágenes. Empaquetó todo en un `.zip`. |

**Datos personales:** los prompts no contenían datos personales, credenciales ni información confidencial.
El documento adjunto (`instrucciones.md`) es un documento con instrucciones sobre las especificaciones de la práctica.

**Evidencia pública de la conversación:** https://claude.ai/share/27622429-5090-4ef4-8a74-3b6e552887a3.

## 3. Material generado y limitaciones

**Generado por la IA:**

- `PolestarPrototipo/App.xaml`: 15 colores y 14 estilos.
- `PolestarPrototipo/App.xaml.cs`: clase `App` vacía.
- `PolestarPrototipo/MainWindow.xaml`: cabecera, las 3 pantallas (11 tarjetas escritas a mano), pie y los 3 `Storyboard`.
- `PolestarPrototipo/MainWindow.xaml.cs`: navegación, validación del acceso, mensajes de error, bloqueo y cierre de sesión.
- `PolestarPrototipo/PolestarPrototipo.csproj` y `PolestarPrototipo.sln`.
- `PolestarPrototipo/Imagenes/`: `logo.png` y 6 `polestar_*.png` (creados ejecutando `generar_imagenes.py`).
- `herramientas/generar_imagenes.py`, `herramientas/contraste.py`, `herramientas/verificar_xaml.py`.
- `docs/navegacion.dot` (contenido del enunciado con el comando corregido) y `docs/navegacion.png`.
- `docs/DOCUMENTACION.md` (y su versión PDF), `docs/registro-ia.md`, `README.md` y `.gitignore`.
- Todos los textos de la interfaz y los datos de producto (autonomías, precios, ofertas), que son **inventados**.

**Decisiones tomadas por la IA que el alumno debe revisar:**

1. **Nombres de los colores** (`ColorFondo`, `ColorAcento`...) y a qué elemento se asigna cada uno de los 15 valores dados.
2. **Qué cuenta como fallo para el bloqueo:** solo las credenciales incorrectas; los campos vacíos o el correo mal escrito no gastan intentos.
3. **Cuenta de demostración** `cliente@polestar.es` / `Polestar2026` y nombre "Ana", escritos en el código.
4. **Cerrar sesión:** añadido aunque no aparece en el flujo del enunciado (el botón *Acceder* pasa a *Cerrar sesión*).
5. **Desbloqueo:** el bloqueo solo se quita reiniciando la aplicación.
6. **Reglas del correo** en `CorreoBienEscrito` (una `@`, punto en el dominio, sin puntos al principio/final ni dobles, sin espacios).
7. **Modelos, autonomías, precios y ofertas** del prototipo: inventados; los nombres de modelo se usan solo como contexto.
8. **Logotipo y siluetas:** diseño provisional original (anillo con punto + texto "POLESTAR"); no es el logotipo oficial.
9. **.NET 8** (`net8.0-windows`) como versión de destino, por compatibilidad con Blend 2022 y posteriores.
10. **Elementos extra** no pedidos expresamente: pie de página, atajos de teclado (Alt+letra), título de ventana que cambia, respeto de la opción de Windows de desactivar animaciones, `.sln`, `README.md` y `.gitignore`.
11. **Corrección del comando de Graphviz:** el del enunciado (`dot navegacion.dot -o navegacion.png`) genera texto; se cambió a `dot -Tpng ...`.
12. **Interpretación de "App.xml"** del enunciado como `App.xaml`.
13. **Autor** en la portada de la documentación: Ismael García Grao (añadir compañeros si los hay).

**Limitaciones:** la IA **no pudo compilar ni ejecutar** la aplicación porque trabajaba sin Windows.
Solo hizo comprobaciones automáticas del XAML y del contraste de colores.
Tampoco pudo hacer pruebas con usuarios ni publicar el repositorio: los enlaces públicos están marcados con
[COMPLETAR] en el apartado 6 de la documentación.

## 4. Revisión humana — [COMPLETAR por el alumno]

| Aspecto | Qué se comprobó y cómo | Resultado o cambios |
|---|---|---|
| Funciona: compila, se ejecuta y la navegación va bien | El proyecto compila, se ejecuta y la navegación con el ratón es correcta. | Aceptado |
| Usabilidad (pruebas del apartado 4.2 de la documentación) | Hice algunas pruebas para comprobar la facilidad de uso del prototipo y no hubo ningún problema, es sencillo encontrar cada apartado o iniciar sesión. | Aceptado |
| Accesibilidad (teclado, contraste) | Los colores se diferencian bien, y se puede navegar haciendo uso del teclado por las diferentes secciones del prototipo. | Aceptado |
| Seguridad del login | Seguridad básica, tienes 3 intentos hasta que se bloquea. Además, comprueba el formato del correo (si tiene @ o ., y la contraseña no es visible.) | Aceptado |
| Propiedad intelectual (logotipo, imágenes, datos) | En la primera version son generados por IA, así que se han revisado y modificado (menos las imágenes y el logo, que no voy a poner el original por si hubiera algún problema legal) | Modificado |
| Cumple todos los requisitos del enunciado | Se han comprobado los requisitos del enunciado y la solución creada. | Aceptado |
| Entiendo y sé explicar cada parte del XAML y del C# | En el archivo App.xaml se encuentran los colores y estilos de la aplicación. En el archivo MainWindow.xaml se encuentran las animaciones: entrada, error y banner, además de las tres partes de la pantalla: cabecera, vista general y pie de página. Aquí también se encuentran las tres secciones o pantallas, las cuales se pueden ocultar o mostrar haciendo uso de la propiedad Visibility. Si nos vamos al archivo MainWindow.xaml.cs podemos ver la algunas propiedades o datos de la cuenta de demostración, además, usamos correctamente la inicialización del prototipo y definimos funciones simples para cada funcionalidad del mismo. | Aceptado |

## 5. Contribución del alumno

| Elemento generado | Aceptado, modificado o descartado | Por qué |
|---|---|---|
| Colores y estilos (`App.xaml`) | Colores elegidos por mí, estilos generados por IA (Aceptados) | Buen contraste, colores no molestos y textos legibles fácilmente. |
| Estructura de la ventana y cabecera (`MainWindow.xaml`) | Aceptado | Cabecera bien estructurada, simple y efectiva. |
| Pantalla de Inicio (banner, Novedades, Mejor precio) | Aceptado | Pantalla simple, fácil de usar y sin distracciones. |
| Pantalla de Galería | Aceptado | Pantalla simple, fácil de usar y sin distracciones. |
| Pantalla de Acceso y gestión de errores | Modificado | Añadido un botón para mostrar u ocultar la contraseña. |
| Animaciones (3 `Storyboard`) | Aceptado | Animaciones simples, no molestan ni distraen. |
| Código de navegación y login (`MainWindow.xaml.cs`) | Aceptado | Hice varias pruebas manualmente y entiendo qué hace cada método. |
| Imágenes y `generar_imagenes.py` | Aceptado | Imágenes adecuadas y script útil para generarlas. |
| `contraste.py` | Aceptado | Script útil para comprobar contraste de colores. |
| `verificar_xaml.py` | Aceptado | Script útil para realizar comprobaciones estáticas del proyecto.  |
| Diagrama de navegación | Aceptado | Flujo de navegación correcto. |
| Documentación y plan de pruebas | Aceptado | Pruebas realizadas y con resultado correcto. Documentación clara y bien redactada. |