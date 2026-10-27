# SkillPath AI

**Smart India Hackathon (SIH 2026) — AI-Enabled Adaptive Learning Platform for Competency-Gap Identification, Personalized Training, Grounded RAG Tutoring, and Automated Assessment Generation.**

SkillPath AI transforms modern higher education from static one-size-fits-all content delivery into continuous, data-driven competency mastery.

---

## 🌟 Core Closed-Loop Adaptive Architecture

```
Diagnostic Quiz (Stage 1)
       ↓
Multi-Topic Competency Gap Identification (Radar Chart, Weak/Average/Strong)
       ↓
Cognitive Load & Wellness Calibration (Mental Feedback)
       ↓
Personalized Adaptive Learning Path (Daily & 7-Day Roadmap)
       ↓
Zero-Hallucination Grounded RAG AI Tutor (Curriculum Embeddings)
       ↓
Targeted Weak-Topic Practice Drill (Stage 2)
       ↓
Single-Topic Mastery Gate Assessment (Stage 3 — ≥80% Threshold)
       ↓
Gamification & Next Module Progression (XP, Badges, Streaks)
```

---

## 🚀 Key Modules & What's Implemented

### 1. Grounded RAG AI Tutor (`backend/app/services/rag_pipeline.py` & `frontend/src/pages/student/AITutor.jsx`)
- **Semantic Vector Retrieval**: Indexes course materials (notes, syntax cheatsheets, visual guides, interview problem sets).
- **Anti-Hallucination Guardrails**: Checks cosine similarity relevance threshold before answering; strictly disclaims non-curriculum queries.
- **Multilingual Support**: Supports English, Hindi (हिन्दी), and Hinglish explanations.
- **Pedagogical Citations**: Automatically appends exact course source references with confidence scores.
- **Interactive UI**: Preset prompt chips, conversation history, and quick questions.

### 2. Personalized Learning Path Engine (`backend/app/services/learning_path.py` & `frontend/src/pages/student/LearningPath.jsx`)
- **Gap-Prioritized Scheduling**: Automatically positions identified weak topics in morning focus slots with remedial videos and cheatsheets.
- **Cognitive Load Dynamic Scaling**: Automatically lightens task volume if stress or workload >= 7/10.
- **Interactive Completion**: Check off daily tasks to earn immediate +50 XP rewards.
- **7-Day Master Roadmap**: Monday through Sunday progression tailored to learner pace.

### 3. Adaptive Practice & Mastery Gates (`backend/app/services/quiz_generator.py` & `frontend/src/pages/student/AdaptivePractice.jsx`)
- **Stage 2 Weak-Topic Remediation Drills**: Pulls MCQs strictly from topics classified as weak or average.
- **Stage 3 Mastery Gate Challenge**: Rigorous verification quiz requiring >= 80% accuracy to unlock subsequent curriculum topics.
- **Bloom's Taxonomy Integration**: Questions tagged with cognitive tiers (Remember, Understand, Apply, Analyze).
- **Detailed Question Review**: Explains exact invariant analysis, student answers vs correct answers, and learning objectives.

### 4. Curriculum & Study Materials Hub (`frontend/src/pages/student/StudyHub.jsx`)
- Filter notes, cheatsheets, and interview problem sets by topic.
- Full glassmorphic reader drawer.
- Interactive 5-star rating and feedback widget that awards +15 XP.
- 1-click link to ask AI Tutor about any specific concept.

### 5. Gamification & Streaks (`frontend/src/pages/student/Achievements.jsx`)
- **XP Progression & Tiers**: Bronze Scholar, Silver Practitioner, Gold Strategist, Platinum Specialist, Diamond Architect.
- **Streak Tracker**: Tracks current and longest continuous study streak with animated multipliers.
- **Skill Badges**: Diagnostic Pioneer, Streak Master, Array Ace, Tree Titan, Graph Gladiator, Mastery Gatekeeper, Adaptive Explorer.
- **Cohort Leaderboard**: Live department peer standings.

### 6. Institutional & Educator Oversight
- **Teacher Dashboard (`TeacherDashboard.jsx`)**: Real-time cohort topic mastery heatmap (Weak/Average/Strong breakdown) and class intervention alerts.
- **Admin Dashboard (`AdminDashboard.jsx`)**: Institutional pass rate telemetry, active departments, policy control (80% gate threshold).

---

## 💻 Running Locally

### 1. Backend (FastAPI + SQLite)
```bash
cd backend
# Activate virtual environment
venv\Scripts\activate          # On Windows
# source venv/bin/activate     # On Linux / macOS

# Install dependencies
pip install -r requirements.txt
pip install scikit-learn numpy

# Seed database with courses, question bank, study materials, and demo accounts
python seed_data.py

# Launch server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend (React + Vite + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```
Visit `http://127.0.0.1:5173`. The Vite server proxies API requests to `http://127.0.0.1:8000`.

---

## 🔑 Demo Accounts (1-Click Login available on Login screen)

| Role | Email | Password | Pre-seeded Features |
| :--- | :--- | :--- | :--- |
| **Student** | `student@skillpath.ai` | `password123` | 5d streak, 1,250 XP, 6 badges, baseline radar scores, active learning path |
| **Teacher** | `teacher@skillpath.ai` | `password123` | Data Structures cohort heatmap, class size: 42, gap alerts |
| **Admin** | `admin@skillpath.ai` | `password123` | 4 departments, institutional pass rates, system health telemetry |

---

## 🧪 Quick Test Flow
1. Open `http://127.0.0.1:5173/login` and click **"Student"** 1-Click Demo Login.
2. View your **Student Dashboard** with live telemetry, active daily tasks, and quick actions.
3. Open **"Learning Path"** from the navbar, click **"Mark Done"** on a task to earn +50 XP.
4. Open **"Practice & Mastery"**, select **"Weak-Topic Targeted Drill"**, answer questions and view detailed explanations.
5. Open **"AI Tutor"**, click a prompt chip like *"Explain array memory layout and index access time"*, and observe the grounded course citations.
6. Open **"Study Hub"**, read Array notes, rate the resource to earn +15 XP.
7. Open **"Achievements"** to see your updated XP rank, unlocked badges, and cohort leaderboard.
8. Switch accounts to **Teacher** or **Admin** to inspect cohort heatmaps and institutional analytics.
