# Registro de revisiones de DataFlow AI — v0.2

Fecha: 28 de octubre de 2026.

Las secciones siguientes conservan el historial de preparación; sus referencias
a comprobaciones pendientes o cambios aún locales describen aquel momento.
La sección final registra la validación de release 0.2 y prevalece sobre los
estados históricos. El estado de publicación y hash se consultan en Git.

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

## Integración opcional de Gemini — preparación local

Fecha: 28 de octubre de 2026. El usuario informa de que la versión 0.1 ya está
publicada en GitHub y Community Cloud. Esta sección describe cambios posteriores
preparados únicamente en el equipo local; no se han subido ni desplegado.

Se leyeron `AGENTS.md`, `especificacion.md`, `README.md` y el código antes de
modificarlo. Las 19 pruebas anteriores pasaron al comenzar. `analyzer.py` y
`especificacion.md` permanecen intactos: las reglas, resultados y límites del modo
local no cambian. El modo local continúa seleccionado por defecto y no requiere
clave, importación del SDK ni conexión a Google para analizar.

### Archivos de la integración

- Nuevo `gemini_analyzer.py`: resolución de `GEMINI_API_KEY` con prioridad de
  secretos de Streamlit sobre el entorno; cliente por petición y cierre automático;
  instrucciones de sistema en español separadas de los datos no confiables; salida
  JSON validada con observaciones, hipótesis, correcciones, recomendaciones y límites.
  No se ofrecen herramientas, funciones, búsquedas ni ejecución de SQL o código.
  Se fija el endpoint oficial de Gemini Developer API y se desactiva el backend
  empresarial para evitar depender de otra configuración local del SDK.
- `app.py`: selector explícito entre reglas locales y Gemini, confirmación previa
  al envío con aviso de privacidad/cuota/coste y revocación al editar datos, cambiar
  el ejemplo o los selectores de modo. Resultado Gemini en texto plano, advertencia
  fija sobre incertidumbre, errores saneados y recuperación local mediante botón
  sin reenviar a Google ni ocultar el fallo.
- `requirements.txt`: añade `google-genai==2.23.0` y `httpx==0.28.1`, utilizado
  directamente para distinguir errores de transporte. Conserva Streamlit 1.66.1.
  No se instala `google-generativeai`. `requirements-local.lock.txt` se actualiza
  para reflejar el entorno Windows verificado; no es el archivo de Cloud.
- Nuevos `tests/test_gemini_analyzer.py` y `tests/test_app_gemini.py`: clientes
  simulados y transporte HTTP mock; nunca claves reales ni llamadas a Google.
  `tests/test_app.py` comprueba además que las pruebas del modo local no crean
  ningún cliente Gemini. `tests/test_deployment.py` conserva los nuevos módulos
  publicables y sigue verificando la exclusión de secretos.
- `AGENTS.md`: documenta restricciones de llamadas reales, permisos, mocks,
  entradas no confiables, salida plana, costes y recuperación local.
- `README.md`: actualiza dependencias y alcance, documenta configuración privada
  local y en Secrets de Community Cloud, consentimiento, límites, privacidad y
  pasos para las pruebas manuales. `REVISION.md` registra los resultados.

### Verificación oficial del modelo y SDK

Con autorización explícita del usuario se consultaron documentación oficial y
PyPI y se descargaron dependencias en `.venv`:

- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash):
  identificador estable `gemini-3.8-flash`, con salida estructurada y nivel de
  pensamiento `low`. No se usan identificadores preview, aliases latest ni modelos
  retirados. Disponibilidad efectiva y acceso de este proyecto pendientes de prueba real.
