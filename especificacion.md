# Especificación de DataFlow AI — v0.1

## 1. Problema
Diagnosticar errores de consultas SQL y procesos ETL puede resultar lento para profesionales junior.

## 2. Usuario y funcionalidades
Usuarios: desarrolladores junior e ingenieros de datos. Funcionalidades previstas: (1) explicar errores, (2) sugerir soluciones, (3) recomendar mejoras SQL. La versión 0 solo cubre un subconjunto de errores mediante reglas locales.

## 3. Entradas y salidas
Entrada: texto ficticio de consulta SQL o error ETL (máximo 4000 caracteres). Salida: categoría, explicación, sugerencias y limitación/confianza de la detección.

## 4. Pieza de IA
Plan: API de Gemini, por su capacidad de interpretar texto técnico y generar explicaciones. La versión 0 no hace llamadas al modelo.

## 5. Flujo principal
Seleccionar tipo de entrada → escribir o elegir ejemplo → pulsar Analizar → leer resultado → validar las sugerencias antes de aplicarlas.

## 6. Restricciones
Coste cero dentro de cuotas gratuitas; no subir secretos; no usar datos personales reales ni datos de clientes; no ejecutar SQL; no conservar entradas.

## 7. Casos de prueba
- `SELEC nombre FROM empleados;`: detectar posible error de sintaxis.
- `SELECT ventas / 0 FROM resumen;`: detectar posible división por cero.
- Cadena vacía: validación legible.
- Consulta sin patrón: no asegurar que sea correcta.
- Más de 4000 caracteres: rechazar.

## 8. Fuera de alcance
Conexión a sistemas corporativos, ejecución de consultas, cambios automáticos de código, garantía de precisión y análisis de información sensible.

## 9. Despliegue
Repositorio de GitHub con `app.py`, `analyzer.py`, `requirements.txt`; desplegar desde Streamlit Community Cloud. Configurar Gemini en secretos solo en futura fase.
