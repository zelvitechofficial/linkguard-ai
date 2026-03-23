# LinkGuard AI: Intelligent Phishing & Malicious URL Detection

Welcome to **LinkGuard AI**! This project is a comprehensive, AI-powered cybersecurity solution designed to protect users from malicious links, phishing attempts, and typosquatting attacks in real-time.

This document serves as a detailed, step-by-step project overview intended for college project demonstrations, explaining the architecture, technology choices, and underlying algorithms in an easily understandable format.

---

## 🚀 1. Project Overview

LinkGuard AI analyzes URLs submitted by users and determines whether they are safe or malicious. Unlike traditional signature-based blockers (which only block known bad links), our system uses **Machine Learning (Lexical Analysis)** and **Heuristic Pattern Matching** to identify entirely new, zero-day threats. It also features a built-in AI Chatbot powered by Google GenAI to assist users with cybersecurity queries.

### Key Features:
- **Real-Time URL Scanning**: Analyze any link instantly.
- **AI Cybersecurity Assistant**: Chatbot for proactive security advice.
- **Admin Dashboard**: A centralized hub to monitor global scan traffic, user metrics, and ML accuracy.
- **User Management**: Secure authentication and usage tracking to prevent API abuse.

---

## 🏗️ 2. System Architecture

The project is divided into three interconnected layers: the Frontend (User Interface), the Admin Dashboard (Management Interface), and the Backend (Core Processing & AI).

### A. Frontend Architecture (User-Facing)
The Frontend is the portal where end-users interact with the application.
- **Workflow**: Users log in securely via Clerk, input a URL, and submit it. The frontend sends this to the backend API, waits for the AI analysis, and displays the risk score and final verdict (Safe / Malicious).
- **State Management**: Tracks user daily scan limits and chatbot usage in real-time, syncing with the backend database.

### B. Admin Dashboard Architecture
The Admin Interface is a separate, secure portal restricted to administrators.
- **Workflow**: Admins log in to view system health and oversight operations. The dashboard fetches aggregated metrics (total scans, malicious vs. safe ratio, ML model metrics) and the full URL scan database.
- **Live Data**: React components independently fetch real-time analytics from asynchronous backend endpoints, providing live updates on system performance.

### C. Backend Architecture (The Brains)
The Backend handles all the heavy computation, acting as the bridge between the database, the ML models, and the frontends.
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
| **Frontend & Admin** | **React.js + Vite** | React allows us to build isolated, reusable UI components. Vite is significantly faster than traditional bundlers (like Webpack), leading to instant server starts and rapid hot-module replacement. |
| **Styling** | **Tailwind CSS** | A utility-first CSS framework. It eliminates massive custom CSS files, making styling scalable and completely preventing CSS conflicts. |
| **Backend Framework** | **FastAPI (Python)** | FastAPI is lightning fast, supports asynchronous programming (`async/await`) out of the box, and automatically generates API documentation (Swagger UI). Python is also the undisputed standard for Machine Learning. |
| **Database & ORM** | **SQLAlchemy Async** | SQLAlchemy provides a secure, async Object Relational Mapper (ORM), protecting against SQL injection while making database interactions Pythonic and efficient. |
| **Authentication** | **Clerk** | A modern, highly secure drop-in authentication provider. Building custom auth from scratch is prone to severe security flaws; Clerk handles sessions, OAuth, and security natively. |
| **AI LLM** | **Google GenAI** | Used for the cybersecurity chatbot. It provides state-of-the-art natural language understanding, maintaining an expert cybersecurity persona with a solid fallback mechanism. |

---

## 🧠 4. Machine Learning Algorithms Explained

To predict if a URL is malicious, we don't look at the website content; we look at the **Lexical Structure** of the URL itself (how the URL is built). We extract 18 distinct numerical features from the text (like `url_length`, `count_hyphen`, `use_https`, `subdomain_depth`).

