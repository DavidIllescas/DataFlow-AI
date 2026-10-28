import streamlit as st
from analyzer import EXAMPLES, MAX_INPUT_CHARS, analyze_local
from gemini_analyzer import TIMEOUT_MS, GeminiError, analyze_gemini, get_api_key, local_diagnostics_enabled, resolve_model


def load_example():
    st.session_state['input_text'] = EXAMPLES.get(st.session_state['example'], '')
    revoke_permission()


def revoke_permission():
    st.session_state['gemini_permission'] = False
    st.session_state.pop('gemini_error', None)
    st.session_state.pop('gemini_diagnostic', None)


def clear_input():
    st.session_state['input_text'] = ''
    st.session_state['example'] = 'Escribir mi propio texto'
    revoke_permission()


def show_local_result(result):
    st.subheader(result['categoria'])
    st.write(result['explicacion'])
    st.markdown('**Posibles acciones:**')
    for suggestion in result['sugerencias']:
        st.markdown(f'- {suggestion}')
    st.caption(result['confianza'])
    st.caption('No ejecutes recomendaciones sin revisarlas y probarlas en un entorno de desarrollo.')


def show_gemini_result(result):
    st.subheader('Resultado de Gemini')
    # El contenido del modelo se muestra como texto: no carga enlaces ni imágenes.
    st.text(result['categoria'])
    st.text(result['explicacion'])
    for field, label in (
        ('hechos', 'Observaciones del texto'), ('hipotesis', 'Hipótesis por validar'),
        ('correcciones', 'Posibles correcciones'), ('recomendaciones', 'Recomendaciones de mejora'),
    ):
        st.markdown(f'**{label}:**')
        for item in result[field]:
            st.text(f'• {item}')
        if not result[field]:
            st.text('Sin elementos indicados.')
    st.text(result['limitaciones'])
    st.caption('Sugerencias generadas por IA: pueden ser incorrectas. No se ha ejecutado SQL ni verificado ningún esquema. Valídalas antes de aplicarlas.')


st.set_page_config(page_title='DataFlow AI', page_icon='🔎', layout='centered')
diagnostic_mode = local_diagnostics_enabled(st.get_option('server.address'))
st.title('🔎 DataFlow AI')
st.caption('Asistente educativo para errores de SQL y ETL · Versión 0.2')
st.warning('Utiliza solo ejemplos ficticios. No pegues datos personales, credenciales ni código confidencial.')
mode = st.radio('¿Qué quieres revisar?', ['Consulta SQL', 'Mensaje de error ETL'], horizontal=True, on_change=revoke_permission)
engine = st.radio('Sistema de análisis', ['Reglas locales', 'Gemini (opcional)'], key='engine', on_change=revoke_permission)
selected_model = None
if engine == 'Reglas locales':
    st.info('Modo demostración: análisis por reglas locales, sin IA generativa ni conexión a bases de datos.')
else:
    try:
        selected_model = resolve_model()
        st.info(f'Análisis inteligente con {selected_model}. Solo se envía el texto al pulsar Analizar con tu autorización.')
    except GeminiError as exc:
        st.error(str(exc))
    st.caption(f'Tiempo de espera de red configurado: {TIMEOUT_MS // 1000} s. Un solo intento, sin reintentos ni cambios automáticos de modelo.')
st.selectbox('Ejemplo opcional', ['Escribir mi propio texto'] + list(EXAMPLES), key='example', on_change=load_example)
text = st.text_area('Pega tu consulta o mensaje de error', key='input_text', height=175, max_chars=MAX_INPUT_CHARS, placeholder='Ej.: SELEC nombre FROM empleados;', on_change=revoke_permission)
permission = False
if engine == 'Gemini (opcional)':
    st.warning('El texto se enviará a Google y estará sujeto a sus condiciones de tratamiento de datos. La API puede consumir cuota o generar costes. No envíes información empresarial confidencial.')
    permission = st.checkbox('Confirmo que es un ejemplo ficticio y autorizo enviarlo a Google, con el posible consumo de cuota o coste.', key='gemini_permission')
if st.button('Analizar', type='primary', use_container_width=True):
    st.session_state.pop('gemini_error', None)
    st.session_state.pop('gemini_diagnostic', None)
    try:
        if engine == 'Reglas locales':
            show_local_result(analyze_local(text, mode))
        elif not permission:
            st.warning('Autoriza el envío del ejemplo ficticio para utilizar Gemini, o selecciona Reglas locales.')
        elif selected_model is None:
            st.warning('Corrige la configuración del modelo o utiliza Reglas locales. No se ha enviado el texto.')
        else:
            with st.spinner('Consultando Gemini…'):
                result = analyze_gemini(text, mode, api_key=get_api_key(st.secrets), model=selected_model)
            show_gemini_result(result)
    except ValueError as exc:
        st.error(str(exc))
    except GeminiError as exc:
        if selected_model is not None:
            exc.diagnostic['model'] = selected_model
        st.session_state['gemini_error'] = str(exc)
        if diagnostic_mode:
            st.session_state['gemini_diagnostic'] = exc.diagnostic
if engine == 'Gemini (opcional)' and st.session_state.get('gemini_error'):
    st.error(st.session_state['gemini_error'])
    if diagnostic_mode and st.session_state.get('gemini_diagnostic'):
        with st.expander('Diagnóstico técnico local (saneado)'):
            st.json(st.session_state['gemini_diagnostic'])
    st.info('El análisis de Gemini ha fallado. Puedes analizar el texto actual con reglas locales, sin enviarlo de nuevo a Google.')
    if st.button('Continuar con análisis local'):
        try:
            show_local_result(analyze_local(text, mode))
        except ValueError as exc:
            st.error(str(exc))
st.button('Borrar texto y resultado', on_click=clear_input)
st.divider()
with st.expander('Acerca del proyecto'):
    st.write('Prototipo educativo: reglas locales de la versión 0.1 y análisis opcional con Gemini. Las sugerencias requieren revisión humana.')
