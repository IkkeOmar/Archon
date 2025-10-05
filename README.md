<p align="center">
  <img src="./archon-ui-main/public/archon-main-graphic.png" alt="Archon Main Graphic" width="853" height="422">
</p>

<p align="center">
  <em>Power up your AI coding assistants with a local-first knowledge base and project hub</em>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#whats-included">What's Included</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## 🎯 What is Archon?

> Archon is currently in beta! Expect things to not work 100%, and please feel free to share any feedback and contribute with fixes/new features! Thank you to everyone for all the excitement we have for Archon already, as well as the bug reports, PRs, and discussions. It's a lot for our small team to get through but we're committed to addressing everything and making Archon into the best tool it possibly can be!

Archon is the **command center** for AI coding assistants. For you, it's a sleek interface to manage knowledge, context, and tasks for your projects. Connect Claude Code, Kiro, Cursor, Windsurf, etc. to give your AI agents access to:

- **Your documentation** (crawled websites, uploaded PDFs/docs)
- **Smart search capabilities** with advanced RAG strategies
- **Task management** integrated with your knowledge base
- **Real-time updates** as you add new content and collaborate with your coding assistant on tasks
- **Much more** coming soon to build Archon into an integrated environment for all context engineering

This new vision for Archon replaces the old one (the agenteer). Archon used to be the AI agent that builds other agents, and now you can use Archon to do that and more.

> It doesn't matter what you're building or if it's a new/existing codebase - Archon's knowledge and task management capabilities will improve the output of **any** AI driven coding.

## 🔗 Important Links

