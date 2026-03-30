# Agente de IA para Agencia de Viajes (Carrarurquía)

Proyecto convertido de notebook a estructura de proyecto Python, listo para subir a GitHub.

## Qué incluye

- `app.py`: aplicación principal (RAG + LangGraph + Web con SerpAPI)
- `requirements.txt`: dependencias del proyecto
- `.env.example`: plantilla de variables de entorno
- `.gitignore`: exclusiones para entorno local y cachés
- `Agente de IA Carrarurquia/`: carpeta con los PDFs para RAG

## Requisitos

1. Python 3.10+
2. API keys:
	- `GEMINI_API_KEY`
	- `SERPAPI_API_KEY`

## Instalación

1. Crea y activa entorno virtual.
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Crea tu `.env` a partir de `.env.example` y completa claves.

## Uso

### Modo pregunta única

```bash
python app.py --pregunta "¿Cuál es el paquete más económico?"
```

### Modo interactivo

```bash
python app.py
```

### Chat para usuario final (Streamlit)

```bash
streamlit run streamlit_app.py
```

Luego abre la URL local que muestra Streamlit en la terminal (normalmente http://localhost:8501).

## Deploy web (sin instalar nada local)

Puedes desplegar en Streamlit Community Cloud:

1. Sube este repositorio a GitHub.
2. En https://share.streamlit.io crea una nueva app.
3. Selecciona como archivo principal `streamlit_app.py`.
4. En **App Settings > Secrets** agrega:

```toml
GEMINI_API_KEY = "tu_api_key_gemini"
SERPAPI_API_KEY = "tu_api_key_serpapi"
# PDF_DIR = "Agente de IA Carrarurquia"
```

Con esto, el usuario final solo abre el enlace de la app y usa el chat.

### Reconstruir índice FAISS

```bash
python app.py --pregunta "test" --rebuild-index
```

## Notas

- Por defecto, el proyecto toma los PDFs desde `Agente de IA Carrarurquia/`.
- Si deseas cambiar carpeta de documentos, usa en `.env`:

```env
PDF_DIR=otra_carpeta_con_pdfs
```