- [SDK oficial Python](https://googleapis.github.io/python-genai/) y
  [google-genai en PyPI](https://pypi.org/project/google-genai/): versión 2.23.0.
  Se contrastaron las opciones con los tipos del SDK instalado.
- [Respuestas estructuradas](https://ai.google.dev/gemini-api/docs/structured-output)
  y [gestión de errores](https://ai.google.dev/gemini-api/docs/troubleshooting).

### Límites y errores

Se valida el máximo de 4000 caracteres originales antes de crear el cliente. Se
configura timeout HTTP de 20 000 ms, un solo intento sin reintentos y máximo de
4096 tokens de salida. Se limita el JSON recibido a 20 000 caracteres y se validan
campos y longitudes. Una finalización por límite de tokens o bloqueo se rechaza,
incluso si el texto contiene JSON válido. El timeout es del transporte HTTP y no
constituye un plazo total exacto para todo el procesamiento.

Se distinguen clave ausente, configuración de secretos inválida, errores de
autenticación/permisos/configuración (400/401/403), cuota (429), modelo inaccesible
(404), timeout (408/504 o transporte), conexión, servicio y respuestas vacías,
bloqueadas o mal formadas. No se muestran ni registran detalles originales de las
excepciones. Los códigos 400/403 pueden tener varias causas: los mensajes no
aseguran que la clave sea necesariamente el problema.

### Resultado de las comprobaciones

- **42 pruebas correctas**: 13 del analizador local, 5 de su interfaz, 7 de la
  interfaz Gemini, 16 del cliente/configuración/respuestas Gemini y 1 de exclusiones.
- Las pruebas interceptan los clientes; una prueba adicional utiliza el SDK real
  con `httpx.MockTransport` para comprobar la serialización HTTP sin red.
- `pip check`: sin dependencias incompatibles. La versión de websockets resuelta
  por pip es compatible tanto con Streamlit como con google-genai.
- Compilación con `compileall`: correcta.
- Arranque real de Streamlit en `127.0.0.1:8502`, con HTTP 200 tanto en `/` como
  en `/_stcore/health` (`ok`). La interfaz se comprobó con AppTest, sin revisión
  visual manual en navegador en esta integración.
- `git diff --check`: correcto; `git diff --exit-code -- analyzer.py`: sin cambios.
- No se han configurado claves reales, creado archivos de secretos, realizado
  llamadas reales a Gemini, consumido cuota de Gemini, creado commits ni hecho push.

### Pendientes manuales

1. Revisar condiciones de Google, permisos del modelo, cuotas y facturación del
   proyecto antes de autorizar cualquier llamada real.
2. Configurar la clave privadamente en `.streamlit/secrets.toml` o en el entorno
   siguiendo el README. No enviarla al chat ni subirla a GitHub.
3. Autorizar la prueba real y comprobar un ejemplo ficticio SQL y otro ETL,
   la separación entre observaciones e hipótesis y la recuperación local en fallo.
4. Confirmar que cambiar el texto o los modos exige renovar la autorización y
   que el modo local sigue funcionando sin clave.
5. Solo tras aprobar los cambios, publicar y actualizar Cloud; configurar su
   clave exclusivamente en Secrets. El despliegue Linux de esta integración y su
   prueba de extremo a extremo siguen pendientes.

No se garantiza que las instrucciones eviten toda interpretación incorrecta del
modelo. No se valida ningún esquema y las sugerencias requieren revisión humana.
En modo Gemini el texto sale del equipo hacia Google y se aplican las condiciones
de tratamiento del proveedor; la aplicación no puede garantizar que Google no
retenga información. Nunca se deben introducir datos empresariales confidenciales.

## Diagnóstico y ajuste del primer timeout — v0.2

El usuario comunicó un timeout al analizar el ejemplo ficticio
`SELECT importe / 0 FROM ventas;`. No se ha reproducido con una petición real;
se han utilizado exclusivamente mocks y transporte HTTP simulado.

### Hechos confirmados y comprobación de presencia

- SDK instalado: `google-genai==2.23.0`. Sus tipos documentan timeout en
  milisegundos. En `_api_client.py`, `get_timeout_in_seconds` divide por 1000,
  y `populate_server_timeout_header` crea `X-Server-Timeout` en segundos.
  El límite original era de 20 s tanto para HTTPX como para esa cabecera;
  no había una confusión entre segundos y milisegundos.
- `HttpRetryOptions(attempts=1)` incluye la petición original y no realiza
  reintentos. Se verifica también utilizando el SDK real con MockTransport,
  incluyendo errores de red, timeout, 429 y 503/504.
- No se encontraron pausas artificiales, bloqueos por locks, consultas previas a
  la API ni bucles de reintento en la aplicación. La llamada síncrona espera la
  respuesta mientras Streamlit muestra el indicador de progreso.
- El mensaje antiguo agrupaba cualquier timeout de transporte y HTTP 408/504,
  por lo que no permite identificar retrospectivamente la fase del fallo.
- Solo se consultaron nombres de variables y existencia de archivos, nunca
  contenidos de secretos ni valores de claves. `GEMINI_API_KEY` no está presente
  en el entorno del proceso de diagnóstico ni en el del usuario ejecutor
  comprobado; tampoco consta su nombre entre las variables persistentes del
  usuario o sistema revisadas. No existen archivos de secretos local ni global
  en las rutas predeterminadas comprobadas. No se modificó ninguna credencial.
  Esto no verifica la sesión o despliegue donde se realizó la primera prueba:
  su configuración sigue pendiente de comprobación privada por el usuario.

### Cambios de esta corrección

- `gemini_analyzer.py`: timeout HTTP de **60 000 ms** con un intento por acción.
  Se amplía el margen para generación estructurada con razonamiento sin habilitar
  reintentos ni esperas ilimitadas. El plazo es del transporte y del presupuesto
  enviado al servidor; no garantiza un límite total exacto de la función.
  Se distinguen `ConnectTimeout`, `ReadTimeout`, `WriteTimeout`, `PoolTimeout`,
  timeout genérico y timeout devuelto por el servicio. Los mensajes de lectura y
  envío indican que no puede confirmarse si Google sigue procesando la petición.
  HTTP 400, 401, 402 y 403 tienen mensajes separados para evitar atribuir todos
  esos casos a una clave incorrecta. No se exponen detalles originales.
- `app.py`: muestra la versión 0.2, el límite de espera y la ausencia de
  reintentos/cambios automáticos de modelo; conserva la recuperación local.
- `tests/test_gemini_analyzer.py`: amplía errores relevantes, comprueba el cierre
  del cliente tras timeout y el estado `DEADLINE_EXCEEDED`. Con transporte
  simulado comprueba que HTTPX recibe 60.0 segundos y el servidor la cabecera
  `X-Server-Timeout: 60`, y que se realiza exactamente un intento por error.
- `tests/test_app_gemini.py`: reproduce el ejemplo comunicado con timeout de
  lectura simulado, comprueba el error saneado y la recuperación por reglas
  locales sin una segunda petición.
- `README.md` y `REVISION.md`: documentan diagnóstico, límites, alternativas
  y procedimiento de una sola prueba real, condicionado a autorización.

El modelo continúa siendo `gemini-3.8-flash`, con pensamiento `low`. La consulta a
la [documentación oficial de Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
confirma una alternativa estable y orientada a baja latencia con salida
estructurada; no confirma su acceso desde este proyecto. No se ha cambiado el
modelo, listado modelos mediante API ni realizado comparaciones de pago.

### Hipótesis pendientes

Una generación que tarde más de 20 s, congestión del servicio, problemas de red,
DNS, proxy o un intermediario que agote su plazo podrían producir el mensaje
anterior. No se atribuye el fallo a ninguna de ellas sin evidencia de la sesión
real. Tampoco se garantiza que ampliar el timeout resuelva el problema. Una clave
ausente en este entorno produciría una validación local, no explica por sí sola
el timeout comunicado en otra sesión.

La próxima prueba deberá realizarse con autorización, una sola pulsación y el
mismo modelo, recogiendo únicamente tiempo aproximado y mensaje saneado. Si
hay timeout no debe suponerse que la operación se canceló o que no consumió cuota.
El procedimiento detallado está en el README. No se requieren commits, push ni
actualización del despliegue para hacer la prueba local.

Verificación de esta corrección: **46 pruebas correctas**, incluidas las 19
originales y los nuevos casos de transporte/timeout. `pip check`, `compileall`
y `git diff --check` correctos. `git diff --exit-code -- analyzer.py` confirma
que el analizador local sigue intacto. Se inició una instancia temporal de
Streamlit en `127.0.0.1:8503`, con HTTP 200 en `/` y `/_stcore/health` (`ok`), y
se detuvo esa instancia al terminar. No se hicieron llamadas reales a Gemini,
consultas de modelos por API, cambios de credenciales, commits, push ni despliegues.

## Diagnóstico del segundo fallo: error genérico del servicio

Se revisaron cliente, interfaz y pruebas. El texto comunicado por el usuario
correspondía a una rama `APIError` que agrupaba códigos no tratados, entre ellos
500 y 503. Si la prueba utilizó esa versión, el mensaje indica dicha rama, pero
no conserva el código HTTP ni permite distinguir su causa. No se ha reproducido
el fallo mediante una llamada real y no se atribuye a un código concreto.

### Petición y modelos revisados

Con el SDK instalado 2.23.0 y transporte HTTP simulado se comprobó la petición a
`v1beta/models/gemini-3.8-flash:generateContent`: esquema JSON de siete campos,
MIME `application/json`, instrucciones de sistema separadas de los datos,
4096 tokens máximos, herramientas vacías y llamadas de funciones desactivadas.
El SDK serializa el pensamiento como `thinkingConfig: {"thinking_level": "LOW"}`.
Este detalle se captura en una prueba; no se altera manualmente la serialización.
La [especificación ProtoJSON](https://protobuf.dev/programming-guides/json/)
admite los nombres originales de campos y sus equivalentes camelCase. No se
considera ese nombre una causa confirmada del fallo. La validación local del SDK
y la documentación no prueban aceptación por el backend ni acceso del proyecto.

Se volvieron a consultar las fichas oficiales de
[Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
y [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite).
Ambas documentan versiones estables, entrada/salida de texto y salidas estructuradas.
Flash 3.8 soporta pensamiento `low`; Flash-Lite está orientado a baja latencia.
No se ha consultado la API de modelos ni se ha verificado su acceso para este
proyecto. Se conserva el modelo 3.8; no hay fallback de modelo.

### Política de transporte y errores

La generación de análisis y la nueva sonda comparten `_generate_content`:
timeout de 60 000 ms, `HttpRetryOptions(attempts=1)` y
`client_args={'follow_redirects': False}`. El SDK puede reintentar cuando se
configura para ello; un intento incluye la petición original y aquí excluye
reintentos. Se comprobó el código instalado de `retry_args` y su comportamiento
con MockTransport. Tampoco se siguen redirecciones HTTP ni se listan modelos,
cuentan tokens remotamente o ejecutan llamadas previas o posteriores automáticas.

Se distinguen HTTP 400, 401, 402, 403, 404, 429, 500, 503 y 408/504, además de
`DEADLINE_EXCEEDED`, errores de red y timeouts por fase. HTTP 500 indica error
interno y 503 indisponibilidad temporal, sin afirmar que la consulta SQL sea
incorrecta. Los estados no clasificados conservan un mensaje comprensible y
su código saneado en metadatos. Los fallos al interpretar la respuesta también
se sanean para no mostrar un `ValueError` original procedente del SDK.

### Diagnóstico estrictamente opt-in

`GeminiError` incorpora únicamente un diccionario de seis campos: `http_status`
(entero 100–599 o null), `exception_class` (lista cerrada u `OtherError`), `model`,
`timeout_ms`, `max_attempts` y `operation` (analysis/connectivity). No copia
mensajes, payloads, cabeceras, URLs, claves, respuestas, consultas ni trazas.

El panel de Streamlit está desactivado por defecto. Requiere simultáneamente
`DATAFLOW_LOCAL_DIAGNOSTICS=1` y enlace explícito del servidor a loopback. Una
dirección vacía, pública o `0.0.0.0` lo deshabilita. No debe habilitarse en Cloud,
túneles ni proxies que expongan la instancia local. Los datos saneados solo se
muestran en el panel local de errores, sin archivos de log, y se eliminan al
cambiar texto o modo. El modo local y `analyzer.py` permanecen intactos.

La comprobación de clave utilizó solo el booleano de presencia de su nombre en
el entorno: **false** en la terminal de diagnóstico. No se leyeron sus valores ni
el contenido de archivos de secretos; las rutas local y global comprobadas no
contenían tales archivos. Esto no verifica la terminal o el despliegue de la
segunda prueba real. No se han tocado credenciales.

### Sonda aislada preparada, no ejecutada contra Google

Nuevo `gemini_connectivity_check.py`. Sin argumentos o con un solo indicador
no lee la clave ni crea cliente alguno. Solo con ambos indicadores
`--execute-once --confirm-cost`, tras autorización del usuario, puede ejecutar
una petición con la clave ya configurada en el entorno. No carga secretos de
Streamlit ni acepta claves como argumentos. Los errores de argumentos tampoco
reflejan los argumentos recibidos.

La sonda usa el mismo modelo y transporte con el prompt fijo
`Responde únicamente OK.`, sin esquema, MIME de salida, instrucciones de sistema
ni configuración de pensamiento. Limita la salida a 128 tokens. No lee ni muestra
el texto generado y suprime logs del SDK/transporte durante la ejecución. Solo
indica recepción exitosa de la API o error saneado con HTTP/clase y metadatos fijos.
Una recepción exitosa no garantiza respuesta textual, ausencia de bloqueo o éxito
del análisis estructurado. La sonda no se ejecutó realmente en esta preparación;
sus rutas de ejecución se probaron únicamente con mocks y transporte simulado.

### Archivos y verificaciones de esta iteración

- `gemini_analyzer.py`, `app.py`: política común, clasificación y panel local.
- Nuevo `gemini_connectivity_check.py`: sonda local con dos indicadores explícitos.
- `tests/test_gemini_analyzer.py`, `tests/test_app_gemini.py`, nuevo
  `tests/test_connectivity_cli.py` y `tests/test_deployment.py`: errores,
  serialización real del SDK con MockTransport, redirecciones, metadatos,
  aislamiento del panel, consentimiento de la sonda y exclusiones de publicación.
- `README.md`, `AGENTS.md`, `REVISION.md`: instrucciones, límites y procedimiento.

**61 pruebas correctas**: 13 de reglas locales, 5 de interfaz local, 10 de interfaz
Gemini, 27 de cliente/diagnóstico, 5 de CLI y 1 de exclusiones. `pip check` y
`compileall` correctos. Arranque de una nueva instancia temporal de Streamlit en
un puerto libre de loopback, con HTTP 200 en `/` y `/_stcore/health` (`ok`). Se
detuvo exclusivamente el árbol de procesos de esa instancia temporal al terminar.
No se cambió el SDK, las dependencias ni el modelo.

### Causa pendiente y siguiente paso autorizado

Siguen siendo hipótesis la indisponibilidad del servicio, un error interno o un
problema del backend al manejar la combinación de opciones. No se confirma un
problema de credenciales, permisos, cuota, esquema JSON o disponibilidad del modelo
sin el código saneado de la sesión real. Aumentar el timeout no diagnostica estos
fallos ni los corrige necesariamente.

Se recomienda autorizar **una sola sonda de conectividad**, no otra prueba SQL
simultánea. El README indica el comando exacto. Una respuesta exitosa separaría
conexión/acceso básico de la generación estructurada, sin demostrar que el
servicio esté siempre disponible. Un fallo aportaría código y clase para el
siguiente diagnóstico. No repetir, cambiar de modelo ni volver a pulsar Analizar
sin una autorización independiente. No se han realizado llamadas reales a Gemini,
consumido su cuota, creado commits, hecho push ni publicado cambios.

## Preparación de una única prueba con Flash-Lite

El usuario comunica HTTP 503 `ServerError` de la sonda con `gemini-3.8-flash`,
sin reintentos. Ese resultado no prueba que la clave tenga acceso a Flash-Lite
ni que cambiar de modelo vaya a solucionar el servicio.

Se revisaron `gemini_analyzer.py` y `gemini_connectivity_check.py`. Se verificó
el identificador estable `gemini-3.5-flash-lite` en su
[ficha oficial](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
que documenta texto, salida estructurada y orientación a baja latencia. La consulta
de documentación no utiliza la API Key ni valida permisos del proyecto.

Cambios de esta preparación:

- `gemini_analyzer.py`: lista cerrada de dos modelos y resolución de configuración.
  La selección explícita tiene prioridad sobre `GEMINI_MODEL`. Sin configuración,
  el análisis conserva 3.8 Flash y la sonda adopta 3.5 Flash-Lite como modelo de
  prueba. No se modifica el entorno del usuario ni se cambian modelos en fallo.
  Los errores, resultados y solicitudes usan el mismo modelo resuelto para esa
  operación. Valores no permitidos se rechazan sin mostrarlos ni crear un cliente.
  Si se elige Lite para el análisis, no se fuerza la opción de pensamiento `low`
  específica de la configuración 3.8; la sonda sigue sin configurar pensamiento.
- `gemini_connectivity_check.py`: añade `--model`, con prioridad sobre el entorno,
  y anuncia modelo/límites antes de la única llamada autorizada. La salida final
  o el diagnóstico de error también indican el modelo efectivo. No muestra el
  texto recibido, secretos, cabeceras ni mensajes originales del SDK.
- `app.py`: muestra el modelo configurado validado y lo pasa explícitamente al
  cliente; una configuración Gemini inválida no impide usar las reglas locales.
- Pruebas actualizadas en `tests/test_gemini_analyzer.py`,
  `tests/test_connectivity_cli.py`, `tests/test_app_gemini.py` y
  `tests/test_app.py`: selección y prioridad, ambos modelos, metadatos en errores,
  conservación del transporte y funcionamiento local con configuración inválida.
- `README.md`, `AGENTS.md` y `REVISION.md`: configuración, restricciones y comando
  exacto para la única prueba pendiente.

Se mantienen timeout de 60 000 ms, un solo intento total, redirecciones desactivadas,
clasificación de errores y ausencia de fallback remoto. La petición de la sonda
sigue siendo texto fijo sin esquema JSON y limitada a 128 tokens. Se conserva la
opción 3.8 mediante `--model gemini-3.8-flash`; no se ejecuta como segunda prueba
automática si Lite falla.

Verificación: **70 pruebas correctas**, sin llamadas reales, `pip check` sin
incompatibilidades y compilación con `compileall` correcta. También se ejecutó
la comprobación sin indicadores de ejecución (`--model gemini-3.5-flash-lite`):
mostró el modelo Lite, timeout 60 000 y un intento, con `request_executed: false`.
La presencia del nombre de la clave en esa terminal resultó false; no se leyó su
valor. No se cambiaron dependencias, credenciales ni el analizador local.

La construcción de peticiones para Lite se ha comprobado con el SDK y transporte
simulado. **No se puede confirmar que esté habilitado para esta API Key sin una
llamada autorizada.** No se ha consultado la lista de modelos por API ni hecho
ninguna petición de comprobación adicional. Esa comprobación efectiva queda
reservada a la única sonda real solicitada, aún no ejecutada por el agente.

Tras autorizarla, desde la carpeta interior y una terminal con la clave configurada
privadamente, ejecutar exactamente una vez:

```powershell
.\.venv\Scripts\python.exe gemini_connectivity_check.py --model gemini-3.5-flash-lite --execute-once --confirm-cost
```

Esperar el resultado sin pulsar Analizar, repetir el comando ni probar otro modelo.
Compartir solo la salida técnica saneada. No se han realizado llamadas reales a
Google, modificado credenciales, creado commits, hecho push ni publicado cambios.

## Flash-Lite predeterminado y preparación de la prueba funcional SQL

El usuario comunica que la sonda real con `gemini-3.5-flash-lite` devolvió
`response_received: true`, timeout 60 000 ms y un intento. Se registra como un
resultado aportado por el usuario; no se ha repetido ni se ha leído la API Key.
La recepción satisfactoria de la sonda no prueba todavía el análisis SQL con
salida estructurada ni la calidad de una explicación generada.

Cambios de esta iteración:

- `gemini_analyzer.py`: `MODEL` pasa a `gemini-3.5-flash-lite`, también predeterminado
  de la sonda. Se introduce `ALTERNATIVE_MODEL='gemini-3.8-flash'` para conservar
  una alternativa explícita y separar el predeterminado del modelo que admite
  nuestra configuración de pensamiento `low`. No se fuerza esa opción en Lite.
  `GEMINI_MODEL` continúa teniendo prioridad sobre el predeterminado y `--model`
  de la sonda sobre el entorno. No hay cambios automáticos por fallo.
- `tests/test_gemini_analyzer.py`: valida con el ejemplo exacto
  `SELECT importe / 0 FROM ventas;` el modelo Lite, el contenido como datos,
  MIME JSON y esquema completo. La prueba de transporte simulado comprueba que
  el SDK envía el esquema sin cambios a la ruta Lite. Se verifica expresamente
  que la alternativa 3.8 conserva pensamiento `low` y un intento.
- `tests/test_app_gemini.py`: prueba funcional simulada con el texto SQL, modelo
  predeterminado visible en la interfaz y resultado estructurado, sin errores ni
  llamadas adicionales. La prueba de configuración verifica que la alternativa
  explícita 3.8 también se identifica y utiliza correctamente.
- `tests/test_connectivity_cli.py`: conserva cobertura de ambos modelos aunque
  los predeterminados de análisis y sonda ahora coincidan.
- `AGENTS.md`, `README.md`, `REVISION.md`: actualizan el predeterminado, la
  evidencia comunicada, los límites de la comprobación y el procedimiento manual.

`app.py` ya resuelve y muestra el modelo configurado; no necesitó cambios en esta
iteración. `analyzer.py` permanece intacto, al igual que el comportamiento del
modo local. Tampoco se modifican dependencias, credenciales o secretos.

### Compatibilidad del esquema

La [ficha oficial de Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
documenta soporte de salida estructurada. La
[guía de GenerateContent](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en)
incluye los elementos utilizados por el esquema actual: objeto, cadenas, listas,
`properties`, `required`, `items` y `additionalProperties`.

Se mantienen los siete campos `categoria`, `explicacion`, `hechos`, `hipotesis`,
`correcciones`, `recomendaciones` y `limitaciones`, con
`response_mime_type='application/json'` y `response_json_schema`. No se cambia el
esquema ni se relajan las validaciones locales de tipos, longitudes o finalización.
Se mantiene el máximo de 4000 caracteres originales, salida de 4096 tokens,
timeout HTTP de 60 segundos, un intento, ausencia de redirecciones y tratamiento
seguro de errores y de datos no confiables.

La documentación y las pruebas con el SDK real y MockTransport son evidencia de
compatibilidad prevista y serialización, no una prueba real del formato para
este proyecto. Esa validación de extremo a extremo sigue pendiente de autorización.

### Verificación y siguiente paso

**73 pruebas correctas**. `pip check`, `compileall` y `git diff --check` correctos.
`git diff --exit-code -- analyzer.py` confirma que el analizador local está intacto.
Se inició una nueva instancia temporal de Streamlit en un puerto libre de loopback:
`/` y `/_stcore/health` respondieron HTTP 200 (`ok`). Se detuvo únicamente el árbol
de procesos de esa instancia al terminar. No se han realizado llamadas reales a
Gemini, leído claves, creado commits, hecho push ni publicado la versión 0.2.

La siguiente prueba manual, una vez autorizada, debe hacerse desde la interfaz
Streamlit con la clave ya configurada privadamente, seleccionando Consulta SQL y
Gemini, comprobando el modelo Lite e introduciendo exclusivamente
`SELECT importe / 0 FROM ventas;`. Pulsar Analizar una sola vez, sin repetir la
sonda previa ni cambiar de modelo. Se debe revisar explicación en español,
indicios de posible división por cero, separación entre observaciones e hipótesis,
correcciones y recomendaciones condicionales, y límites sin inventar esquemas.
Si falla, conservar solo el mensaje/diagnóstico saneado y continuar localmente si
se desea, sin otra petición. El README incluye los comandos de arranque y criterios
detallados. Cualquier reintento real requiere una autorización independiente.

## Preparación editorial y de privacidad de v0.2 para publicación

El usuario confirma una primera prueba funcional real satisfactoria con Flash-Lite
y `SELECT importe / 0 FROM ventas;`, con observaciones, hipótesis, correcciones
y recomendaciones estructuradas. Se registra como evidencia comunicada; no se
repite la petición ni se considera una evaluación de todas las respuestas posibles.

### Instrucciones de Gemini y ejemplo ETL

`gemini_analyzer.py` refuerza la diferencia entre denominador cero, valor fuera del
rango de un tipo y conversión inválida. Se prohíbe inferir desbordamiento por ver
`/ 0` o proponer aumentar precisión/convertir a DECIMAL como arreglo del denominador.
Una discrepancia entre mensaje y fragmento debe exponerse como incertidumbre.

Se exige español natural con tildes, sin traducir palabras clave SQL ni nombres
aportados. Se preservan observaciones explícitas, hipótesis, correcciones y
recomendaciones en campos separados. Los ejemplos SQL deben ser ilustrativos,
de solo lectura y condicionales al motor, usando constantes o los identificadores
del texto, sin inventar esquemas. Se propone como ejemplo condicional
`10.0 / NULLIF(0, 0)` y se exige explicar el resultado NULL y decidir su tratamiento,
sin sustituirlo por cero automáticamente ni prometer portabilidad universal.

Se añade `examples/error_etl_ficticio.txt`: conversión del marcador ficticio
`importe="N/D"` a decimal durante la carga de un CSV de demostración, sin motor
ni precisión conocidos, datos personales o credenciales. No modifica los ejemplos
ni las reglas del analizador local. El README incluye su texto y criterios para
una única prueba manual futura con autorización: conversión frente a división
por cero/desbordamiento, significado de N/D como hipótesis, validación de formato
y tratamiento explícito de registros rechazados.

### Revisión de sesiones y Secrets

La interfaz no usa cachés o variables globales para consultas/respuestas/clientes.
La clave procede del backend y no se copia a widgets o Session State. Cada petición
crea y cierra su cliente. La entrada y el consentimiento permanecen en el widget
de su propia sesión; el resultado se renderiza sin guardarse en Session State.
Solo se conservan errores y metadatos saneados. El resultado visible puede copiarse
y el texto ocupa memoria transitoria: no se admiten datos sensibles.

`app.py` añade **Borrar texto y resultado**, que vacía la entrada, reinicia el
ejemplo y retira resultado, permiso, error y diagnóstico de la sesión actual sin
llamar a Google ni afectar a otras sesiones. No se promete borrado criptográfico
de memoria, del navegador ni eliminación en el proveedor.

La carga mediante `st.secrets['GEMINI_API_KEY']`, con prioridad sobre el entorno,
se mantiene. Se prueba con valores ficticios y con `StreamlitSecretNotFoundError`
real para confirmar fallback cuando falta el archivo. No se leen claves reales.
La [documentación oficial de Secrets en Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
confirma la configuración en App settings/Secrets; el despliegue efectivo no se
ha actualizado ni comprobado con la clave real. La
[documentación de sesiones](https://docs.streamlit.io/develop/concepts/architecture/session-state)
describe el aislamiento por sesión; las pruebas locales lo ejercitan con dos
instancias de AppTest, sin sustituir una prueba de navegadores/Cloud.

Una clave de servidor será compartida para las llamadas de los visitantes. La
casilla de consentimiento no impone autenticación o cuotas por usuario, que esta
aplicación no implementa. Antes de abrir la versión a terceros, el propietario
debe revisar permisos de acceso, cuotas y facturación. Diagnóstico local desactivado
en Cloud; secretos fuera de Git, logs de depuración y capturas.

### Archivos y verificaciones

- `gemini_analyzer.py`: instrucciones educativas refinadas; sin cambios de modelo,
  esquema, timeout, intentos ni transporte.
- `app.py`: borrado explícito de la sesión; se mantiene el modelo visible y la
  recuperación local. `analyzer.py` sigue intacto.
- `examples/error_etl_ficticio.txt`: nuevo caso manual público y ficticio.
- `tests/test_gemini_analyzer.py`: contrato de instrucciones, Unicode y separación
  de campos, ejemplos SQL, carga desde secretos/entorno y claves por petición sin caché.
- `tests/test_app_gemini.py`: dos sesiones independientes, ausencia de clave en la
  salida, borrado sin petición adicional y flujo ETL con respuesta simulada en español.
- `tests/test_deployment.py`: confirma que el ejemplo ETL no queda excluido.
- `AGENTS.md`, `README.md`, `REVISION.md`: límites, evidencia, privacidad y despliegue.

**80 pruebas correctas**. `pip check`, `compileall` y `git diff --check` correctos.
`git diff --exit-code -- analyzer.py` sin diferencias. Una nueva instancia temporal
de Streamlit respondió HTTP 200 en `/` y `/_stcore/health` (`ok`); se detuvo solo
su árbol de procesos al terminar. No se modifican dependencias ni credenciales.

Las pruebas con mocks verifican el contrato de instrucciones, el transporte y el
formato/presentación, no que el modelo real siempre razone correctamente o escriba
sin errores. Las instrucciones refinadas y el caso ETL aún requieren revisión
manual autorizada. No se ha llamado a Gemini, leído una clave real, creado commits,
hecho push ni publicado la versión 0.2 durante esta preparación.

### Antes de publicar

Completar la revisión manual autorizada de SQL con las instrucciones refinadas y
del ejemplo ETL; revisar el diff y las exclusiones; conservar/configurar la clave
únicamente en Secrets de Cloud; comprobar acceso, cuotas, Python 3.12, dependencias,
modelo visible Lite y diagnóstico desactivado. Solo después de autorizar la
publicación, crear commit y push. Un push a una rama seguida por Cloud puede
disparar el despliegue automático, por lo que debe prepararse su configuración antes.
Después quedarán la comprobación real Linux/Cloud y el aislamiento en navegadores
independientes. El README detalla estos pasos y el procedimiento manual.

## Validación de release DataFlow AI v0.2

El usuario confirma pruebas manuales SQL y ETL satisfactorias y autoriza publicar
en el repositorio existente `https://github.com/DavidIllescas/DataFlow-AI`, mediante
un commit en `main` y un push normal, sin force push. Los resultados manuales son
aportados por el usuario; el agente no repite llamadas a Gemini.

La release reúne el modo opcional Gemini con `gemini-3.5-flash-lite`, formato JSON
validado, instrucciones educativas en español, consentimiento explícito, un intento
y timeout HTTP de 60 segundos. Conserva reglas locales predeterminadas y recuperación
local, sin cambios en `analyzer.py`, además de borrado de sesión y ejemplo ETL ficticio.

Validación automática de release: **81 pruebas correctas**, `pip check` sin
incompatibilidades y `compileall` correcto. Las pruebas usan mocks, transporte
simulado y claves ficticias. No se lee ni publica una clave real. Se añade un caso
que comprueba la configuración versionada de Cloud: el diagnóstico queda desactivado
incluso si existe el indicador de entorno, porque no se enlaza explícitamente el
servidor a loopback. No se activa diagnóstico en producción ni se cambian secretos
de Cloud. El estado externo del despliegue se verifica por separado tras la subida.

Dependencias directas de producción: Streamlit 1.66.1, SDK oficial google-genai
2.23.0 y httpx 0.28.1 para transporte/clasificación de errores. No se añaden paquetes
de tests a `requirements.txt`; unittest forma parte de Python. El snapshot local
de dependencias no sustituye ese archivo de instalación de Cloud.

Se actualiza el título del README a v0.2 y se registran las pruebas manuales
satisfactorias. `especificacion.md` conserva expresamente el alcance original
v0.1, que el README identifica como antecedente de esta integración opcional.

Antes del commit se revisa el índice completo para excluir claves, credenciales,
entornos, consultas confidenciales y rutas privadas innecesarias. `.gitignore`
excluye `.env`, `.venv`, cachés, temporales, credenciales y `secrets.toml`, y conserva
`.streamlit/config.toml`. La publicación se condiciona a que esta revisión no
encuentre problemas. El hash de release y la sincronización se verifican en Git;
no se escribe un hash autorreferente dentro del propio commit.

El commit solicitado es `Release DataFlow AI v0.2: Gemini integration`. No se
realizan llamadas reales a Gemini ni operaciones destructivas. La actualización
automática que Cloud pueda efectuar al seguir `main` no prueba la configuración
del servicio ni autoriza llamadas Gemini adicionales. La comprobación operativa
de la aplicación desplegada queda separada del resultado de GitHub.

## Integración segura del devcontainer y resolución de la divergencia

El primer push de release fue rechazado porque `origin/main` había añadido
`3fe128a` (Added Dev Container Folder). El usuario autoriza integrar ese commit
con la release local `d8c6aa5`, preservando ambos historiales y corrigiendo las
opciones inseguras de desarrollo antes de publicar.

Tras `git fetch origin`, la revisión confirma que el único archivo remoto nuevo
es `.devcontainer/devcontainer.json`: imagen oficial de desarrollo Python 3.11,
extensiones de Microsoft, apertura de README/app, instalación de dependencias,
puerto 8501 y arranque de Streamlit. No se detectaron secretos, URLs con
credenciales, rutas privadas o cambios ajenos a esa configuración. Sus comandos
de instalación se revisaron como texto y no se ejecutaron ni se construyó el
contenedor durante esta tarea.

El merge normal se inició con `--no-commit --no-ff origin/main` y no produjo
conflictos. Antes del commit se elimina del arranque únicamente
`--server.enableCORS false --server.enableXsrfProtection false`; queda
`streamlit run app.py`. Se conservan los demás ajustes legítimos. El resultado
del merge incluye la corrección, las pruebas y la documentación: no se reescriben
commits, no se descartan cambios y no se necesita force push.

Se añade una prueba en `tests/test_deployment.py` para comprobar comando seguro,
imagen y puerto conservados y opciones CORS/XSRF activas en Streamlit. El README
documenta el devcontainer y actualiza la validación a **82 pruebas correctas**.
`pip check` y `compileall` correctos. Una instancia nueva de Streamlit, con las
protecciones activas, responde HTTP 200 en `/` y `/_stcore/health` (`ok`); se detiene
únicamente el árbol de esa instancia temporal al finalizar.

Se mantiene el diagnóstico desactivado con la configuración de producción
versionada, Flash-Lite predeterminado y `analyzer.py` sin modificaciones. La
revisión previa al commit examina el índice completo, las exclusiones de privados
y el diff de seguridad. No se leen claves privadas del entorno ni Secrets, no se
realizan llamadas reales a Gemini y no se cambia la configuración privada de Cloud.

El nuevo commit es un merge con dos padres, que conserva `d8c6aa5` y `3fe128a`
como ancestros. El resultado del push normal y la igualdad entre HEAD,
`origin/main` y la referencia remota se verifican posteriormente en Git.
Tras publicar queda revisar manualmente el arranque/logs del despliegue Cloud,
modelo visible y diagnóstico desactivado; cualquier llamada Gemini adicional
requiere autorización independiente.