### The Training Dataset
To ensure the system is highly accurate, we trained our ML models on a massive, real-world dataset (`malicious_phish.csv`).
- **Total Records:** 651,200 unique URLs.
- **Categorization:** The dataset maps URLs into four distinct classes:
  1. `benign` (Safe URLs)
  2. `phishing` (Sites attempting to steal credentials)
  3. `defacement` (Sites hacked to display unauthorized content)
  4. `malware` (Sites distributing malicious software)

We utilize two primary algorithms for prediction:

### 1. Random Forest (Primary Model) - Accuracy: 89.00%
**What it is:** Random Forest is an "ensemble" algorithm. Instead of creating one decision-maker, it creates a "forest" of many individual Decision Trees (e.g., 100 trees). 
**Why we used it:** It is highly resistant to "overfitting" (memorizing the training data) and handles complex, non-linear relationships in data much better than simpler models. It is highly robust against noisy data.
**Simple Calculation/Explanation:** 
Imagine asking 100 different cybersecurity experts if a link is dangerous. 
- Expert 1 looks at the URL length and says "Malicious".
- Expert 2 notices the lack of HTTPS and says "Malicious".
- Expert 3 sees it has no subdomains and says "Safe".
The Random Forest aggregates all 100 votes. If 85 experts say "Malicious", the model outputs a Malicious verdict with an 85% confidence score.

### 2. Decision Tree (Baseline Model) - Accuracy: 86.49%
**What it is:** A flowchart-like algorithm that splits data based on feature conditions.
**Why we used it:** It serves as our baseline model. While slightly less accurate than Random Forest, it is 100% interpretable. We can visually see exactly *why* it flagged a URL.
**Simple Calculation/Explanation:**
The algorithm starts at the top and answers Yes/No questions to reach a conclusion:
```text
IF use_https == 0 (No)
 └── IF url_length > 75 
      └── PREDICT: Malicious
IF use_https == 1 (Yes)
 └── IF abnormal_url == 1
      └── PREDICT: Malicious
```

---

## 🔬 5. Deep Research Insights: The Typosquatting Threat

*(Special Research Section)*

While Machine Learning is excellent at detecting structurally anomalous URLs, attackers are continually evolving. One of the most dangerous, highly successful methods used today is **Typosquatting** (or URL hijacking).

**The Threat:**
Attackers register domains that look visually identical to trusted brands but contain slight typographical errors. For instance, replacing a lowercase `l` (el) with an uppercase `I` (eye), or spelling `microsoft.com` as `rnicrosoft.com` (using 'r' and 'n'). 
Standard ML models often classify these as "Safe" because their lexical structure is perfectly normal (standard length, uses HTTPS, no weird symbols).

**Our Innovative Solution:**
We implemented a hybrid approach to combat this. Before the ML model finalizes its verdict, the backend executes a specialized Heuristic Lexical Scanner.
1. It extracts the core domain of the requested URL.
2. It runs a `SequenceMatcher` algorithm (calculating the Levenshtein distance/similarity ratio) against a hardcoded list of high-value targets (e.g., Google, Chase, PayPal).
3. If the similarity ratio is between `80%` and `99%` (meaning it's suspiciously close but not an exact match), the system overrides the ML model.
4. It forcefully flags the URL as a `Typosquatting` attempt with extreme confidence.

This multi-layered approach (ML + Heuristics) drastically reduces false negatives, ensuring our system remains resilient against sophisticated, zero-day phishing campaigns that traditional scanners miss.

---

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

3. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Start the Admin Dashboard**
   ```bash
   cd admin
   npm install
   npm run dev
   ```

*Note: Ensure all `.env` files are properly configured with your database URLs, ML metrics paths, and Clerk API keys before launching.*

---

## 🌐 7. Live Production Links

Access the live application and its components via the following links:

- **Frontend (Main Application)**: [https://linkguardaihome.netlify.app/](https://linkguardaihome.netlify.app/)
- **Admin Dashboard**: [https://linkguardaiadmin.netlify.app/](https://linkguardaiadmin.netlify.app/)
- **Backend API (Production)**: [https://linkguard-backend-q6cu.onrender.com](https://linkguard-backend-q6cu.onrender.com)

---
*Built with ❤️ for a safer internet.*
