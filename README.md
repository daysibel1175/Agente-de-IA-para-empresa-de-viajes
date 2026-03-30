# Agent AI Travel Agency / Agente de IA para Agência de Viagens
Proyecto desarrollado en la imersion de Agentes de IA de Alura Latam 2026

Selecciona tu idioma / Escolha seu idioma:
- [Español (ES)](#español-es)
- [Português (PT)](#português-pt)

---

## Español (ES)

### Agente de IA para Agencia de Viajes (Carrarurquía) 🤖✈️

Este proyecto implementa un agente de inteligencia artificial avanzado diseñado para una agencia de viajes especializada en turismo en Turquía. El sistema utiliza una arquitectura de **Generación Aumentada por Recuperación (RAG)** y un flujo de trabajo orquestado por **LangGraph** para responder preguntas basadas tanto en documentos internos como en búsquedas en tiempo real en la web.

#### 🚀 Características principales
* **Arquitectura RAG:** Extrae información precisa de reportes internos en formato PDF.
* **Orquestación Inteligente:** Utiliza LangGraph para decidir si una consulta se resuelve con documentos locales o mediante búsqueda web (SerpAPI).
* **Base de Datos Vectorial:** Emplea **FAISS** para el almacenamiento y búsqueda eficiente de embeddings.
* **Multimodelo:** Configurado para trabajar con modelos de Google Generative AI (`gemini-2.0-flash` y `text-embedding-004`).
* **Salida Formateada:** Genera respuestas automáticas en Markdown y permite exportación a PDF.

#### 🛠️ Tecnologías utilizadas
* **Lenguaje:** Python
* **Frameworks:** LangChain, LangGraph
* **LLM & Embeddings:** Google Gemini API
* **Vector Store:** FAISS
* **Herramientas de búsqueda:** SerpAPI

#### 📋 Requisitos previos
Necesitarás las siguientes API Keys configuradas en tu entorno:
1. `GEMINI_API_KEY`: Para el acceso a los modelos de lenguaje de Google.
2. `SERPAPI_API_KEY`: Para las búsquedas en la web.

#### 🔧 Instalación
```bash
pip install -q google-genai langchain-community pypdf langchain-text-splitters langchain-google-genai faiss-cpu langgraph google-search-results markdown fpdf2
```
<a name="português-pt"></a>
## Português (PT)

### Agente de IA para Agência de Viagens (Carrarurquía) 🤖✈️

Este projeto implementa um agente de inteligência artificial avançado projetado para uma agência de viagens especializada em turismo na Turquia. O sistema utiliza uma arquitetura de **Geração Aumentada por Recuperação (RAG)** e um fluxo de trabalho orquestrado pelo **LangGraph** para responder perguntas baseadas tanto em documentos internos quanto em buscas em tempo real na web.

#### 🚀 Principais Características
* **Arquitetura RAG:** Extrai informações precisas de relatórios internos em formato PDF.
* **Orquestração Inteligente:** Utiliza LangGraph para decidir se uma consulta deve ser resolvida com documentos locais ou através de busca na web (SerpAPI).
* **Banco de Dados Vetorial:** Utiliza **FAISS** para o armazenamento e busca eficiente de embeddings.
* **Multimodelo:** Configurado para trabalhar com modelos da Google Generative AI (`gemini-2.0-flash` e `text-embedding-004`).
* **Saída Formatada:** Gera respostas automáticas em Markdown e permite exportação para PDF.

#### 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python
* **Frameworks:** LangChain, LangGraph
* **LLM & Embeddings:** Google Gemini API
* **Vector Store:** FAISS
* **Ferramentas de busca:** SerpAPI

#### 📋 Pré-requisitos
Você precisará das seguintes chaves de API configuradas no seu ambiente:
1. `GEMINI_API_KEY`: Para acessar os modelos de linguagem do Google.
2. `SERPAPI_API_KEY`: Para realizar buscas na web.

#### 🔧 Instalação
```bash
pip install -q google-genai langchain-community pypdf langchain-text-splitters langchain-google-genai faiss-cpu langgraph google-search-results markdown fpdf2
```
