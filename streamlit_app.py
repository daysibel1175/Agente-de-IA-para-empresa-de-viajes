from __future__ import annotations

import os

import streamlit as st

from app import build_agent


st.set_page_config(page_title="Agente IA Viajes", page_icon="✈️", layout="wide")

st.title("🤖✈️ Agente de IA para Viajes (Carrarurquía)")
st.caption("Consulta documentos internos (RAG) y web en un solo chat.")


def sync_secrets_to_env() -> None:
    try:
        secrets_dict = dict(st.secrets)
    except Exception:
        # Si secrets.toml está ausente o mal formateado, seguimos con variables del .env
        return

    for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "SERPAPI_API_KEY", "PDF_DIR"]:
        value = secrets_dict.get(key)
        if value and not os.getenv(key):
            os.environ[key] = str(value)

    if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


sync_secrets_to_env()


def api_key_ref() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return "no-configurada"
    if len(key) <= 10:
        return "configurada"
    return f"{key[:4]}...{key[-6:]}"


@st.cache_resource
def get_agent():
    return build_agent(rebuild_index=False)


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.agent_blocked = False


with st.sidebar:
    st.header("Configuración")
    st.write("Asegúrate de tener configuradas las variables en tu archivo .env.")
    if st.button("Reconstruir índice FAISS"):
        with st.spinner("Reconstruyendo índice, esto puede tardar..."):
            build_agent(rebuild_index=True)
            st.success("Índice reconstruido con éxito.")
            st.cache_resource.clear()

    if st.button("Limpiar chat"):
        reset_chat()
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_blocked" not in st.session_state:
    st.session_state.agent_blocked = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

pregunta = st.chat_input("Escribe tu pregunta sobre viajes...")

if pregunta:
    if st.session_state.agent_blocked:
        st.warning("El agente quedó bloqueado por un error previo. Pulsa 'Limpiar chat' para reintentar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                agente = get_agent()
                resultado = agente.invoke(
                    {
                        "pregunta": pregunta,
                        "fuente": "",
                        "contexto": "",
                        "respuesta": "",
                    }
                )

                fuente = resultado.get("fuente", "N/D")
                respuesta = resultado.get("respuesta", "No se pudo generar respuesta.")

                st.markdown(f"**Fuente usada:** {fuente}")
                st.markdown(respuesta)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"**Fuente usada:** {fuente}\n\n{respuesta}",
                    }
                )
            except Exception as exc:
                error_msg = f"Error ejecutando el agente: {exc}\n\nReferencia API key: {api_key_ref()}"
                st.error(error_msg)
                st.session_state.agent_blocked = True
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
