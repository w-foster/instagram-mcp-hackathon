# instagram-mcp-hackathon

A full-stack project featuring a FastAPI backend and a modern react.js frontend application, built for the Instagram MCP Hackathon.

---

## Repository Structure

```
.
├── backend/      # FastAPI backend API
├── frontend/     # Frontend react.js application
├── README.md     # This file
└── .gitignore
└── .github/workflows
```

---

## Getting Started

This repository contains two main parts:

- **Backend:** A Flask API server located in the `backend/` directory.
- **Frontend:** A JavaScript frontend application located in the `frontend/` directory.

Each part has its own installation and running instructions.

---

## Setup Instructions

### Installation

1. Clone and navigate to the project:

   ```bash
   git clone https://github.com/w-foster/instagram-mcp-hackathon.git
   cd instagram-mcp-hackathon
   ```

2. Follow the backend installation and run instructions detailed in [backend/README.md](./backend/README.md).

3. Follow the frontend installation and run instructions detailed in [frontend/README.md](./frontend/README.md).

---

## Running the Entire Project Locally

Since this was created for the hackathon, you will first need to navigate to [this](https://github.com/trypeggy/instagram_dm_mcp) repo and follow its instructions to set up the MCP.

Once setup and linked, you can follow the instructions below to locally run the project:

1. Start the backend server first (default port configured in backend).
2. Start the frontend development server (default port configured in frontend).
3. Open your browser and go to `http://localhost:8080`.
4. The frontend will communicate with the backend API.

---

## Environment Variables

Configure environment variables separately for both backend and frontend as described in their README files.

