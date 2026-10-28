# Autoprueba, validación y mejora — DataFlow AI Studio

Versión pública de referencia: **v0.3**. Este documento recoge el cierre de
autoprueba, validación y mejora del proyecto.

- [Repositorio oficial](https://github.com/DavidIllescas/DataFlow-AI).
- [Aplicación pública](https://dataflow-ai-davidillescas.streamlit.app/).

## Objetivo

Documentar las autopruebas, la validación y la mejora de DataFlow AI Studio
durante las semanas 2 y 3 del proyecto, manteniendo las funcionalidades
educativas de análisis SQL/ETL. Se distinguen los hechos comunicados por el usuario,
las verificaciones automatizadas locales y las limitaciones todavía abiertas.

## Pruebas

| Actividad | Tipo y procedencia de la evidencia | Resultado documentado |
| --- | --- | --- |
| Análisis SQL y ETL con Gemini de v0.2 | Pruebas manuales previas confirmadas por el usuario | Resultados satisfactorios; no se han repetido durante este cierre. |
| Revisión del rediseño v0.3 | Verificación manual del usuario | Los seis aspectos de la interfaz revisados funcionaron correctamente, según su confirmación. |
| Release v0.3 | Verificación automatizada local registrada en REVISION | 113 pruebas correctas al preparar la publicación. |
| Cierre documental, incluido diagnóstico 503 | Ejecución automatizada local repetida antes de publicar | 121 pruebas correctas, sin fallos ni omisiones. |

Las comprobaciones manuales son las comunicadas por el usuario; no se han repetido
durante esta revisión documental. Las pruebas automatizadas usan mocks y
transporte simulado para Gemini: no requieren claves reales ni consumen cuota.

Entre los casos propios del proyecto figuran la consulta SQL ficticia
`SELECT importe / 0 FROM ventas;` y el [ejemplo ETL ficticio](../examples/error_etl_ficticio.txt)
de conversión de `N/D` a decimal, con motor y herramienta no especificados.
Las pruebas locales también cubren entradas vacías, exceso de longitud, ejemplos
de sintaxis y columnas no encontradas, y consultas sin patrones reconocidos.

## Resultados

La versión pública actual es v0.3, según el estado comunicado por el usuario, y
su release está registrado en el historial local de Git. La aplicación dispone
de análisis local por reglas y Gemini opcional, con autorización explícita de
envío, borrado, ejemplos SQL/ETL, recuperación local y límites de solicitudes.
El modo local permanece seleccionado por defecto.

Las 121 pruebas corresponden al árbol local actual: incluyen ocho regresiones
añadidas después del release para estudiar configuración y HTTP 503. Esa ampliación
y la sonda administrativa se incluyen en este cierre documental. Su incorporación
al repositorio no certifica su despliegue en Cloud.

## Problema detectado

En la evaluación propia de usabilidad se consideró que la interfaz anterior tenía
una apariencia demasiado genérica para una herramienta educativa de ingeniería de
datos. Se planteó una identidad visual más diferenciada y una organización del
editor y los resultados que facilitara su lectura. Es una valoración de diseño;
no se han medido mejoras de tiempo, satisfacción o rendimiento.

Existe además una limitación técnica independiente: Gemini puede devolver
**HTTP 503**, como ocurrió en la aplicación pública según el usuario. Se muestra
un mensaje de indisponibilidad temporal y se ofrece **Continuar con análisis
local**, sin reenviar el texto a Google. Esta recuperación es una alternativa
explícita; no convierte el fallo remoto en un análisis Gemini satisfactorio.

El éxito previo en local y un 503 posterior en Cloud no demuestran una causa ligada
a Windows/Linux, a las credenciales o al esquema JSON. La causa específica de la
instancia remota sigue sin confirmarse. El diagnóstico y sus límites se desarrollan
en [README](../README.md#diagnosticar-http-503-local-frente-a-cloud-sin-repetir-solicitudes).

## Mejora implementada

La evolución de **DataFlow AI v0.2 a DataFlow AI Studio v0.3 nació de una evaluación
propia de usabilidad**. La decisión de reorganizar el editor y los resultados y
renovar la identidad visual responde a esa revisión del propio proyecto.

La mejora ya implementada introduce tema oscuro, identidad compacta, navegación
lateral, editor SQL/ETL monoespaciado y consola de resultados. Distingue diagnóstico,
observaciones, hipótesis, correcciones y recomendaciones; conserva la selección
Local/Gemini y los controles de autorización, privacidad y uso. La revisión manual
confirmada respalda su funcionamiento, sin constituir un estudio de usuarios.

El rediseño mejora la presentación; no elimina la dependencia de la disponibilidad
de Gemini. Se conserva un único intento por solicitud, sin reintentos automáticos
ni cambios automáticos de modelo. La propuesta de reintento documentada en README
es una posibilidad futura, no una funcionalidad implementada.

## Verificación

Antes de publicar este cierre se repitió desde la raíz interior del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Resultado registrado: **121 pruebas correctas** en el entorno local Windows.
Las comprobaciones manuales previas no se repitieron. También pasaron `pip check`,
compilación e importación en proceso limpio. Un servidor Streamlit temporal
respondió HTTP 200 y salud `ok`; se cerró al terminar.
La batería cubre reglas y validación de entrada, flujos de interfaz, consentimiento,
borrado, ejemplos, selección de modelo, fallos simulados del servicio, recuperación
local, límites, concurrencia, aislamiento de sesiones y configuración de despliegue.
Incluye la importación de los módulos reales en un proceso Python limpio para
prevenir la regresión de `validate_gemini_input`.

La comparación local con Git confirma que `app.py`, `analyzer.py`,
`gemini_analyzer.py`, `gemini_limits.py`, CSS, configuración de Streamlit y
dependencias no cambian durante este cierre. Los cambios previos de la sonda y sus
pruebas se incluyen tras su revisión: ofrecen metadatos offline saneados sin
exponer un diagnóstico público ni modificar las peticiones del analizador.

Se revisó el documento para excluir credenciales, datos personales innecesarios,
rutas privadas e información confidencial. No se consultaron Secrets, no se
realizaron llamadas reales a Gemini. La publicación en Git se realiza únicamente
tras autorización y verificación del cierre documental.
La comprobación automatizada local no certifica la disponibilidad futura del
servicio ni sustituye una verificación técnica del contenedor remoto.

## Conclusión

Quedan documentadas las autopruebas SQL/ETL, las verificaciones del proyecto y
la mejora propia de usabilidad implementada en v0.3. La revisión manual
comunicada por el usuario y las pruebas automatizadas locales aportan evidencias
diferenciadas del estado del proyecto.

El cierre documenta la validación y mejora de DataFlow AI Studio, con HTTP 503
identificado como limitación conocida y recuperación local disponible. La causa
remota específica sigue abierta; no se implementan reintentos automáticos.
