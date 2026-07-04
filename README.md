# 📊 Job Market Intelligence Dashboard

A data pipeline + interactive dashboard that scrapes live job postings,
extracts in-demand skills using NLP, and visualises trends by role and location.

## 🚀 Live Demo
[View on Streamlit Cloud](https://job-market-dashboard-umdafho5mmqc3zf4ypndax.streamlit.app/) 

## 🛠️ Tech Stack
- **Scraping** — Python, Requests, RemoteOK API
- **NLP** — spaCy, Regex-based skill extraction
- **Data** — Pandas
- **Dashboard** — Streamlit, Plotly
- **Deployment** — Streamlit Cloud

## 📋 Features
- Top 20 in-demand skills across 300+ live job postings
- Skill Explorer — see which roles demand any skill
- Role Comparison — compare skill overlap between two roles
- Skill Gap Analyser — paste your skills, see what you're missing

## ⚙️ Run Locally

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Scrape fresh data
python scraper/scrape_jobs.py

# Extract skills
python nlp/extract_skills.py

# Launch dashboard
streamlit run dashboard/app.py
```

## 📁 Project Structure
job-market-dashboard/
├── scraper/         # Job scraping from RemoteOK API
├── nlp/             # Skill extraction using spaCy + regex
├── data/            # Processed job data (CSV)
├── dashboard/       # Streamlit app + CSS
└── requirements.txt

Built by Tanvi Jain

