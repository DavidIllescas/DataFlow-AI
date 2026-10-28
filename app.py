from pathlib import Path

import streamlit as st
from analyzer import EXAMPLES, MAX_INPUT_CHARS, analyze_local
from gemini_analyzer import TIMEOUT_MS, GeminiError, analyze_gemini, get_api_key, local_diagnostics_enabled, resolve_model, validate_gemini_input
from gemini_limits import LimitConfigError, QuotaExceeded, SessionUsage, get_limiter, load_limits


def load_example():
    st.session_state['input_text'] = EXAMPLES.get(st.session_state['example'], '')
    revoke_permission()


def revoke_permission():
    st.session_state['gemini_permission'] = False
    st.session_state.pop('gemini_error', None)
    st.session_state.pop('gemini_diagnostic', None)
    st.session_state.pop('gemini_limit_error', None)


def clear_input():
    st.session_state['input_text'] = ''
    st.session_state['example'] = 'Escribir mi propio texto'
    revoke_permission()


def load_library_example(name, text, kind):
    st.session_state['input_text'] = text
    st.session_state['input_kind'] = kind
    st.session_state['example'] = name if name in EXAMPLES else 'Escribir mi propio texto'
    revoke_permission()


def analyze_with_limits(text, kind, model):
    validate_gemini_input(text, kind)
    limits = load_limits()
    usage = st.session_state['gemini_usage']
    limiter = get_limiter()
    limiter.check(usage, limits)
    api_key = get_api_key(st.secrets)
    if not api_key:
        raise GeminiError('Falta configurar GEMINI_API_KEY en los secretos o en el entorno.', model=model)
    # Otra sesión puede consumir el último intento mientras se lee configuración:
    # reserve vuelve a comprobar todo bajo el mismo lock, sin hacer aún ninguna red.
    limiter.reserve(usage, limits)
    return analyze_gemini(text, kind, api_key=api_key, model=model)


def show_local_result(result):
    st.caption('RESULTADO / REGLAS LOCALES')
    st.subheader(result['categoria'])
    st.markdown('**Diagnóstico**')
    st.write(result['explicacion'])
    st.markdown('**Observaciones del texto**')
    st.text('El modo local detecta patrones; no genera una lista de observaciones verificadas.')
    st.markdown('**Hipótesis por validar**')
    st.text('El modo local no genera hipótesis contextuales ni verifica el esquema.')
    st.markdown('**Posibles correcciones**')
    for suggestion in result['sugerencias']:
        st.markdown(f'- {suggestion}')
    st.caption(result['confianza'])
    st.markdown('**Recomendaciones**')
    st.caption('No ejecutes recomendaciones sin revisarlas y probarlas en un entorno de desarrollo.')


def show_gemini_result(result):
    st.caption('RESULTADO / GEMINI')
    st.subheader('Resultado de Gemini')
    # El contenido del modelo se muestra como texto: no carga enlaces ni imágenes.
    st.text(result['categoria'])
    st.markdown('**Diagnóstico**')
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


st.set_page_config(page_title='DataFlow AI Studio', layout='wide', initial_sidebar_state='auto')
st.html(Path(__file__).resolve().parent / 'assets' / 'studio.css')
diagnostic_mode = local_diagnostics_enabled(st.get_option('server.address'))

with st.sidebar:
    st.html('''<div class="studio-side-brand"><span class="studio-monogram" aria-hidden="true">DF</span>
    <div><strong>DataFlow AI</strong><small>STUDIO / v0.3</small></div></div>
    <nav class="studio-nav" aria-label="Navegación del estudio">
    <a href="#analisis"><span>01</span> Análisis</a>
    <a href="#ejemplos"><span>02</span> Ejemplos</a>
    <a href="#proyecto"><span>03</span> Proyecto</a></nav>''')
    st.divider()
    st.caption('ENTORNO EDUCATIVO')
    st.write('SQL / ETL')
    st.caption('Reglas locales sin conexión.\n\nGemini solo con tu autorización.')
    st.divider()
    st.caption('PRIVACIDAD')
    st.write('Trabaja con ejemplos ficticios.')
    st.caption('Sin ejecución de SQL ni conexión a tus bases de datos.')

