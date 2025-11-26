import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def get_job_description(job_id):
    
    JOB_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    target_url = JOB_URL.format(job_id)
    try:
        response = requests.get(target_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            description_box = soup.find("div", class_="show-more-less-html__markup")
            
            if description_box:
                return description_box.get_text(strip=True)
            else:
                return "Description not found"
        else:
            return f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def scrape_linkedin_jobs(keyword, location, pages=1):

    job_list = []

    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    print(f"Starting scrape Linkedin Jobs for {keyword} in {location}")

    for page in range(pages):
        start_offset = page * 25
        params = {
            "keywords": keyword,
            "location": location,
            "start": start_offset
        }

        try:
            response = requests.get(SEARCH_URL, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"Scrape failed for page {page+1}. Status code:{response.status_code}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("li")
            
            for card in job_cards:
                title_tag = card.find("h3", class_="base-search-card__title")
                company_tag = card.find("h4", class_="base-search-card__subtitle")
                location_tag = card.find("span", class_="job-search-card__location")
                date_tag = card.find("time", class_="job-search-card__listdate")
                link_tag = card.find("a", class_="base-card__full-link")
                jobid_tag = card.find("div", class_="base-card")
                id = jobid_tag['data-entity-urn'].split(":")[-1]

                job_data = {
                    "Title": title_tag.text.strip() if title_tag else "NA",
                    "Company": company_tag.text.strip() if company_tag else "NA",
                    "Location": location_tag.text.strip() if location_tag else "NA",
                    "Date_Posted": date_tag['datetime'] if date_tag else "NA",
                    "Description": get_job_description(id),
                    "Link": link_tag['href'] if link_tag else "NA"
                }
                
                job_list.append(job_data)
            
            print(f"Page {page+1} complete. Total jobs: {len(job_list)}")
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            return f"Error: {e}"
    
    return pd.DataFrame(job_list)  
