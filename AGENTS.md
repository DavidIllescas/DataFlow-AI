# Instrucciones para agentes — DataFlow AI

- Objetivo: aplicación en español para principiantes que explica errores de SQL/ETL mediante ejemplos ficticios.
- Mantener las tres funciones previstas: explicación, soluciones posibles, consejos de mejora.
- No ejecutar SQL proporcionado por usuarios ni conectar bases de datos.
- No registrar ni almacenar textos pegados; no pedir datos personales o secretos.
- Claves de API exclusivamente mediante secretos de Streamlit o variables de entorno; nunca hardcodear ni subir al repositorio.
- Mostrar los límites del análisis local y de cualquier sugerencia de IA: no garantizar corrección.
- Mantener interfaz clara para usuarios no técnicos, errores amistosos, entradas limitadas y pruebas.
- Si se añade Gemini, comprobar fallos de red, cuotas y claves ausentes sin exponer detalles de secretos.
- Ejecutar `python -m unittest discover -s tests` al modificar reglas locales.
