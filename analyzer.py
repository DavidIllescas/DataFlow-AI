"""Análisis local y determinista de demostración, sin ejecutar SQL."""
import re

MAX_INPUT_CHARS = 4000

EXAMPLES = {
    'Columna inexistente': "Unknown column 'salario' in 'field list'",
    'Error de sintaxis': 'SELEC nombre FROM empleados;',
    'División por cero': 'SELECT ventas / 0 FROM resumen;',
}

def analyze_local(query: str, kind: str = 'Consulta SQL') -> dict:
    if len(query) > MAX_INPUT_CHARS:
        raise ValueError(f'El texto supera el límite de {MAX_INPUT_CHARS} caracteres.')
    text = query.strip()
    if not text:
        raise ValueError('Introduce una consulta SQL o un mensaje de error.')
    low = text.lower()
    if re.search(r'\b(selec|selct)\b', low):
        return {'categoria':'Posible error de sintaxis', 'explicacion':'La palabra SELECT parece estar mal escrita.', 'sugerencias':['Comprueba la palabra clave SELECT.', 'Revisa el resto de la consulta y los nombres de tablas.'], 'confianza':'Regla local: indicio claro'}
    # Reconoce literales cero completos, sin confundir 0.5 con cero.
    if re.search(r'/\s*[+-]?(?:0+(?:\.0*)?|\.0+)(?:e[+-]?\d+)?(?![\w.])', low) or 'division by zero' in low or 'división por cero' in low:
        return {'categoria':'Posible división por cero','explicacion':'Una operación podría estar dividiendo por cero.','sugerencias':['Comprueba el denominador.', 'En motores compatibles, considera NULLIF(denominador, 0).'], 'confianza':'Regla local: indicio claro'}
    if 'does not exist' in low or 'unknown column' in low or 'invalid column' in low:
        return {'categoria':'Columna o tabla no encontrada','explicacion':'El motor indica que algún identificador no existe en el contexto de la consulta.','sugerencias':['Comprueba nombres y alias.', 'Confirma el esquema y los permisos.'], 'confianza':'Regla local: indicio claro'}
    return {'categoria':'Revisión general','explicacion':'No se ha detectado un patrón conocido con las reglas locales. Esto no permite confirmar si la consulta o el proceso contiene errores ni si es correcto.', 'sugerencias':['Revisa sintaxis, identificadores y tipos de datos.', 'Consulta la documentación del motor SQL o de la herramienta ETL que utilizas.', 'Comprueba los tipos de datos antes de realizar operaciones y conversiones.'], 'confianza':'No se puede determinar con reglas locales'}
