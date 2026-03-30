# LinkGuard AI: Intelligent Phishing & Malicious URL Detection

Welcome to **LinkGuard AI**! This project is a comprehensive, AI-powered cybersecurity solution designed to protect users from malicious links, phishing attempts, and typosquatting attacks in real-time.

This document serves as a detailed, step-by-step project overview intended for college project demonstrations, explaining the architecture, technology choices, and underlying algorithms in an easily understandable format.

---

## 🚀 1. Project Overview

LinkGuard AI analyzes URLs submitted by users and determines whether they are safe or malicious. Unlike traditional signature-based blockers (which only block known bad links), our system uses **Machine Learning (Lexical Analysis)** and **Heuristic Pattern Matching** to identify entirely new, zero-day threats. It also features a built-in AI Chatbot powered by Google GenAI to assist users with cybersecurity queries.

### Key Features:
- **Real-Time URL Scanning**: Analyze any link instantly.
- **AI Cybersecurity Assistant**: Chatbot for proactive security advice.
- **Admin Dashboard**: A centralized hub to monitor global scan traffic and user metrics with **30-second real-time auto-synchronization**.
- **User Management**: Secure authentication and usage tracking to prevent API abuse, with real-time Clerk integration.

---

## 🏗️ 2. System Architecture

The project is divided into two main layers: the Frontend (User & Admin Interface) and the Backend (Core Processing & AI).

### A. Frontend Architecture (Integrated User & Admin)
The Frontend is the single portal for all users. Administrative features are seamlessly integrated and accessible via the `/admin` route.
- **User Workflow**: Users log in securely via Clerk, input a URL, and submit it. The frontend sends this to the backend API, waits for the AI analysis, and displays the risk score and final verdict (Safe / Malicious).
- **Admin Workflow**: Any authenticated user can access the `/admin` dashboard to view system health and oversight operations. The dashboard fetches aggregated metrics (total scans, malicious vs. safe ratio, ML model metrics) and the full URL scan database.
- **Real-Time Sync**: Implements a global 30-second background polling mechanism. Deleting a scan record automatically triggers a refresh of the overview statistics to ensure cross-page data consistency.
- **State Management**: Tracks user daily scan limits and chatbot usage in real-time, syncing with the backend database.

### B. Backend Architecture (The Brains)
The Backend handles all the heavy computation, acting as the bridge between the database, the ML models, and the frontend.
- **Workflow**: 
  1. Receives the URL from the frontend.
  2. Extracts 18 lexical features (e.g., URL length, symbol counts, IP presence).
  3. Feeds features to the `MLService` containing pre-trained Scikit-Learn models.
  4. Runs heuristic checks to detect potential typosquatting (e.g., a fake 'google.com').
  5. Saves the scan result and user association to the PostgreSQL/SQLite database and returns the final verdict.

---

## 🛠️ 3. Tech Stack & "Why We Chose It"

Choosing the right technology is critical for performance, scalability, and developer experience.

| Component | Technology | Why We Chose It |
| :--- | :--- | :--- |
| **Unified Frontend** | **React.js + Vite** | React allows us to build isolated, reusable UI components. Vite is significantly faster than traditional bundlers (like Webpack), leading to instant server starts and rapid hot-module replacement. |
| **Styling** | **Tailwind CSS** | A utility-first CSS framework. It eliminates massive custom CSS files, making styling scalable and completely preventing CSS conflicts. |
| **Backend Framework** | **FastAPI (Python)** | FastAPI is lightning fast, supports asynchronous programming (`async/await`) out of the box, and automatically generates API documentation (Swagger UI). Python is also the undisputed standard for Machine Learning. |
| **Database & ORM** | **SQLAlchemy Async** | SQLAlchemy provides a secure, async Object Relational Mapper (ORM), protecting against SQL injection while making database interactions Pythonic and efficient. |
| **Authentication** | **Clerk** | A modern, highly secure drop-in authentication provider. Building custom auth from scratch is prone to severe security flaws; Clerk handles sessions, OAuth, and security natively. |
| **AI LLM** | **Google GenAI** | Used for the cybersecurity chatbot. It provides state-of-the-art natural language understanding, maintaining an expert cybersecurity persona with a solid fallback mechanism. |

---

... (sections 4 and 5 remain unchanged) ...

## 👨‍💻 6. How to Run the Project Locally

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd linkguard-ai
   ```

2. **Start the Backend (FastAPI)**
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # source venv/bin/activate    # Mac/Linux
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Start the Integrated Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Access the main app at http://localhost:5173 and the Admin Dashboard at http://localhost:5173/admin.*

*Note: Ensure all `.env` files are properly configured with your database URLs, ML metrics paths, and Clerk API keys before launching.*

---

## 🌐 7. Live Production Links

Access the live application and its components via the following links:

- **Frontend & Admin (Unified)**: [https://linkguardaihome.netlify.app/](https://linkguardaihome.netlify.app/)
- **Backend API (Production)**: [https://linkguard-backend-q6cu.onrender.com](https://linkguard-backend-q6cu.onrender.com)

---

## 🛠️ 8. Troubleshooting & Production Configuration

For the live project demonstration, ensure the following environment variables are correctly configured in your hosting platform (Render/Netlify).

### Required Backend Environment Variables (Render)
| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string (asyncpg). |
| `CLERK_SECRET_KEY` | Required for Admin panel to fetch Registered Users. |
| `GEMINI_API_KEY` | Required for the AI Cybersecurity Assistant. |
| `CLERK_API_KEY` | Public key for user resolution. |

### Required Frontend Environment Variables (Netlify)
| Variable | Description |
| :--- | :--- |
| `VITE_API_URL` | Should point to your production Render backend URL. |

> [!TIP]
> **CAPTCHA Issues?** The system now includes an updated Content Security Policy (CSP) to allow Cloudflare Turnstile. If CAPTCHA fails to load, ensure no browser extensions (like aggressive ad-blockers) are interfering.

---
*Built with ❤️ for a safer internet.*
