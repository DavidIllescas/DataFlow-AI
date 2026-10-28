import streamlit as st
from analyzer import EXAMPLES, MAX_INPUT_CHARS, analyze_local


def load_example():
    st.session_state['input_text'] = EXAMPLES.get(st.session_state['example'], '')


st.set_page_config(page_title='DataFlow AI', page_icon='🔎', layout='centered')
st.title('🔎 DataFlow AI')
st.caption('Asistente educativo para errores de SQL y ETL · Versión 0.1')
st.info('Modo demostración: análisis por reglas locales, sin IA generativa ni conexión a bases de datos.')
st.warning('Utiliza solo ejemplos ficticios. No pegues datos personales, credenciales ni código confidencial.')
mode = st.radio('¿Qué quieres revisar?', ['Consulta SQL', 'Mensaje de error ETL'], horizontal=True)
st.selectbox('Ejemplo opcional', ['Escribir mi propio texto'] + list(EXAMPLES), key='example', on_change=load_example)
text = st.text_area('Pega tu consulta o mensaje de error', key='input_text', height=175, max_chars=MAX_INPUT_CHARS, placeholder='Ej.: SELEC nombre FROM empleados;')
if st.button('Analizar', type='primary', use_container_width=True):
    try:
        result = analyze_local(text, mode)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.subheader(result['categoria'])
        st.write(result['explicacion'])
        st.markdown('**Posibles acciones:**')
        for suggestion in result['sugerencias']:
            st.markdown(f'- {suggestion}')
        st.caption(result['confianza'])
        st.caption('No ejecutes recomendaciones sin revisarlas y probarlas en un entorno de desarrollo.')
st.divider()
with st.expander('Acerca del proyecto'):
    st.write('Prototipo individual del módulo Python para IA. La integración de Gemini está prevista para la siguiente iteración.')
