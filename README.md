# Multi-Agent Research System

A comprehensive research application powered by a multi-agent AI pipeline. This system leverages specialized AI agents to plan, research, critique, and write in-depth research reports on any given topic.

## Features

- **Multi-Agent Architecture**: Built with LangGraph, it orchestrates a team of agents:
  - **Planner Agent**: Breaks down the main topic into researchable subtopics.
  - **Researcher Agent**: Gathers information from the web for each subtopic.
  - **Critic Agent**: Evaluates the gathered information and decides if more research loops are needed.
  - **Writer Agent**: Synthesizes the findings into a comprehensive, well-structured markdown report.
- **Real-Time Streaming (SSE)**: The frontend displays real-time updates of the agent thought processes, research findings, and live token-by-token streaming of the final report.
- **Mock Fallback Mode**: Fully functional offline/mock mode when API keys are not provided, allowing for local development and testing without incurring LLM API costs.
- **Deep-Dive Capabilities**: Ability to select specific sections of the generated report and instruct the system to "dig deeper" to fetch more granular information.

## Tech Stack

### Backend
- **Python & FastAPI**: For high-performance async API endpoints and SSE streaming.
- **LangGraph**: Orchestrates the multi-agent state machine and logic flow.
- **SQLite / SQLAlchemy**: For persistent storage of research reports.
- **Redis (Optional)**: State management across the LangGraph execution. Includes an in-memory fallback if Redis is unavailable.

### Frontend
- **React & Vite**: Fast, modern frontend framework.
- **Server-Sent Events (SSE)**: For consuming real-time streaming updates from the backend.
- **Tailwind CSS (or similar)**: For styling and UI.

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- (Optional) Redis server

### 2. Backend Setup
Navigate to the root directory of the project and set up the Python backend:

```bash
# Create a virtual environment
python -m venv backend/venv

# Activate the virtual environment (Windows)
.\backend\venv\Scripts\activate
# Activate on macOS/Linux: source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### Environment Variables (Optional)
To use real AI models and live web search, create a `.env` file in the `backend` directory with the following keys. If omitted, the system will seamlessly run in mock mode.
```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

#### Run the Backend Server
Make sure you are in the project root directory (`multi-agent-research`):
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
The backend API will be available at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal window and set up the frontend:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```
The frontend application will be available at `http://localhost:5173`.

## Architecture Flow

1. The user inputs a topic on the frontend.
2. The backend initiates the LangGraph `research_graph` pipeline.
3. State is persisted, and the **Planner Agent** outlines the research strategy.
4. The **Researcher Agent** and **Critic Agent** run in a loop (up to a set limit) to gather and refine information.
5. The **Writer Agent** drafts the final report.
6. The entire process, including intermediate agent thoughts and the final report drafting, is streamed back to the frontend via SSE and displayed to the user in real time.
