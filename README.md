# DataFlow AI — v0.2

Prototipo de aplicación educativa para explicar errores frecuentes de SQL y ETL en español.

Versión 0.2: integración opcional de Gemini Flash-Lite, recuperación local y
controles de privacidad. El usuario confirma pruebas manuales SQL y ETL
satisfactorias. La validación automática actual incluye 105 pruebas locales,
sin llamadas reales a Gemini. Esta actualización incorpora la protección de cuota
descrita abajo; su activación en el despliegue Cloud se comprueba por separado.

## Funciones actuales
- Entrada de consultas o mensajes de error ficticios.
- Análisis local por reglas: sintaxis SELECT, división por cero y referencias a columnas inexistentes.
- Explicación y sugerencias con advertencia de limitaciones.

El modo **Reglas locales** conserva el análisis de la versión 0.1 y es la opción
predeterminada. El nuevo modo **Gemini (opcional)** ofrece explicaciones,
observaciones, hipótesis, posibles correcciones y recomendaciones en español.
No se ejecutan consultas ni se guardan entradas o respuestas en archivos.
`especificacion.md` describe el alcance original de la versión 0.1; esta
integración opcional se documenta aquí y en `REVISION.md`.

## Ejecutar

El repositorio conserva el devcontainer añadido previamente en GitHub. Su arranque
usa `streamlit run app.py`, con las protecciones CORS y XSRF predeterminadas activas;
no hay opciones que las deshabiliten. Se mantienen su imagen Python 3.11,
extensiones, instalación de dependencias y puerto 8501. El entorno local y Cloud
documentados abajo usan Python 3.12. No es necesario construir el devcontainer para
ejecutar la aplicación, y su configuración no modifica los secretos de Cloud.

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
la apertura automática del navegador. El modo local no necesita claves ni servicios
externos; la instalación inicial sí descarga paquetes. Gemini requiere configurar
una clave y autorizar el envío desde la interfaz.

`requirements.txt` fija `streamlit==1.66.1`, el SDK oficial `google-genai==2.23.0`
y `httpx==0.28.1` (también utilizado directamente para distinguir errores de red
y timeout). Las dependencias transitivas las resuelve pip según el sistema
operativo. Se utiliza Python 3.12 para el entorno local y el despliegue.
No se necesitan `packages.txt` ni controladores SQL.

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
Las pruebas Gemini usan claves ficticias, clientes mock y transporte HTTP simulado:
no requieren configurar `GEMINI_API_KEY`, no llaman a Google ni consumen cuota.
Las pruebas de interfaz del modo local verifican que no se crea un cliente Gemini.
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
no detectan todos los errores. El modo local no envía el texto a servicios de análisis.
Los textos permanecen en memoria durante la sesión de Streamlit; la aplicación
no los registra ni los guarda en archivos.

## Gemini opcional: configuración y uso

