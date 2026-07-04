import requests
import pandas as pd
import json
import time
import os
from datetime import datetime

def fetch_jobs(keywords):
    """
    Fetch jobs from RemoteOK public API.
    keywords: list of job titles to search e.g. ["data analyst", "data scientist"]
    """
    all_jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (JobMarketDashboard - Student Project)"
    }

    for keyword in keywords:
        print(f"Fetching jobs for: {keyword}")
        
        # RemoteOK API - free and public
        url = f"https://remoteok.com/api?tag={keyword.replace(' ', '-')}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # First item is always a notice/metadata, skip it
            jobs = data[1:] if len(data) > 1 else []
            
            for job in jobs:
                all_jobs.append({
                    "title":       job.get("position", ""),
                    "company":     job.get("company", ""),
                    "location":    job.get("location", "Remote"),
                    "description": job.get("description", ""),
                    "tags":        ", ".join(job.get("tags", [])),
                    "date_posted": job.get("date", ""),
                    "salary":      job.get("salary", ""),
                    "url":         job.get("url", ""),
                    "search_term": keyword
                })
            
            print(f"  Found {len(jobs)} jobs for '{keyword}'")
            time.sleep(2)  # Be polite, don't hammer the API
            
        except Exception as e:
            print(f"  Error fetching '{keyword}': {e}")
            continue

    return all_jobs


def save_jobs(jobs, filepath="data/jobs_raw.csv"):
    """Save jobs list to CSV"""
    if not jobs:
        print("No jobs to save.")
        return
    
    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    df = pd.DataFrame(jobs)
    
    # Remove duplicates based on title + company
    df.drop_duplicates(subset=["title", "company"], inplace=True)
    
    df.to_csv(filepath, index=False)
    print(f"\n✅ Saved {len(df)} jobs to {filepath}")
    return df


if __name__ == "__main__":
    # Job roles to search — edit these to whatever you want
    search_terms = [
    "machine-learning",
    "python",
    "data-science",
    "analytics",
    "ai"
]
    print("🔍 Starting job scraper...")
    print(f"Searching for: {search_terms}\n")
    
    jobs = fetch_jobs(search_terms)
    df = save_jobs(jobs)
    
    if df is not None:
        print(f"\nSample of collected data:")
        print(df[["title", "company", "location", "tags"]].head())
