# Revisión local de DataFlow AI

Fecha: 28 de octubre de 2026.

## Documentación y alcance

Se revisaron `README.md`, `AGENTS.md`, `especificacion.md`, ambos módulos Python,
las pruebas, las dependencias y los archivos de configuración del proyecto.
Se mantienen explicación, posibles soluciones y consejos de mejora mediante
reglas locales. No se ha incorporado Gemini, ejecución de SQL, conexión a bases
de datos ni almacenamiento de entradas. `AGENTS.md` y `especificacion.md`
permanecen sin modificaciones.

## Problemas corregidos

- El analizador recortaba espacios antes de validar la longitud, permitiendo
  entradas originales de más de 4000 caracteres. Ahora valida el texto completo
  y comparte el límite con la interfaz mediante `MAX_INPUT_CHARS`.
- La regla `/0` confundía denominadores como `0.5` con cero. Ahora comprueba
  literales numéricos cero completos, incluidos `0.0`, `.0`, ceros con signo y
  notación científica, sin ejecutar ni interpretar consultas.
- El ejemplo «Columna inexistente» era una consulta que no podía diagnosticarse
  sin conocer el esquema. Ahora contiene un mensaje ficticio `Unknown column`.
- El modo ETL ignoraba el ejemplo seleccionado. La selección ahora carga el
  texto en ambos modos mediante un callback del widget; el usuario puede editarlo
  antes de analizarlo y volver a una entrada vacía al elegir texto propio.
- La revisión general sugería conectar Gemini aunque esta versión no lo ofrece.
  Ahora proporciona consejos aplicables al análisis local y conserva el aviso
  de que no detectar patrones no garantiza que la consulta sea correcta.

## Preparación local y dependencias

Python no estaba en el PATH. Se utilizó una instalación existente de Python 3.12
para crear `.venv` en la carpeta del proyecto. No se modificó el PATH ni se
instalaron paquetes globales. Este entorno depende de esa instalación de Python;
en otro equipo debe recrearse siguiendo el README.

En la preparación inicial se instaló Streamlit 1.66.1 con Python 3.12.14,
partiendo de `streamlit>=1.35,<2`; `requirements-local.lock.txt`
registra las versiones instaladas para reproducir este entorno en Windows con
Python 3.12. La comprobación se realizó con estas versiones concretas, sin
probar todas las versiones del rango permitido.

La configuración local desactiva las estadísticas de uso y la apertura automática
del navegador. El comando documentado limita el servidor a `127.0.0.1`.
El README incluye creación del entorno, instalación, pruebas, arranque y solución
para un puerto ocupado. `.gitignore` ya excluía `.venv`, secretos y cachés.

## Verificaciones realizadas

- Antes de modificar el código: 6 pruebas originales correctas.
- Las nuevas pruebas del analizador reprodujeron los errores antes de corregirlos.
- Después de los cambios: `python -m unittest discover -s tests -v`, 16 pruebas
  correctas (12 del analizador y 4 de interfaz con AppTest de Streamlit).
- Casos cubiertos: entradas vacías, límite exacto y exceso de caracteres con
  espacios, ejemplos, mensajes ETL, ceros y denominadores no nulos, edición de
  ejemplos, carga de ejemplos en ambos modos y vuelta a texto propio.
- `python -m pip check`: sin requisitos incompatibles.
- Compilación de los módulos y pruebas con `compileall`: correcta.
- Arranque real con `python -m streamlit run app.py --server.address 127.0.0.1`.
- `GET /_stcore/health`: HTTP 200, `ok`; `GET /`: HTTP 200.

Las pruebas de interfaz usan
[AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest),
que ejecuta la aplicación y simula la interacción con sus widgets. No se realizó
una revisión visual manual en navegador. AppTest emitió avisos de contexto del
hilo principal, sin excepciones de aplicación ni fallos de pruebas.

## Limitaciones que siguen vigentes

Las reglas no son un parser SQL: pueden coincidir con texto en comentarios o
cadenas y no cubren todos los dialectos, expresiones o errores ETL. Las referencias
a identificadores se reconocen mediante mensajes de error; no se verifica ningún
esquema. El selector de tipo de entrada no añade reglas específicas por motor.
Estas limitaciones se conservan dentro del alcance de la versión 0.1 y se
documentan sin garantizar la corrección de las sugerencias.

La carpeta recibida no contiene metadatos Git, por lo que no se creó ningún commit.

## Preparación posterior para GitHub y Community Cloud

Se conserva el funcionamiento de la versión 0.1. Se revisaron `app.py` y
`.streamlit/config.toml` sin necesidad de modificarlos: no contienen rutas
absolutas, importaciones exclusivas de Windows ni ajustes de red que bloqueen
el despliegue en Cloud. El código utiliza importaciones con la capitalización
correcta; las pruebas localizan la aplicación con `pathlib`.

Cambios de esta preparación:

- `.gitignore`: amplía la exclusión de entornos, cachés, temporales y credenciales;
  conserva `.streamlit/config.toml` y plantillas `.env` sin valores reales.
- `requirements.txt`: fija `streamlit==1.66.1`, la versión ya instalada y probada.
  Es la única dependencia directa de producción. No se añaden paquetes de pruebas
  ni Gemini. Sus metadatos requieren Python >=3.11; el despliegue documentado
  utiliza Python 3.12. Las dependencias transitivas se resuelven según la plataforma.
- `analyzer.py`: la revisión general expresa que las reglas no permiten confirmar
  errores ni corrección y recomienda consultar la documentación de SQL o ETL,
  eliminando la referencia a revisar un error ficticio. No cambian las reglas.
- `tests/test_analyzer.py` y `tests/test_app.py`: comprueban el mensaje general
  y su presentación, manteniendo los casos anteriores.
- `tests/test_deployment.py`: nueva prueba con Git en un repositorio temporal
  para verificar qué archivos se excluirían o conservarían. Usa separadores nulos
  para evitar diferencias de finales de línea entre Windows y Linux.
- `README.md`: añade comandos para Linux/macOS y pasos manuales para revisar,
  crear y subir el repositorio y desplegar `app.py` con Python 3.12. Distingue
  `requirements.txt` del snapshot opcional de dependencias locales Windows.
- `REVISION.md`: elimina la ruta absoluta del intérprete local y registra esta
  preparación. La ruta anterior solo aparecía en documentación; no era una
  dependencia del código.

Resultado actualizado: **19 pruebas correctas**, sin omisiones (13 del analizador,
5 de interfaz y 1 de exclusiones de Git). `pip check` no detecta incompatibilidades.
El archivo de configuración se ha leído correctamente con `tomllib`.
Las tres pruebas manuales previas fueron comunicadas por el usuario; no se han
repetido como parte de esta preparación.

Git está instalado y tiene nombre y correo configurados. La carpeta del proyecto
sigue sin repositorio inicializado. No se ha creado un commit, configurado un
remoto, subido archivos, publicado la aplicación ni realizado operaciones remotas.
La revisión Linux es estática: la instalación y ejecución reales en Community Cloud
deben confirmarse al desplegar. Los pasos manuales completos están en el README.
