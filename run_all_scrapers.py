import subprocess
import os

def run_scrapers():
    scrapers = [
        "scraper_reinasex.py",
        "scraper_aru18.py",
        "scraper_ranking_net.py",
        "scraper_lifecolle.py",
        "scraper_yuuzuki.py"
    ]
    
    for scraper in scrapers:
        if os.path.exists(scraper):
            print(f"Running {scraper}...")
            try:
                subprocess.run(["python", scraper], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running {scraper}: {e}")
        else:
            print(f"Scraper {scraper} not found.")

if __name__ == "__main__":
    run_scrapers()
