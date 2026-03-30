from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    pregunta: str
    fuente: str
    contexto: str
    respuesta: str


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_PDF_DIR = PROJECT_ROOT / "Agente de IA Carrarurquia"
INDEX_DIR = PROJECT_ROOT / "data" / "faiss_index"


load_dotenv()


def _get_google_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _validate_env() -> None:
    missing = []
    if not _get_google_api_key():
        missing.append("GEMINI_API_KEY/GOOGLE_API_KEY")
    if not os.getenv("SERPAPI_API_KEY"):
        missing.append("SERPAPI_API_KEY")

    if missing:
        raise RuntimeError(
            "Faltan variables de entorno: "
            + ", ".join(missing)
            + ". Crea un archivo .env basado en .env.example"
        )


def _resolve_pdf_dir() -> Path:
    configured = os.getenv("PDF_DIR")
    pdf_dir = Path(configured) if configured else DEFAULT_PDF_DIR
    if not pdf_dir.is_absolute():
        pdf_dir = (PROJECT_ROOT / pdf_dir).resolve()
    if not pdf_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de PDFs: {pdf_dir}")
    return pdf_dir


def _get_index_dir() -> Path:
    """Devuelve una ruta segura para FAISS (evita problemas con rutas Unicode en Windows)."""
    configured = os.getenv("FAISS_INDEX_DIR")
    if configured:
        index_dir = Path(configured)
        if not index_dir.is_absolute():
            index_dir = (PROJECT_ROOT / index_dir).resolve()
        return index_dir

    # Intento ruta del proyecto
    try:
        str(INDEX_DIR).encode("ascii")
        return INDEX_DIR
    except UnicodeEncodeError:
        # Fallback para Windows/FAISS cuando el path contiene caracteres no ASCII
        base_temp = Path(os.getenv("LOCALAPPDATA", tempfile.gettempdir()))
        return base_temp / "agente_ia_viajes" / "faiss_index"


def _load_documents(pdf_dir: Path):
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise RuntimeError(f"No se encontraron PDFs en {pdf_dir}")

    documents = []
    for pdf in pdf_files:
        loader = PyPDFLoader(str(pdf))
        documents.extend(loader.load())
    return documents


def _build_or_load_vectorstore(embeddings: GoogleGenerativeAIEmbeddings, rebuild: bool = False):
    index_dir = _get_index_dir()
    index_faiss = index_dir / "index.faiss"
    index_pkl = index_dir / "index.pkl"

    if not rebuild and index_faiss.exists() and index_pkl.exists():
        return FAISS.load_local(
            str(index_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    pdf_dir = _resolve_pdf_dir()
    documents = _load_documents(pdf_dir)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    index_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_dir))
    return vectorstore


def get_embeddings(google_api_key: str | None) -> GoogleGenerativeAIEmbeddings:
    """Prueba modelos en orden y usa el primero disponible."""
    modelos_a_probar = [
        "models/gemini-embedding-001",
        "models/text-embedding-004",
        "models/embedding-001",
        "embedding-001",
    ]
    errores: list[str] = []

    for nombre_modelo in modelos_a_probar:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model=nombre_modelo,
                google_api_key=google_api_key,
            )
            embeddings.embed_query("test")
            if nombre_modelo != "models/gemini-embedding-001":
                print(f"Aviso: usando fallback de embeddings: {nombre_modelo}")
            return embeddings
        except Exception as e:
            errores.append(f"{nombre_modelo}: {e}")
            continue

    raise RuntimeError(
        "No se pudo inicializar ningún modelo de embeddings. "
        "Revisa tu API key/permisos. Detalles: "
        + " | ".join(errores)
    )


def build_agent(rebuild_index: bool = False):
    _validate_env()
    google_api_key = _get_google_api_key()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        google_api_key=google_api_key,
        max_retries=0,
    )
    embeddings = get_embeddings(google_api_key)

    vectorstore = _build_or_load_vectorstore(embeddings, rebuild=rebuild_index)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    web = SerpAPIWrapper()

    def nodo_agente(state: AgentState):
        prompt = f"""Eres un clasificador. Decide si la pregunta debe responderse con documentos locales (RAG) o con web.
Responde SOLO con 'RAG' o 'Web'.

Pregunta: {state['pregunta']}
"""
        decision = llm.invoke(prompt).content.strip()
        fuente = "RAG" if "RAG" in decision.upper() else "Web"
        return {"fuente": fuente}

    def nodo_rag(state: AgentState):
        docs = retriever.invoke(state["pregunta"])
        contexto = "\n\n---\n\n".join(d.page_content for d in docs)
        return {"contexto": contexto}

    def nodo_web(state: AgentState):
        contexto = web.run(state["pregunta"])
        return {"contexto": contexto}

    def nodo_markdown(state: AgentState):
        prompt = f"""Eres un asistente experto de una agencia de viajes en Turquía.
Responde en español y en formato Markdown.
Incluye: título (#), subtítulos (##), listas y recomendaciones claras.

Fuente: {state['fuente']}
Contexto:
{state['contexto']}

Pregunta: {state['pregunta']}
"""
        respuesta = llm.invoke(prompt).content
        return {"respuesta": respuesta}

    def decidir_fuente(state: AgentState):
        return "if_rag" if state["fuente"] == "RAG" else "if_web"

    graph = StateGraph(AgentState)
    graph.add_node("Agente", nodo_agente)
    graph.add_node("RAG", nodo_rag)
    graph.add_node("Web", nodo_web)
    graph.add_node("Markdown", nodo_markdown)

    graph.add_edge(START, "Agente")
    graph.add_conditional_edges(
        "Agente",
        decidir_fuente,
        {
            "if_rag": "RAG",
            "if_web": "Web",
        },
    )
    graph.add_edge("RAG", "Markdown")
    graph.add_edge("Web", "Markdown")
    graph.add_edge("Markdown", END)

    return graph.compile()


def ejecutar_agente(pregunta: str, rebuild_index: bool = False) -> dict:
    agente = build_agent(rebuild_index=rebuild_index)
    return agente.invoke(
        {
            "pregunta": pregunta,
            "fuente": "",
            "contexto": "",
            "respuesta": "",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente de IA para agencia de viajes (RAG + Web)")
    parser.add_argument("--pregunta", type=str, help="Pregunta para el agente")
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Reconstruye el índice FAISS desde los PDFs",
    )
    args = parser.parse_args()

    if args.pregunta:
        result = ejecutar_agente(args.pregunta, rebuild_index=args.rebuild_index)
        print("=" * 60)
        print(f"Fuente utilizada: {result['fuente']}")
        print("=" * 60)
        print(result["respuesta"])
        return

    print("Modo interactivo. Escribe 'salir' para terminar.\n")
    while True:
        pregunta = input("Tu pregunta: ").strip()
        if not pregunta or pregunta.lower() in {"salir", "exit", "quit"}:
            break
        result = ejecutar_agente(pregunta, rebuild_index=False)
        print("=" * 60)
        print(f"Fuente utilizada: {result['fuente']}")
        print("=" * 60)
        print(result["respuesta"])
        print()


if __name__ == "__main__":
    main()
