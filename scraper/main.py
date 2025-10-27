import requests
import datetime
from typing import Optional
from data.getter import get_board_token


URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

def parse_iso_datetime(iso_datetime: str) -> datetime.datetime:
    cleaned_string = iso_datetime[:-3] + iso_datetime[-2:]
    format_code = "%Y-%m-%dT%H:%M:%S%z"
    return datetime.datetime.strptime(cleaned_string, format_code)


def get_jobs(board_token: str, date: Optional[datetime.date] = None, position: Optional[str] = None) -> list[dict]:
    """Fetch jobs from Greenhouse API, optionally filtered by date."""
    jobs = []
    try:
        response = requests.get(URL.format(board_token=board_token))
        response.raise_for_status()
        jobs_data = response.json()
        
        for job in jobs_data.get("jobs", []):
            try:
                updated_at = parse_iso_datetime(job.get("updated_at"))
                if date is not None:
                    updated_date = updated_at.date()
                    filter_date = date.date() if hasattr(date, 'date') else date
                    if updated_date < filter_date:
                        continue
                # Skip jobs that are PhD positions
                if "PHD".lower() in job.get("title", "").lower():
                    continue
                if position is not None:
                    if position.lower() not in job.get("title", "").lower():
                        continue
                jobs.append({
                    "id": job.get("id"),
                    "internal_id": job.get("internal_id"),
                    "title": job.get("title"),
                    "url": job.get("absolute_url"),
                    "updated_at": updated_at.isoformat(),
                })
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping job due to date parsing error: {e}")
                continue
                
    except requests.RequestException as e:
        print(f"Error fetching jobs: {e}")
        return []
    
    return jobs


def get_new_jobs(position: Optional[str] = None) -> list[dict]:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    ret = []
    for board_token in get_board_token():
        jobs = get_jobs(board_token=board_token, date=yesterday, position=position)
        ret.extend(jobs)
    return ret

if __name__ == "__main__":
    jobs = get_new_jobs(position="intern")
    print(jobs)