- **[GitHub Discussions](https://github.com/coleam00/Archon/discussions)** - Join the conversation and share ideas about Archon
- **[Contributing Guide](CONTRIBUTING.md)** - How to get involved and contribute to Archon
- **[Introduction Video](https://youtu.be/8pRc_s2VQIo)** - Getting Started Guide and Vision for Archon
- **[Dynamous AI Mastery](https://dynamous.ai)** - The birthplace of Archon - come join a vibrant community of other early AI adopters all helping each other transform their careers and businesses!

## Quick Start

Archon now runs as a lightweight local web app—no Docker Compose or MCP services required. The commands below work on macOS/Linux (bash) and Windows (PowerShell). Substitute `./` with `.` on Windows where needed.

### Prerequisites

- **Python 3.12** (we recommend [uv](https://docs.astral.sh/uv/) for dependency management)
- **Node.js 18+**
- **Git**
- **Supabase storage choice**
  - *Cloud*: a free [Supabase](https://supabase.com/) project
  - *Local*: the [Supabase CLI](https://supabase.com/docs/guides/local-development) (`supabase start`) if you prefer to keep data on your machine
- An API key for **one** of the supported LLM providers (OpenAI, Google Gemini, or Anthropic Claude)

### 1. Clone the repository

```bash
git clone https://github.com/coleam00/archon.git
cd archon
```

### 2. Configure environment variables

Copy the example file and update the Supabase credentials for the storage option you selected. The server key must be the `service_role` key.

```bash
cp .env.example .env
# then edit .env with your values
```

For local storage run `supabase init` once, then `supabase start` to launch a Postgres + Studio stack on localhost. Use the generated URL and service role key in your `.env` file.

### 3. Prepare the database

Run the SQL in `migration/complete_setup.sql` inside your Supabase project (cloud dashboard or local Studio) to create all required tables and functions.

### 4. Install backend dependencies

```bash
cd python
uv sync
cd ..
```

`uv` creates an isolated virtual environment inside `.venv` and resolves all Python dependencies.

### 5. Start the FastAPI backend

```bash
cd python
uv run python -m src.server.main
```

The API listens on `http://127.0.0.1:8181` by default. You can change the port through `ARCHON_SERVER_PORT` in `.env`.

### 6. Install and start the React UI

```bash
cd archon-ui-main
npm install
npm run dev -- --host 0.0.0.0 --port 3737
```

Visit [http://localhost:3737](http://localhost:3737) to open the interface. On first launch you’ll be asked to paste the API key for your chosen provider (OpenAI, Gemini, or Claude). You can always update credentials later via **Settings → API Keys**.

### 7. Verify the setup

1. Upload a document or crawl a URL in **Knowledge Base** to populate your knowledge graph.
2. Check **Settings → RAG Settings** to confirm that the provider and embedding models look correct.
3. Optionally keep the backend running with a process manager (`uv run -- --reload`) and start the UI with `npm run dev` whenever you need the dashboard.

## 🔄 Database Reset (Start Fresh if Needed)

If you need to completely reset your database and start fresh:

<details>
<summary>⚠️ <strong>Reset Database - This will delete ALL data for Archon!</strong></summary>

1. **Run Reset Script**: In your Supabase SQL Editor, run the contents of `migration/RESET_DB.sql`

   ⚠️ WARNING: This will delete all Archon specific tables and data! Nothing else will be touched in your DB though.

2. **Rebuild Database**: After reset, run `migration/complete_setup.sql` to create all the tables again.

3. **Restart Services**:

   Restart your local processes:

   ```bash
   # Terminal 1
   cd python
   uv run python -m src.server.main

   # Terminal 2
   cd archon-ui-main
   npm run dev
   ```

4. **Reconfigure**:
   - Select your LLM/embedding provider and set the API key again
   - Re-upload any documents or re-crawl websites

The reset script safely removes all tables, functions, triggers, and policies with proper dependency handling.

</details>

## ⚡ Quick Test

Once everything is running:

1. **Test Web Crawling**: Go to http://localhost:3737 → Knowledge Base → "Crawl Website" → Enter a doc URL (such as https://ai.pydantic.dev/llms-full.txt)
2. **Test Document Upload**: Knowledge Base → Upload a PDF
3. **Test Projects**: Projects → Create a new project and add tasks
4. **Invite your AI coding assistant**: Copy the FastAPI base URL (`http://127.0.0.1:8181`) into your assistant’s custom tool configuration so it can call Archon’s REST endpoints.

## 📚 Documentation

### Core Services

| Service         | How to start                                 | Default URL           | Purpose                           |
| --------------- | -------------------------------------------- | --------------------- | --------------------------------- |
| **Web Interface** | `npm run dev` (inside `archon-ui-main`)       | http://localhost:3737 | Main dashboard and controls       |
| **API Service**   | `uv run python -m src.server.main` (in `python/`) | http://127.0.0.1:8181 | Web crawling, document processing |

## What's Included

### 🧠 Knowledge Management

- **Smart Web Crawling**: Automatically detects and crawls entire documentation sites, sitemaps, and individual pages
- **Document Processing**: Upload and process PDFs, Word docs, markdown files, and text documents with intelligent chunking
- **Code Example Extraction**: Automatically identifies and indexes code examples from documentation for enhanced search
- **Vector Search**: Advanced semantic search with contextual embeddings for precise knowledge retrieval
- **Source Management**: Organize knowledge by source, type, and tags for easy filtering

### 🤖 AI Integration

- **Multi-LLM Support**: Works with OpenAI, Google Gemini, and Anthropic Claude models
- **RAG Strategies**: Hybrid search, contextual embeddings, and result reranking for optimal AI responses
- **Real-time Streaming**: Live responses from AI agents with progress tracking

### 📋 Project & Task Management

- **Hierarchical Projects**: Organize work with projects, features, and tasks in a structured workflow
- **AI-Assisted Creation**: Generate project requirements and tasks using integrated AI agents
- **Document Management**: Version-controlled documents with collaborative editing capabilities
- **Progress Tracking**: Real-time updates and status management across all project activities

### 🔄 Real-time Collaboration

- **WebSocket Updates**: Live progress tracking for crawling, processing, and AI operations
- **Multi-user Support**: Collaborative knowledge building and project management
- **Background Processing**: Asynchronous operations that don't block the user interface
- **Health Monitoring**: Built-in service health checks and automatic reconnection

## Architecture

### Microservices Structure

The streamlined developer build focuses on two local services:

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Server (API)   │
│                 │    │                 │
│  React + Vite   │◄──►│ FastAPI + RAG   │
│  Port 3737      │    │  Port 8181      │
└─────────────────┘    └─────────────────┘
         │                    │
         └──────────────┬─────┘
                        │
               ┌─────────────────┐
               │    Database     │
               │                 │
               │ Supabase (cloud │
               │  or local CLI)  │
               └─────────────────┘
```

Legacy MCP and agent services remain in the repository for teams that rely on them, but they are no longer part of the default setup.

### Service Responsibilities

| Service      | Location             | Purpose                      | Key Features |
| ------------ | -------------------- | ---------------------------- | ------------ |
| **Frontend** | `archon-ui-main/`    | Web interface and dashboard  | React, TypeScript, TailwindCSS, Socket.IO client |
| **Server**   | `python/src/server/` | Core business logic and APIs | FastAPI, knowledge ingest, RAG orchestration |

### Communication Patterns

- **HTTP-based**: All inter-service communication uses HTTP APIs
- **Socket.IO**: Real-time updates from Server to Frontend
- **No Direct Imports**: Services are truly independent with no shared code dependencies

### Key Architectural Benefits

- **Local-first**: Everything runs directly on your machine with no container overhead
- **Simple Networking**: Two HTTP services talk over localhost—easy to debug and secure
- **Modular Services**: Frontend and backend can be developed and updated independently
- **Supabase Flexibility**: Use a managed project or run the Supabase CLI locally without changing Archon

## 🔧 Configuring Custom Ports & Hostname

By default, Archon services run on the following ports:

- **Archon UI**: 3737
- **Archon Server**: 8181

### Changing Ports

To use custom ports, add these variables to your `.env` file:

```bash
# Service Ports Configuration
ARCHON_UI_PORT=3737
ARCHON_SERVER_PORT=8181
```

Example: Running on different ports:

```bash
ARCHON_SERVER_PORT=8282
```

### Configuring Hostname

By default, Archon uses `localhost` as the hostname. You can configure a custom hostname or IP address by setting the `HOST` variable in your `.env` file:

```bash
# Hostname Configuration
HOST=localhost  # Default

# Examples of custom hostnames:
HOST=192.168.1.100     # Use specific IP address
HOST=archon.local      # Use custom domain
HOST=myserver.com      # Use public domain
```

This is useful when:

- Running Archon on a different machine and accessing it remotely
- Using a custom domain name for your installation
- Deploying in a network environment where `localhost` isn't accessible

After changing hostname or ports restart the FastAPI server and UI dev server so they pick up the new environment variables.

## 🔧 Development

For development with hot reload:

```bash
# Backend (with auto-reload)
cd python
uv run uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8181

# Frontend (with hot reload)
cd archon-ui-main
npm run dev

# Documentation (with hot reload)
cd docs
npm start
```

**Note**: uvicorn's `--reload` flag automatically restarts the API when backend code changes. Vite provides instant reloads for the UI.

## 📄 License

Archon Community License (ACL) v1.2 - see [LICENSE](LICENSE) file for details.

**TL;DR**: Archon is free, open, and hackable. Run it, fork it, share it - just don't sell it as-a-service without permission.
