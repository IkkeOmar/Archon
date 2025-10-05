# Archon Lite – Agentic Development Tool

Archon Lite is a simplified local control panel for developers who collaborate with AI coding assistants. It provides a FastAPI backend and lightweight front-end to connect to your favourite language models while staying in control of your prompts, project knowledge, and execution flow.

## ✨ Features

- **Runs locally** on Windows or Linux with a single `uvicorn` command
- **Multiple provider support** out of the box: OpenAI, Anthropic, Google Gemini, and local Llama (Ollama or any OpenAI-compatible endpoint)
- **Simple conversation interface** with conversation history and system prompt controls
- **Environment-based configuration** – keep your API keys in a `.env` file outside of source control
- **Pure Python stack** with no build tooling requirements

## 🚀 Quick Start

1. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r simple_agent_tool/requirements.txt
   ```

3. **Configure provider credentials**

   ```bash
   cp simple_agent_tool/.env.example .env
   ```

   Update `.env` with the API keys for the providers you plan to use. Only the providers with keys will be enabled in the UI.

4. **Run the local server**

   ```bash
   uvicorn simple_agent_tool.simple_agent_tool.main:app --reload
   ```

5. **Open the UI**

   Visit [http://localhost:8000](http://localhost:8000) to start a session.

## 🔧 Provider Notes

- **OpenAI**: Supports any OpenAI-compatible endpoint. Set `OPENAI_BASE_URL` if you use Azure OpenAI or a proxy.
- **Anthropic**: Requires an Anthropic Claude API key.
- **Google Gemini**: Uses `google-generativeai`. Provide a Gemini API key.
- **Llama**: Works with [Ollama](https://ollama.com) or any compatible API exposing `/api/chat`.

## 🧰 Development

- The FastAPI app lives in `simple_agent_tool/simple_agent_tool`.
- Static assets are plain CSS/JavaScript for easy modification.
- Extend `providers/` with additional model backends following the base class pattern.

## 🛡️ Security

API keys are loaded from environment variables only; they are never sent to the browser or logged. Protect your `.env` file accordingly.

## 📄 License

This simplified tooling inherits Archon's [MIT License](../LICENSE).