Se utiliza por defecto [`gemini-3.5-flash-lite`](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
identificado como estable y compatible con respuestas estructuradas en la
documentación oficial consultada el 28 de octubre de 2026. Se usa el
[SDK oficial google-genai](https://googleapis.github.io/python-genai/), no la
biblioteca antigua `google-generativeai`. La disponibilidad efectiva depende del
proyecto, la región, los permisos y las cuotas. El usuario ha comunicado una sonda
de conectividad y una primera prueba funcional SQL satisfactorias con Flash-Lite.
Las pruebas manuales SQL y ETL con las instrucciones refinadas también han sido
confirmadas por el usuario antes de esta publicación. No se garantiza coste cero ni disponibilidad
futura del modelo. `gemini-3.8-flash` se conserva como alternativa explícita.

Configura una clave por tu cuenta en Google AI Studio y revisa sus condiciones,
cuotas y facturación antes de cualquier llamada. No pegues claves en el chat,
código, capturas, incidencias o registros. No se ha creado ni configurado ninguna
clave como parte de la integración.

### Configuración local

Opción recomendada: crea localmente `.streamlit/secrets.toml` con tu editor. El
siguiente ejemplo contiene solo un marcador que debes sustituir en ese archivo
privado, nunca en el repositorio:

```toml
GEMINI_API_KEY = "<CONFIGURAR_SOLO_EN_SECRETOS>"
```

El archivo ya está excluido por `.gitignore`; `.streamlit/config.toml` debe seguir
versionado. No crees un archivo de secretos real como parte de las pruebas.
Reinicia Streamlit tras configurar o cambiar la clave.

También se admite la variable de entorno `GEMINI_API_KEY`. En PowerShell puedes
introducirla sin mostrarla ni escribirla en el historial de comandos:

```powershell
$geminiSecret = Read-Host 'Clave Gemini (entrada oculta)' -AsSecureString
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new('', $geminiSecret).Password
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
# Tras detener Streamlit:
Remove-Item Env:GEMINI_API_KEY
Remove-Variable geminiSecret
```

Si existen ambos valores, se prioriza `st.secrets["GEMINI_API_KEY"]`. Un archivo
de secretos ausente permite usar el entorno; un archivo mal formado debe corregirse.
No se cargan archivos `.env` automáticamente. `GOOGLE_API_KEY` no se usa como
fuente alternativa: la aplicación pasa explícitamente la clave seleccionada al SDK.

### Secrets en Streamlit Community Cloud

Cuando autorices la publicación de esta integración, actualiza las dependencias
del despliegue. En la configuración de la aplicación de Community Cloud, abre
**Secrets** y configura la misma entrada TOML `GEMINI_API_KEY` con tu clave privada.
Guarda los secretos y reinicia la aplicación si es necesario. No subas
`.streamlit/secrets.toml` ni uses un archivo `.env` en GitHub.
Sin clave configurada, el modo local sigue funcionando; si se intenta usar Gemini,
se informa de la ausencia de configuración sin hacer la llamada.

### Flujo, límites y privacidad

1. Mantén **Reglas locales** para analizar sin enviar datos a Google.
2. Para una prueba real autorizada, selecciona **Gemini (opcional)** y utiliza
   exclusivamente una consulta o un mensaje ficticio, nunca datos empresariales
   confidenciales, datos personales o credenciales.
3. Marca la confirmación de envío a Google y posible consumo de cuota/coste.
   Seleccionar Gemini o marcar la casilla por sí solo no inicia una llamada.
4. Pulsa **Analizar**. La confirmación se revoca si editas el texto, cambias de
   ejemplo o cambias el sistema de análisis.
5. Revisa observaciones e hipótesis por separado y valida las sugerencias.
   Si Gemini falla, se muestra el error y un botón **Continuar con análisis local**
   para procesar el texto actual sin otra llamada a Google.

Se admiten hasta 4000 caracteres originales. Cada acción hace un solo intento,
sin reintentos automáticos, con timeout HTTP de 60 segundos y un máximo de 4096
tokens de salida. El timeout corresponde al transporte HTTP, no a una garantía
de duración total exacta. La salida JSON se valida y limita a 20 000 caracteres,
con límites por campo; una respuesta vacía, bloqueada, truncada o inválida se
trata como fallo. Se distinguen errores de configuración/autenticación, cuota,
modelo no disponible, conexión y timeout sin mostrar detalles de excepciones.

### Diagnóstico del primer timeout y prueba controlada

El SDK expresa `HttpOptions.timeout` en **milisegundos** y lo convierte a segundos
para HTTPX y para la cabecera `X-Server-Timeout`. La configuración inicial de
20 000 ms equivalía correctamente a 20 s. Se amplía a **60 000 ms (60 s)** para
dar más margen a una generación estructurada con un modelo que razona, sin dejar
la espera ilimitada. Es un ajuste preventivo: no demuestra que la causa original
fuera la latencia del modelo. Sigue habiendo un solo intento por pulsación.
El timeout HTTP limita la espera de cada operación de transporte y el presupuesto
comunicado al servidor; no es un cronómetro total exacto para toda la función.

La aplicación diferencia espera al conectar, enviar, recibir y obtener una
conexión del pool, además de timeout devuelto por el servicio (HTTP 408/504 o
`DEADLINE_EXCEEDED`). Un timeout de lectura no prueba que Google cancelara el
procesamiento: podría haber consumido cuota. Los errores 400, 401, 402, 403, 404
y 429 se presentan respectivamente como solicitud/configuración, autenticación,
facturación, acceso/permisos, modelo no disponible y cuota. No se muestran detalles
de excepciones ni se deduce que todo error 400/403 sea una clave inválida.

Se conserva `gemini-3.8-flash` como alternativa explícita, con pensamiento `low`.
Tras la conectividad satisfactoria comunicada por el usuario, el predeterminado
del análisis pasa a Flash-Lite, sin forzar una configuración de pensamiento.
No se añaden bloqueos, pausas ni cambios automáticos de modelo.

### Configuración del modelo y prueba Flash-Lite

La documentación oficial confirma el identificador estable
[`gemini-3.5-flash-lite`](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite).
La aplicación permite únicamente ese modelo y `gemini-3.8-flash`. La selección se
resuelve una vez por operación, sin fallback automático:

| Configuración | Análisis de la aplicación | Sonda aislada |
| --- | --- | --- |
| Sin configuración | `gemini-3.5-flash-lite` | `gemini-3.5-flash-lite` |
| Variable de entorno `GEMINI_MODEL` | Modelo permitido configurado | Modelo permitido configurado |
| Argumento `--model` | No aplica | Prioridad sobre `GEMINI_MODEL` |

Para configurar la aplicación en una terminal local, puedes establecer
`$env:GEMINI_MODEL = 'gemini-3.5-flash-lite'` antes de arrancar Streamlit; para
elegir la alternativa usa `gemini-3.8-flash`; eliminar esa variable devuelve
el análisis a Flash-Lite. No es una
credencial y no sustituye `GEMINI_API_KEY`. La interfaz muestra el modelo elegido.
Un valor no permitido se rechaza antes de crear el cliente y no se refleja en
mensajes o diagnósticos. No impide usar el analizador local.

El análisis conserva el esquema JSON y el resto de límites; `thinking_level=low`
se sigue configurando para 3.8 Flash. Si se elige Flash-Lite para el análisis, no
se fuerza ese parámetro específico. La sonda no configura pensamiento para ninguno.
Los límites de 60 segundos, un intento y ausencia de redirecciones se conservan.

El usuario ha comunicado un HTTP 503 `ServerError` de la sonda 3.8 y después una
recepción satisfactoria con Flash-Lite, con 60 000 ms y un intento. Eso confirma
la conectividad de aquella petición según la sonda, pero no la calidad del texto,
el esquema JSON ni la disponibilidad futura. El análisis estructurado se ha
verificado localmente con mocks y SDK real sobre transporte simulado. No se ha
leído la API Key ni se ha llamado a Google durante esta preparación.
Posteriormente, el usuario ha confirmado una primera prueba funcional satisfactoria
con `SELECT importe / 0 FROM ventas;` y los apartados estructurados. Las instrucciones
se han refinado después de esa prueba; no se ha repetido contra Google.

### Criterios educativos de la versión 0.2

Las instrucciones exigen español claro, con tildes y redacción natural, preservando
los identificadores y palabras clave SQL. Las observaciones se limitan a lo que
aparece en el texto; las hipótesis y las propuestas se presentan por separado.

Dividir por cero y desbordar un tipo numérico son problemas distintos. Ver `/ 0`
no demuestra desbordamiento; aumentar precisión o convertir a DECIMAL no elimina
un denominador cero. Si un mensaje contradice el fragmento, Gemini debe señalar la
incertidumbre en lugar de inventar una explicación comprobada.

Cuando aporten valor, las correcciones deben incluir expresiones SQL ilustrativas
de solo lectura, con constantes o identificadores ya proporcionados. Por ejemplo,
**si el motor admite NULLIF**, `10.0 / NULLIF(0, 0)` evita la división por cero y
produce NULL. Debe decidirse cómo tratar ese resultado: no se sustituye por cero
automáticamente. No se promete portabilidad universal ni se inventa un esquema.
La aplicación solo muestra ejemplos; nunca ejecuta SQL ni aplica correcciones.
Las pruebas con mocks verifican instrucciones, formato y presentación; no demuestran
que un modelo real siempre siga las instrucciones o clasifique correctamente.

### Ejemplo ETL ficticio para una prueba manual autorizada

Disponible en `examples/error_etl_ficticio.txt`, sin datos personales ni credenciales:

```text
EJEMPLO TOTALMENTE FICTICIO — sin datos personales ni credenciales.
Proceso: cargar un CSV de demostración.
Paso: convertir el campo importe a un número decimal.
Registro de prueba: importe="N/D"; unidades="3".
Mensaje: conversión no válida de "N/D" a número decimal.
Motor SQL y herramienta ETL: no especificados.
No se ha indicado la precisión ni el tipo concreto de destino.
```

Tras autorizar una única llamada, inicia Streamlit con los comandos de la sección
SQL, elige **Mensaje de error ETL → Gemini**, confirma Flash-Lite y pega el ejemplo.
Autoriza el envío y pulsa Analizar una sola vez. Revisa que distinga una posible
conversión inválida de división por cero o desbordamiento, que trate el significado
de `N/D` como hipótesis y que recomiende validar formato y gestionar registros
rechazados, sin sustituir silenciosamente el dato por cero ni inventar el motor.
Debe mostrar los mismos apartados en español y sus limitaciones. Si falla, utiliza
la recuperación local sin otra petición; no repitas Gemini sin nueva autorización.
El usuario ha confirmado esta prueba ETL satisfactoria. El agente no la ha
repetido contra Google; el procedimiento anterior sirve para futuras pruebas
autorizadas, no para generar otra llamada durante la publicación.

### Prueba funcional SQL con Flash-Lite y repetición autorizada

La [documentación de salida estructurada de GenerateContent](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en)
incluye Flash-Lite y los elementos del esquema actual: `object`, `string`, `array`,
`properties`, `required`, `items` y `additionalProperties`. El esquema mantiene
sus siete campos: `categoria`, `explicacion`, `hechos`, `hipotesis`, `correcciones`,
`recomendaciones` y `limitaciones`. Se envía con `response_mime_type='application/json'`
y `response_json_schema`, y se validan tipos, campos, longitudes y fin de generación
al recibir la salida. No se relajan las validaciones para conseguir una respuesta.

La primera ejecución funcional fue confirmada por el usuario. Para comprobar las
instrucciones refinadas, solo tras autorizar **una nueva llamada funcional**, con la clave ya configurada
privadamente y la cuota revisada:

1. Desde la carpeta interior `DataFlow_AI`, utiliza la misma terminal con acceso
   a la configuración de clave de la prueba satisfactoria. No muestres ni copies
   la clave al chat. No repitas la sonda de conectividad.
2. Inicia la aplicación actualizada. La variable siguiente configura solo el modelo,
   no contiene credenciales, y asegura que un ajuste anterior de 3.8 no lo sustituya:

   ```powershell
   $env:GEMINI_MODEL = 'gemini-3.5-flash-lite'
   .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8504
   ```

3. Abre `http://127.0.0.1:8504`. Selecciona **Consulta SQL** y **Gemini (opcional)**.
   Confirma que se muestra `gemini-3.5-flash-lite`, 60 segundos y un intento.
4. Introduce exactamente `SELECT importe / 0 FROM ventas;`, marca la autorización
   de envío del ejemplo ficticio y pulsa **Analizar una sola vez**. No refresques,
   vuelvas a pulsar ni pruebes otro modelo mientras esperas.
5. Comprueba que aparece **Resultado de Gemini**, una explicación en español,
   observaciones separadas de hipótesis, posibles correcciones, recomendaciones
   y limitaciones. Debe reconocer el denominador literal cero como indicio de
   posible división por cero, sin afirmar que se haya ejecutado la consulta ni
   inventar el esquema o los tipos de `ventas` e `importe`. Las correcciones
   deben presentarse como propuestas que requieren validación.
6. Si falla, conserva únicamente el mensaje saneado y, si estaba habilitado el
   diagnóstico local, su código/clase/modelo. Puedes usar **Continuar con análisis
   local**, que no hace otra llamada a Google. No repitas Gemini como parte de
   esta autorización; un timeout no garantiza ausencia de consumo.
7. Detén la instancia con `Ctrl+C`. Registra modelo, duración aproximada, éxito
   del formato y valoración de esos criterios. El texto exacto puede variar y un
   JSON válido no garantiza exactitud. No publiques aún la versión 0.2.

### Segundo error: diagnóstico local seguro

El mensaje genérico «El servicio de Gemini no pudo completar el análisis» agrupaba
códigos de la API no tratados individualmente, entre ellos 500 y 503. Sin el código
original no permite distinguir error interno, indisponibilidad u otro estado.
Ahora 500 y 503 tienen mensajes diferenciados. El resto de excepciones se clasifica
sin imprimir el mensaje original ni su traceback.

La llamada de análisis predeterminada sigue usando el SDK oficial, endpoint Gemini
Developer API, `v1beta/models/gemini-3.5-flash-lite:generateContent`, esquema JSON de siete campos
y 4096 tokens máximos, sin parámetro de pensamiento forzado. Para la alternativa
3.8 el SDK serializa `thinkingConfig: {"thinking_level": "LOW"}`. Se ha comprobado con un transporte
simulado: demuestra qué envía el SDK, no que el proyecto tenga acceso ni que el
backend acepte toda combinación de opciones.

La política compartida por análisis y sonda es **un único intento total**, timeout
HTTP de 60 000 ms y redirecciones HTTP desactivadas. No se listan modelos, cuentan
tokens mediante API, cambian modelos automáticamente ni se hacen comprobaciones remotas previas.
El SDK admite reintentos cuando se configuran; la aplicación los fija expresamente
a `HttpRetryOptions(attempts=1)`. No hay reintentos propios ni fallback remoto.

El diagnóstico está desactivado por defecto. Para habilitarlo **solo en tu equipo**:

```powershell
$env:DATAFLOW_LOCAL_DIAGNOSTICS = '1'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8503
# Tras detener Streamlit:
Remove-Item Env:DATAFLOW_LOCAL_DIAGNOSTICS
```

Se necesitan tanto la variable como un enlace explícito a loopback. Con dirección
vacía o `0.0.0.0` no se habilita. No lo actives en Community Cloud, túneles ni
proxies públicos; el enlace local no protege una instancia que expongas por proxy.
Si ocurre un fallo, aparece un panel con estos únicos campos:

- `http_status`: número HTTP o `null` si no existe/no es válido.
- `exception_class`: nombre incluido en una lista cerrada, u `OtherError`.
- `model`, `timeout_ms`, `max_attempts`, `operation`: metadatos fijos de la petición.

No incluye claves, cabeceras, URLs recibidas, mensajes de excepción, consultas,
respuestas, trazas ni objetos del SDK. No se escribe en registros o archivos.
Un cambio de texto/modo elimina el diagnóstico anterior. Activarlo no ejecuta una
petición: sigue siendo necesario autorizar y pulsar Analizar.

### Sonda aislada de conectividad (conservada para diagnóstico)

La sonda `gemini_connectivity_check.py` permite aislar conexión, acceso al modelo
y servicio. **No se ha ejecutado contra Google por el agente.** Su implementación
se ha probado con mocks; el usuario ha comunicado 503 con 3.8 y después recepción
satisfactoria con Flash-Lite. No se necesita repetirla antes de la prueba funcional
descrita arriba. Cada nueva ejecución real requiere autorización. La sonda usa el modelo
configurado (ahora Flash-Lite por defecto) y la misma política de transporte,
pero envía únicamente `Responde únicamente OK.`, sin instrucciones de sistema,
esquema JSON, MIME de salida ni configuración de pensamiento, con límite de 128
tokens. No muestra ni lee el texto generado: un resultado `response_received: true`
solo confirma que el SDK recibió una respuesta exitosa de la API; no garantiza que
se generara «OK», que no hubiera bloqueo de contenido o que el análisis JSON funcione.

Sin argumentos, o con solo uno de los dos indicadores, la sonda no lee la clave ni
crea un cliente: solo informa de la presencia del **nombre** `GEMINI_API_KEY` en el
entorno y de metadatos fijos. Presencia no equivale a clave válida o no vacía.
Esta sonda usa exclusivamente la clave del entorno, no lee archivos de secretos.
La aplicación Streamlit sigue admitiendo Secrets con prioridad sobre el entorno.

Procedimiento recomendado, **solo tras autorizar una llamada real**:

1. Desde la carpeta interior `DataFlow_AI`, utiliza una terminal local donde ya
   hayas configurado privadamente `GEMINI_API_KEY`. Revisa cuota y facturación;
   no compartas su valor ni lo pases como argumento del programa.
2. Ejecuta exactamente una vez:

   ```powershell
   .\.venv\Scripts\python.exe gemini_connectivity_check.py --model gemini-3.5-flash-lite --execute-once --confirm-cost
   ```

3. Confirma que el anuncio inicial indica `gemini-3.5-flash-lite`, 60 000 ms y
   un intento. El resultado o error saneado también conserva ese modelo.
   Espera a que termine. No pulses Analizar en Streamlit, no pruebes otro modelo
   ni repitas el comando como parte de esta autorización. Si falta la clave,
   se detiene antes de crear el cliente.
4. Comparte únicamente el resultado saneado: código HTTP, clase de excepción,
   modelo y, si quieres, tiempo aproximado. La sonda suprime los logs durante la
   ejecución, no imprime cabeceras, claves, prompt o texto recibido ni traceback.
   Los códigos de salida son 0 para comprobación sin petición o recepción de la
   API; 1 para fallo de la prueba; 2 para configuración/argumentos no válidos.
5. Si recibe respuesta, queda por probar separadamente el formato estructurado
   de la aplicación. Si falla, el código permite dirigir el diagnóstico sin
   atribuirlo a SQL o al esquema JSON. Cualquier segunda petición exige otra
   autorización. Un timeout no garantiza cancelación ni ausencia de consumo.

La entrada se envía como datos JSON separados de las instrucciones de sistema.
No se habilitan herramientas, funciones, búsquedas, ejecución de código ni SQL.
La salida se muestra como texto plano para evitar cargar enlaces o imágenes del
modelo. Estas medidas reducen riesgos de instrucciones ocultas; no garantizan que
Gemini interprete correctamente el texto ni que sus respuestas sean exactas.

En Gemini, el texto sí se transmite a Google y se aplican sus condiciones de
tratamiento de datos. No se garantiza ausencia de retención por el proveedor.
La aplicación no registra ni guarda entradas/respuestas ni las cachea. No actives
logs de depuración del SDK o HTTP con información sensible. En una aplicación
pública, la clave del servidor puede consumir la cuota de su propietario: revisa
límites y facturación antes de habilitar pruebas de terceros.

### Privacidad y varios usuarios

Las entradas y el consentimiento pertenecen al estado del widget de cada sesión;
no se ponen en variables globales, cachés, historial o archivos. Las respuestas se
renderizan en la ejecución actual y no se guardan en Session State. Cada petición
crea y cierra su cliente: no se cachean clientes ni claves. La clave del servidor
solo se utiliza en el backend y no se muestra en widgets, errores o diagnósticos.
El diagnóstico técnico continúa desactivado por defecto y no debe habilitarse en Cloud.

El botón **Borrar texto y resultado** vacía la entrada, reinicia el ejemplo y
retira resultado, consentimiento y diagnóstico de la sesión actual, sin llamadas
a Google. No afecta a otras sesiones. Las pruebas con dos sesiones simuladas
comprueban separación de entradas, consentimiento y resultados, y ausencia de claves
en la salida. No constituyen una auditoría de navegador o de infraestructura Cloud.
No se promete borrado criptográfico de memoria ni eliminación de datos en Google.
El texto permanece temporalmente en la sesión y la respuesta visible puede copiarse;
por eso se admiten exclusivamente ejemplos ficticios, nunca consultas sensibles.

Una casilla de consentimiento no es autenticación ni un límite de consumo por
persona. La aplicación no incorpora cuentas; los límites técnicos por sesión e
instancia se describen a continuación y no identifican a una persona. Antes de abrir
Gemini a terceros, limita el acceso al despliegue cuando proceda y revisa los límites
y la facturación del proyecto de Google; cada visitante puede consumir la cuota de
la misma clave del servidor. El modo local sigue disponible sin enviar datos.

### Protección de cuota Gemini: sesión y proceso

El modo **Reglas locales** sigue seleccionado por defecto, ilimitado en número
de análisis y ajeno a los contadores de Gemini. Conserva su validación de entrada
de 4000 caracteres. El modo Gemini añade estos límites conservadores para una demo:

| Variable pública de entorno | Predeterminado | Significado |
| --- | ---: | --- |
| `DATAFLOW_GEMINI_SESSION_LIMIT` | 3 | Intentos admitidos durante la sesión actual |
| `DATAFLOW_GEMINI_COOLDOWN_SECONDS` | 30 | Segundos entre inicios de intentos de la misma sesión |
| `DATAFLOW_GEMINI_GLOBAL_LIMIT` | 20 | Intentos totales compartidos por todas las sesiones del proceso |

Son enteros no negativos. Cero en un límite de intentos deshabilita Gemini; cero
en cooldown elimina esa espera. Un valor vacío, negativo o no entero bloquea
Gemini con un mensaje saneado, pero permite seguir con el análisis local. No hay
un valor especial «ilimitado» para Gemini. La cuota es de intentos, no de tokens,
dinero ni garantía de coste cero dentro del plan de Google.

Para configurar sin editar código, establece solo esas variables públicas antes
de iniciar Streamlit, por ejemplo en PowerShell:

```powershell
$env:DATAFLOW_GEMINI_SESSION_LIMIT = '3'
$env:DATAFLOW_GEMINI_COOLDOWN_SECONDS = '30'
$env:DATAFLOW_GEMINI_GLOBAL_LIMIT = '20'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

En Community Cloud, tras autorizar la actualización, el propietario puede añadir
estos parámetros no sensibles en el nivel raíz de **App settings → Secrets**,
conservando la clave privada existente sin copiarla al chat ni al repositorio:

```toml
DATAFLOW_GEMINI_SESSION_LIMIT = 3
DATAFLOW_GEMINI_COOLDOWN_SECONDS = 30
DATAFLOW_GEMINI_GLOBAL_LIMIT = 20
```

Streamlit exporta los valores escalares raíz al entorno del servidor; el lector de
límites solo consulta esos tres nombres públicos, nunca `GEMINI_API_KEY` ni el
contenido de Secrets. No se cargan archivos `.env` automáticamente. Comprueba los
límites mostrados en la interfaz al activar la nueva versión. Un reinicio para
aplicar configuración también puede renovar el presupuesto en memoria.

La entrada, el tipo y el modelo se validan antes de reservar. Si un límite ya
bloquea, no se lee la clave ni se crea un cliente SDK. Tras resolver la clave, se
recomprueba y reserva **atómicamente** el intento de sesión y el global bajo un
lock compartido. Así otra sesión no puede utilizar simultáneamente el último
hueco y causar un exceso. El lock se libera antes de llamar al SDK; no se mantiene
durante una espera de red de hasta el timeout configurado.

Un intento admitido cuenta aunque después haya timeout, error de API, respuesta
inválida o fallo al crear el cliente. No se devuelve ese presupuesto, porque no
siempre puede saberse si Google procesó la petición. Una entrada inválida, clave
ausente, cooldown o límite ya alcanzado no suma intentos. Seleccionar Gemini,
cambiar de modelo o marcar el consentimiento tampoco hace llamadas ni consume
presupuesto. Se conservan un intento SDK, 60 segundos de timeout HTTP y Flash-Lite
predeterminado, sin reintentos ni cambios automáticos de modelo.

La interfaz explica el bloqueo y ofrece **Continuar con análisis local** sin otra
llamada a Google. El cooldown no duerme ni bloquea la aplicación: informa del tiempo
restante. Borrar el texto, cambiar ejemplos o cambiar a modo local no reinicia el
consumo Gemini de la sesión ni el global. Abrir otra pestaña puede crear una sesión
nueva y renovar su límite individual, pero comparte el presupuesto global del proceso.

**Límite de esta protección:** el contador global vive únicamente en memoria del
proceso Python de Streamlit. No es distribuido ni persistente, no es una cuota
diaria y no tiene reinicio automático por tiempo. Puede reiniciarse con un reinicio,
despliegue o recarga del proceso/módulo; cada réplica o proceso tiene otro contador.
Cambiar un número de configuración no borra por sí solo el consumo ya registrado
en un proceso que siga vivo. El objeto global guarda un entero, un lock y una
referencia al reloj monotónico; no guarda sesiones, nombres, IP, consultas,
respuestas, claves o datos personales. La sesión solo guarda su contador y la
marca monotónica del último intento admitido.

Para una protección durable entre despliegues o varias réplicas sería necesario
un contador externo con operación atómica, ventanas bien definidas y, si se quieren
cuotas por persona, autenticación. No se ha añadido almacenamiento externo ni
ningún servicio con costes. El límite también es ajeno a la sonda CLI, otros
programas y llamadas de otros proyectos que utilicen la misma clave. Antes de
invitar estudiantes, revisa además acceso, cuotas y facturación en Google y confirma
el comportamiento de la versión desplegada. El estado de publicación se comprueba
en Git; el push no sustituye la validación operativa de Cloud.

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
├── gemini_analyzer.py
├── gemini_limits.py
├── gemini_connectivity_check.py
├── requirements.txt
├── requirements-local.lock.txt
├── README.md
├── AGENTS.md
├── especificacion.md
├── REVISION.md
├── examples/
│   └── error_etl_ficticio.txt
└── tests/
    ├── test_analyzer.py
    ├── test_app.py
    ├── test_deployment.py
    ├── test_gemini_analyzer.py
    ├── test_gemini_limits.py
    ├── test_app_limits.py
    ├── test_connectivity_cli.py
    └── test_app_gemini.py
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

Se utiliza el repositorio existente de DataFlow AI. La publicación de v0.2 en
GitHub y la verificación del despliegue Cloud son operaciones distintas; si Cloud
sigue `main`, un push puede actualizar la aplicación automáticamente. La lectura de secretos está
comprobada con valores ficticios y la excepción real de archivo ausente de
Streamlit: se prioriza `st.secrets['GEMINI_API_KEY']` y se permite el entorno si
falta el archivo o la entrada. No se imprimen valores. La configuración en Cloud
queda a cargo del propietario, según la
[guía oficial de Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

Antes de publicar v0.2:

1. Revisar el diff y la documentación y ejecutar las pruebas automatizadas.
   Las pruebas manuales SQL y ETL con las instrucciones refinadas ya han sido
   confirmadas como satisfactorias por el usuario. El agente no hace llamadas
   reales a Gemini como parte de la publicación.
2. Mantener `.venv`, `.env`, credenciales y `.streamlit/secrets.toml` excluidos;
   incluir `.streamlit/config.toml`, código, pruebas y el ejemplo ficticio.
3. Revisar acceso de usuarios, cuota y facturación. Configurar o conservar la
   entrada privada `GEMINI_API_KEY` en **App settings → Secrets**, sin copiarla
   al repositorio o al chat. El entorno es una alternativa admitida por el código,
   pero Secrets es la vía recomendada en Community Cloud.
4. Confirmar que `DATAFLOW_LOCAL_DIAGNOSTICS` no está activado en Cloud y que
   cualquier configuración previa `GEMINI_MODEL` no elige 3.8 por error; sin ella
   se utiliza Flash-Lite. Mantener Python 3.12 y `requirements.txt` como dependencias.
5. Solo cuando autorices la publicación, crear el commit y subir los cambios.
   Si Cloud sigue la rama `main`, el push puede iniciar la actualización automática;
   prepara los secretos y permisos antes. El estado real de la publicación debe
   comprobarse con Git; estas instrucciones no configuran secretos ni despliegan.
6. Tras el despliegue autorizado, comprobar arranque, modelo visible, borrado de
   entrada, modo local y una llamada Gemini únicamente si se autoriza por separado.
   La validación real en Linux/Cloud y la prueba con navegadores independientes
   quedan pendientes. No se garantiza que las pruebas locales cubran la plataforma.

Para una instalación nueva, los pasos generales son:

1. Accede a [Streamlit Community Cloud](https://share.streamlit.io/) con tu cuenta
   y conecta GitHub, concediendo acceso al repositorio que quieras desplegar.
2. Crea una aplicación y selecciona el repositorio, la rama `main` y el archivo
   principal `app.py`. Si elegiste otra rama, selecciona su nombre real.
3. En las opciones avanzadas, selecciona **Python 3.12**. Para usar solo el
   modo local no hacen falta secretos. Para Gemini, configura la clave únicamente
   en **Secrets** según la sección anterior, tras autorizar su uso.
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
pero debe confirmarse con el despliegue real. Para esta integración solo se han
consultado documentos oficiales y descargado dependencias con autorización.
Las comprobaciones del agente no realizan llamadas reales a Gemini. El resultado
del push no sustituye la verificación de arranque y configuración en Cloud.

## Seguridad
No usar datos personales, consultas confidenciales, contraseñas ni código de clientes. No publicar claves de API.
