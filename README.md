
# StudyPilot 🎯
### Your flexible study co-pilot

StudyPilot is a Python and Streamlit-based study planner that helps students decide what to study first and adjust their plan based on available study time.

## 💡 The Problem

Students often struggle to prioritize subjects, balance difficult topics, and maintain a realistic study schedule when their available time changes.

## 🚀 The Solution

StudyPilot creates a prioritized study plan based on task duration, difficulty, weak topics, and the time available for studying.

## ✨ Features

- **Smart prioritization:** Prioritizes difficult tasks and topics marked as weak.
- **Flexible scheduling:** Generates a plan based on the available time budget.
- **Progress tracking:** Tracks completed and pending study tasks.
- **Adaptive replanning:** Regenerates recommendations when tasks or available time change.
- **Local persistence:** Saves study tasks in a local JSON file.
- **Interactive dashboard:** Displays tasks, progress, and the recommended plan.

## 🛠️ Technology Stack

- Python
- Streamlit
- JSON
- HTML and CSS

## ⚙️ How It Works

1. Add study tasks and specify their duration.
2. Select each task's difficulty and mark weak topics.
3. Set your available study time.
4. Review the recommended study plan.
5. Mark tasks complete and update your plan as needed.

StudyPilot currently uses a transparent, rule-based prioritization algorithm. It does not require an external AI service or API key.

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/mohdabdulwaheed789-alt/StudyPilot.git
cd StudyPilot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install streamlit
```

### 4. Start the application

```bash
python -m streamlit run app.py
```

Open the local URL shown in your terminal, usually http://localhost:8501.

## 🔒 Data and Privacy

Study tasks are stored locally in `tasks.json`. They are not intended to be uploaded to the public repository.

## 🔮 Future Improvements

- Configurable prioritization rules
- Study streaks and goal tracking
- Weekly progress summaries
- Exportable study schedules
- More personalized scheduling options

## 👨‍💻 Built For

Amazon Build, Ship, Shape 2026 hackathon project.

---

**StudyPilot — Plan smarter. Study better.**
