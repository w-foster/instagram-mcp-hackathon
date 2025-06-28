# instagram-mcp-hackathon

**QuizWizard** - **Gala** **Labs** **Instagram** **Buildathon**

A product which gamifies and automates Instagram outreach, by ingesting product info and sending this into an Agentic system with access to Instagram MCP.

You can find the post on X [here](https://x.com/lucas_chan82333/status/1938782631568585177).

## Overview

Powered by a multi-agent system built using LangGraph, utilising Instagram MCP for tools.
1) Collect product info from the frontend, scrape the product page, and use LLM to generate a product overview;
2) User-finder pipeline: an agent with two tools (LLM-based hashtag generation, and Instaloader-based tool for finding users who posted with specified hashtags);
3) DM-creation pipeline: multi-agent system w/ supervisor pattern (subagents-as-tools) - Profile Analyzer uses MCP to get recent posts and build up context of the user; Message Writer crafts tailored DMs with riddles, according to product + user context; Verifier assesses generated DMs and gives qualitative feedback; Supervisor orchestrates these agents and exerts judgement over control flow, and uses MCP to send the final message;
4) Replies: periodically check if anyone is waiting for us to reply, via MCP, and create a response -- solved the riddle = get the promo prize.


![image](https://github.com/user-attachments/assets/1d4a3203-0a5b-4c4e-a7fc-b2302cb53d05)



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

Configure environment variables separately for both backend and frontend as described in their README.md files.

---

## Contributors

- Will Foster
- Andy Peng
- Lucas Chan
- Yile Huang