with st.container(key='studio_shell'):
    st.html('''<header class="studio-header"><div class="studio-header-copy">
    <p class="studio-eyebrow">DATA ENGINEERING WORKSPACE</p>
    <h1>DataFlow AI <span>Studio</span></h1><p class="studio-subtitle">SQL Intelligence Studio</p>
    </div><div class="studio-release">VERSIÓN <span>v0.3</span></div></header>''')
    st.caption('Solo ejemplos ficticios. No introduzcas datos personales, credenciales ni código confidencial.')
    st.header('Espacio de análisis', anchor='analisis')
    editor, results = st.columns([1.06, 1], gap='medium', vertical_alignment='top')

    with editor, st.container(border=True, key='studio_editor'):
        st.html('<div class="studio-panel-bar"><span>01 / EDITOR</span><span>SQL · ETL</span></div>')
        mode = st.radio('Tipo de entrada', ['Consulta SQL', 'Mensaje de error ETL'], key='input_kind', horizontal=True, on_change=revoke_permission)
        engine = st.radio('Sistema de análisis', ['Reglas locales', 'Gemini (opcional)'], key='engine', horizontal=True, on_change=revoke_permission)
        selected_model = None
        if engine == 'Reglas locales':
            st.info('Local activo · análisis ilimitado por reglas, sin enviar datos a Google.')
        else:
            if 'gemini_usage' not in st.session_state:
                st.session_state['gemini_usage'] = SessionUsage()
            try:
                selected_model = resolve_model()
                st.info(f'Modelo activo: {selected_model}. Solo se envía el texto al pulsar Analizar con tu autorización.')
            except GeminiError as exc:
                st.error(str(exc))
            st.caption(f'Espera de red: {TIMEOUT_MS // 1000} s · Un solo intento · Sin cambio automático de modelo')
            try:
                limits = load_limits()
                st.caption(f'Límite de sesión: {limits.session_limit} intentos · Cooldown: {limits.cooldown_seconds} s · Presupuesto compartido: {limits.global_limit} por proceso, no diario.')
            except LimitConfigError as exc:
                st.warning(str(exc))
        st.selectbox('Ejemplo opcional', ['Escribir mi propio texto'] + list(EXAMPLES), key='example', on_change=load_example)
        st.caption('consulta.sql' if mode == 'Consulta SQL' else 'mensaje.etl')
        text = st.text_area('Pega tu consulta o mensaje de error', key='input_text', height=300, max_chars=MAX_INPUT_CHARS, placeholder='SELEC nombre FROM empleados;', on_change=revoke_permission)
        st.caption(f'{len(text):,} / {MAX_INPUT_CHARS:,} caracteres · El texto nunca se ejecuta')
        permission = False
        if engine == 'Gemini (opcional)':
            st.warning('Envío a Google · Puede consumir cuota o generar costes. No envíes información empresarial confidencial.')
            permission = st.checkbox('Confirmo que es un ejemplo ficticio y autorizo enviarlo a Google, con el posible consumo de cuota o coste.', key='gemini_permission')
        with st.container(horizontal=True, gap='small', key='studio_actions'):
            submitted = st.button('Analizar', key='analyze', type='primary', width='stretch')
            st.button('Borrar texto y resultado', key='clear_input', on_click=clear_input, width='stretch')
        if engine == 'Gemini (opcional)':
            # Se muestra después de procesar la acción con un placeholder nativo.
            usage_caption = st.empty()

    with results, st.container(border=True, key='studio_results'):
        st.html('<div class="studio-panel-bar"><span>02 / CONSOLA DE RESULTADOS</span><span>SOLO LECTURA</span></div>')
        if submitted:
            st.session_state.pop('gemini_error', None)
            st.session_state.pop('gemini_diagnostic', None)
            st.session_state.pop('gemini_limit_error', None)
            try:
                if engine == 'Reglas locales':
                    show_local_result(analyze_local(text, mode))
                elif not permission:
                    st.warning('Autoriza el envío del ejemplo ficticio para utilizar Gemini, o selecciona Reglas locales.')
                elif selected_model is None:
                    st.warning('Corrige la configuración del modelo o utiliza Reglas locales. No se ha enviado el texto.')
                else:
                    with st.spinner('Consultando Gemini…'):
                        result = analyze_with_limits(text, mode, selected_model)
                    show_gemini_result(result)
            except (QuotaExceeded, LimitConfigError) as exc:
                st.session_state['gemini_limit_error'] = str(exc)
            except ValueError as exc:
                st.error(str(exc))
            except GeminiError as exc:
                if selected_model is not None:
                    exc.diagnostic['model'] = selected_model
                st.session_state['gemini_error'] = str(exc)
                if diagnostic_mode:
                    st.session_state['gemini_diagnostic'] = exc.diagnostic
        if engine == 'Gemini (opcional)' and (st.session_state.get('gemini_error') or st.session_state.get('gemini_limit_error')):
            if st.session_state.get('gemini_limit_error'):
                st.warning(st.session_state['gemini_limit_error'])
                st.info('No se ha hecho ninguna llamada a Gemini para este intento bloqueado. El análisis local sigue disponible sin límite de uso.')
            else:
                st.error(st.session_state['gemini_error'])
                st.info('El análisis de Gemini ha fallado. Puedes analizar el texto actual con reglas locales, sin enviarlo de nuevo a Google.')
            if diagnostic_mode and st.session_state.get('gemini_diagnostic'):
                with st.expander('Diagnóstico técnico local (saneado)'):
                    st.json(st.session_state['gemini_diagnostic'])
            if st.button('Continuar con análisis local', key='use_local', width='stretch'):
                try:
                    show_local_result(analyze_local(text, mode))
                except ValueError as exc:
                    st.error(str(exc))
        elif not submitted:
            st.html('''<div class="studio-empty"><div class="studio-console-glyph" aria-hidden="true">&gt;_</div>
            <p class="studio-eyebrow">CONSOLA LISTA</p><h3>Del error a la siguiente acción.</h3>
            <p>Escribe una consulta o un mensaje ETL en el editor.<br>El diagnóstico aparecerá aquí.</p>
            <div class="studio-empty-steps"><span>01 · Explica</span><span>02 · Corrige</span><span>03 · Mejora</span></div>
            <small>Sin ejecutar SQL. Sin asumir tu esquema.</small></div>''')
        st.caption('Herramienta educativa · Valida cualquier recomendación antes de aplicarla.')
    if engine == 'Gemini (opcional)':
        usage_caption.caption(f'Intentos consumidos en esta sesión: {st.session_state["gemini_usage"].used}. Borrar no reinicia el contador.')

    st.header('Biblioteca de ejemplos', anchor='ejemplos')
    st.caption('Casos ficticios, listos para cargar. Elegir un ejemplo no llama a Gemini ni consume cuota.')
    with st.expander('Explorar ejemplos SQL y ETL'):
        examples = list(EXAMPLES.items()) + [('Conversión ETL', (Path(__file__).resolve().parent / 'examples' / 'error_etl_ficticio.txt').read_text(encoding='utf-8'))]
        for index, (name, sample) in enumerate(examples):
            with st.container(border=True):
                st.markdown(f'**{name}**')
                st.code(sample, language='sql' if name != 'Conversión ETL' else 'text', wrap_lines=True)
                st.button(f'Cargar {name}', key=f'library_{index}', on_click=load_library_example, args=(name, sample, 'Mensaje de error ETL' if name == 'Conversión ETL' else 'Consulta SQL'))

    st.header('Sobre el estudio', anchor='proyecto')
    with st.expander('Acerca del proyecto'):
        st.write('DataFlow AI Studio v0.3 · Entorno educativo para comprender errores SQL y ETL.')
        st.write('Reglas locales ilimitadas y Gemini opcional. Las respuestas separan observaciones, hipótesis y propuestas, y requieren revisión humana.')
        st.caption('El presupuesto Gemini se comparte en memoria por proceso: no es persistente ni distribuido y puede reiniciarse al desplegar. No se guardan consultas ni respuestas en archivos.')
    st.caption('DATAFLOW AI STUDIO / v0.3 · Diseñado para aprender a diagnosticar.')
