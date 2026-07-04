import pandas as pd
import spacy
import re
import os
from collections import Counter

# ── Load spaCy model ──────────────────────────────────────────────────────────
nlp = spacy.load("en_core_web_sm")

# ── Master skills list ────────────────────────────────────────────────────────
# These are the skills we'll look for in job descriptions
SKILLS = [
    # Programming languages
    "python", "r", "java", "scala", "julia", "c++", "javascript", "typescript",
    # Data & databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "bigquery", "snowflake", "redshift", "databricks",
    # Data science & ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
    "huggingface", "transformers", "llm", "generative ai",
    # Data tools
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "jupyter", "dbt", "airflow", "spark", "hadoop", "kafka",
    # BI & visualization
    "tableau", "power bi", "looker", "metabase", "grafana", "superset",
    # Cloud
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
    # Other
    "git", "github", "linux", "api", "rest api", "fastapi", "flask", "django",
    "excel", "statistics", "a/b testing", "data pipeline", "etl",
    "communication", "teamwork", "leadership", "agile", "scrum"
]

def clean_text(text):
    """Remove HTML tags and extra whitespace from job descriptions"""
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove special characters but keep spaces
    text = re.sub(r"[^\w\s\+\#\.]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def extract_skills_from_text(text):
    """
    Extract skills from a single job description.
    Uses simple phrase matching against our SKILLS list.
    Returns a list of matched skills.
    """
    cleaned = clean_text(text)
    found = []

    for skill in SKILLS:
        # Use word boundary matching so 'r' doesn't match inside 'other'
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, cleaned):
            found.append(skill)

    return found


def process_all_jobs(input_path="data/jobs_raw.csv",
                     output_path="data/jobs_processed.csv"):
    """
    Load raw jobs CSV, extract skills from each description,
    and save enriched CSV.
    """
    print("📂 Loading raw jobs data...")
    df = pd.read_csv(input_path)
    print(f"   Loaded {len(df)} jobs\n")

    print("🔍 Extracting skills from job descriptions...")

    # Combine description + tags for better coverage
    df["full_text"] = df["description"].fillna("") + " " + df["tags"].fillna("")

    # Extract skills for each job
    df["skills_found"] = df["full_text"].apply(extract_skills_from_text)
    df["skills_str"]   = df["skills_found"].apply(lambda x: ", ".join(x))
    df["skill_count"]  = df["skills_found"].apply(len)

    # Save processed file
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved processed data to {output_path}\n")

    # ── Print a summary ───────────────────────────────────────────────────────
    print("📊 TOP 20 MOST IN-DEMAND SKILLS:")
    print("─" * 35)

    all_skills = []
    for skills_list in df["skills_found"]:
        all_skills.extend(skills_list)

    skill_counts = Counter(all_skills)
    for skill, count in skill_counts.most_common(20):
        bar = "█" * (count // 2)
        print(f"  {skill:<20} {count:>3}  {bar}")

    print(f"\n📈 Average skills per job posting: "
          f"{df['skill_count'].mean():.1f}")
    print(f"📋 Jobs with at least 1 skill found: "
          f"{(df['skill_count'] > 0).sum()} / {len(df)}")

    return df


if __name__ == "__main__":
    process_all_jobs()