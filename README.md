# DataFlow AI

Prototipo de aplicación educativa para explicar errores frecuentes de SQL y ETL en español.

## Funciones actuales (versión 0.1)
- Entrada de consultas o mensajes de error ficticios.
- Análisis local por reglas: sintaxis SELECT, división por cero y referencias a columnas inexistentes.
- Explicación y sugerencias con advertencia de limitaciones.

**Esta versión no utiliza IA**. Se añadirá Gemini en una iteración posterior. No se ejecutan consultas ni se almacenan los textos introducidos.

## Ejecutar

Desde PowerShell, sitúate en la carpeta `DataFlow_AI` que contiene `app.py`.
Para una instalación nueva, utiliza Python 3.12 (la versión usada para validar
este proyecto) y crea un entorno virtual:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Si dispones de `python` en lugar de `py`, puedes crear el entorno con
`python -m venv .venv`. Si ninguno está disponible, instala Python 3.12 o
ejecuta el comando con la ruta completa de tu intérprete.

Con el entorno ya preparado, inicia la aplicación:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Abre <http://127.0.0.1:8501> y detén el servidor con `Ctrl+C`.
No es necesario activar el entorno ni cambiar la política de ejecución de
PowerShell. Si el puerto está ocupado, añade `--server.port 8502` y abre ese
puerto en el navegador.

En Linux/macOS, desde la misma carpeta y con Python 3.12 instalado:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

La configuración `.streamlit/config.toml` desactiva las estadísticas de uso y
la apertura automática del navegador. No se necesitan claves de API ni servicios
externos para ejecutar esta versión; la instalación inicial sí descarga paquetes.

`requirements.txt` contiene solo `streamlit==1.66.1`, la dependencia directa de
producción verificada. Sus dependencias transitivas las resuelve pip según el
sistema operativo. Se utiliza Python 3.12 para el entorno local y el despliegue.
No se necesitan `packages.txt`, controladores SQL ni paquetes de Gemini.

`requirements-local.lock.txt` es una captura opcional del entorno Windows con
Python 3.12; no es el archivo de instalación de Community Cloud ni garantiza
compatibilidad con otros sistemas. Para reproducir ese entorno local:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-local.lock.txt
```

## Probar

Desde la misma carpeta y con las dependencias instaladas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Incluye pruebas de reglas locales, límites de entrada y flujo de interfaz con
[`AppTest` de Streamlit](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
También comprueba las exclusiones de `.gitignore` usando un repositorio temporal
local; esa prueba se omite si Git no está instalado. No necesita pytest.
En Linux/macOS, ejecuta `.venv/bin/python -m unittest discover -s tests -v`.
Para comprobar solo el analizador, sin instalar Streamlit:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_analyzer.py -v
```

## Alcance del análisis local

El ejemplo «Columna inexistente» incluye un mensaje ficticio del motor: sin
acceso al esquema no es posible determinar si una columna de una consulta existe.
Las reglas buscan patrones de texto, no interpretan SQL completo ni distinguen
todos los comentarios, cadenas o dialectos. Pueden producir falsos positivos y
no detectan todos los errores. Gemini sigue reservado para una futura iteración.
Los textos solo permanecen en memoria durante la sesión de Streamlit; la aplicación
no los registra, guarda en archivos ni envía a servicios de análisis.

## Preparar el repositorio de GitHub

Los siguientes pasos son manuales. Preparar estos archivos no crea un repositorio
remoto ni publica la aplicación.

Utiliza la carpeta interior `DataFlow_AI` como raíz del repositorio, con esta
estructura (los nombres respetan mayúsculas y minúsculas en Linux):

```text
DataFlow_AI/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── app.py
├── analyzer.py
├── requirements.txt
├── requirements-local.lock.txt
├── README.md
├── AGENTS.md
├── especificacion.md
├── REVISION.md
└── tests/
    ├── test_analyzer.py
    ├── test_app.py
    └── test_deployment.py
```

1. Ejecuta las pruebas y `pip check` con los comandos anteriores.
2. Comprueba Git con `git --version`, `git config --get user.name` y
   `git config --get user.email`. Si falta la identidad, configúrala con
   `git config --global user.name "Tu nombre"` y
   `git config --global user.email "Tu correo de GitHub"`.
3. Desde la carpeta interior `DataFlow_AI`, si todavía no hay repositorio,
   ejecuta `git init -b main`.
4. Ejecuta `git status --short --ignored` para revisar exclusiones. `.venv`,
   cachés, temporales, credenciales y `.streamlit/secrets.toml` deben quedar
   excluidos. `.streamlit/config.toml` debe incluirse. Los archivos `.env.example`
   y `.env.template`, si los creas, solo deben contener valores de ejemplo.
5. Prepara los archivos con `git add .`, revisa `git diff --cached --stat` y
   `git diff --cached`, y crea el commit con
   `git commit -m "Prepara DataFlow AI 0.1 para Streamlit Community Cloud"`.
   `.gitignore` no deja de seguir archivos que ya estuvieran versionados:
   comprueba `git ls-files` si partes de un repositorio existente.
6. Cuando decidas publicarlo, crea un repositorio vacío en GitHub, sin añadir
   allí otro README o `.gitignore`. Configura su URL real con
   `git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git`
   y ejecuta `git push -u origin main`. Estos comandos remotos se muestran
   únicamente para que los ejecutes cuando autorices la publicación.

## Desplegar en Streamlit Community Cloud

1. Accede a [Streamlit Community Cloud](https://share.streamlit.io/) con tu cuenta
   y conecta GitHub, concediendo acceso al repositorio que quieras desplegar.
2. Crea una aplicación y selecciona el repositorio, la rama `main` y el archivo
   principal `app.py`. Si elegiste otra rama, selecciona su nombre real.
3. En las opciones avanzadas, selecciona **Python 3.12**. Deja vacíos los
   secretos: la versión 0.1 no requiere claves ni Gemini.
4. Inicia el despliegue. Cloud debe instalar las dependencias de `requirements.txt`;
   no selecciones `requirements-local.lock.txt` ni subas `.venv`.
5. Revisa los registros de instalación y arranque. La configuración incluida no
   fija puerto, dirección de red ni rutas del equipo local; deja que Cloud los
   gestione. El argumento `--server.address 127.0.0.1` es solo para uso local.
6. Abre la URL pública y verifica: entrada vacía con mensaje legible; los tres
   ejemplos con sus resultados; y `SELECT nombre FROM empleados;` con revisión
   general y advertencia de incertidumbre. Prueba también el modo ETL.
7. Si la entrega lo requiere, copia la URL pública en la ficha de Blackboard.

Si subes la carpeta exterior en vez de usar la estructura recomendada, el archivo
principal será `DataFlow_AI/app.py`. Para evitar ambigüedades con las rutas de
configuración, utiliza preferentemente la carpeta interior como raíz.

Las comprobaciones automatizadas se ejecutan localmente en Windows con Python
3.12; la compatibilidad Linux se ha revisado en el código y la configuración,
pero debe confirmarse con el despliegue real. No se han realizado operaciones
remotas durante esta preparación.

## Seguridad
No usar datos personales, consultas confidenciales, contraseñas ni código de clientes. No publicar claves de API.
