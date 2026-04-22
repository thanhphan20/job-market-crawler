import os
from typing import TypedDict, Optional
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from dotenv import load_dotenv

# Load secret variables from .env
load_dotenv()

Entry = TypedDict(
    "Entry",
    {
        "elem_id": str,
        "title": str,
        "url": str,
        "company": str,
        "address": str,
        "benefits": Optional[str],
        "salary": Optional[str],
        "skills_and_experience": Optional[str],
    },
    total=False,
)

import time
import random

# Common headers to mimic a browser accurately
headers = {
    "authority": "itviec.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}


def scrap_itviec(limit: int, start_page: int = 1, end_page: int = 5) -> list[Entry]:
    results: list[Entry] = []
    queries = ["backend", "fullstack-developer", "java", "software-engineer"]
    seen_ids = set()

    # Use curl_cffi to bypass Cloudflare TLS fingerprinting
    # impersonate="chrome" makes it look like a real Chrome browser
    req_session = curl_requests.Session(impersonate="chrome")
    req_session.headers.update(headers)

    # Get credentials from env
    session_cookie = os.getenv("ITVIEC_SESSION")
    auth_token_cookie = os.getenv("ITVIEC_TOKEN")

    if session_cookie:
        req_session.cookies.set("_ITViec_session", session_cookie, domain="itviec.com")
    if auth_token_cookie:
        req_session.cookies.set("auth_token", auth_token_cookie, domain="itviec.com")

    for page_num in range(start_page, end_page + 1):
        print(f"Scraping page {page_num}...")
        for query in queries:
            url = f"https://itviec.com/it-jobs/{query}?page={page_num}"
            try:
                page = req_session.get(url, timeout=15)
                if page.status_code == 403:
                    print(
                        f"Warning: Got 403 for {url}. ITViec is blocking the request."
                    )
                    continue
                page.raise_for_status()
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue

            soup = BeautifulSoup(page.content, "html.parser")
            elems = soup.find_all(class_="job-card")

            for elem in elems:
                job_key = elem.attrs.get("data-job-key", "")
                if job_key in seen_ids:
                    continue

                if len(results) >= limit:
                    return results

                seen_ids.add(job_key)
                data: Entry = dict()
                data["elem_id"] = job_key
                title_elem = elem.find(class_="job-card-title") or elem.find("h3")
                data["title"] = title_elem.text.strip() if title_elem else ""

                job_url = elem.attrs.get("data-search--job-selection-job-url-value")
                if not job_url:
                    a_tag = elem.find(
                        "a", {"data-search--job-selection-target": "jobTitle"}
                    )
                    if a_tag and "href" in a_tag.attrs:
                        job_url = a_tag["href"]

                data["url"] = job_url
                data["skills_and_experience"] = ""
                data["company"] = ""
                data["address"] = ""
                data["salary"] = ""
                data["benefits"] = ""

                company_elem = elem.find(class_="ims-2") or elem.find(
                    "a", href=lambda x: x and "/companies/" in x
                )
                if company_elem:
                    data["company"] = company_elem.text.strip()

                address_div = elem.find("div", title=True)
                if address_div and "map-pin" in str(
                    address_div.find_previous_sibling()
                ):
                    data["address"] = address_div.get("title")
                else:
                    loc_elem = elem.find(
                        lambda tag: (
                            tag.name == "div"
                            and tag.has_attr("title")
                            and not tag.has_attr("class")
                        )
                    )
                    if loc_elem:
                        data["address"] = loc_elem.get("title")

                salary_elem = elem.find(class_="sign-in-view-salary") or elem.find(
                    class_="salary"
                )
                if salary_elem:
                    data["salary"] = salary_elem.text.strip()

                if data["url"]:
                    if not data["url"].startswith("/"):
                        data["url"] = "/" + data["url"]
                    jd_link = f"https://itviec.com{data['url']}"

                    for jd_retry in range(2):  # 2 attempts for JD
                        try:
                            time.sleep(random.uniform(1, 2))
                            print(
                                f"  - Fetching job {len(results) + 1}/{limit}: {jd_link[:60]}..."
                            )
                            # Crucial: Referer must be the search page
                            req_session.headers.update({"Referer": url})
                            jd_page = req_session.get(jd_link, timeout=15)

                            if jd_page.status_code == 403:
                                wait_time = 2 if jd_retry == 0 else 4
                                print(
                                    f"403 on JD {jd_link}. Waiting {wait_time}s... (Retry {jd_retry + 1}/2)"
                                )
                                time.sleep(wait_time)
                                continue

                            jd_page.raise_for_status()
                            jd_soup = BeautifulSoup(jd_page.content, "html.parser")

                            if not data["company"]:
                                company_header = jd_soup.find(
                                    class_="normal-text text-rich-grey"
                                ) or jd_soup.find(
                                    "a", href=lambda x: x and "/companies/" in x
                                )
                                data["company"] = (
                                    company_header.text.strip()
                                    if company_header
                                    else ""
                                )

                            if not data["address"]:
                                address_span = jd_soup.find(
                                    "span", class_="small-text text-rich-grey"
                                )
                                data["address"] = (
                                    address_span.text.strip() if address_span else ""
                                )

                            skills_section = jd_soup.find(
                                "section", class_="job-experiences"
                            )
                            if skills_section:
                                data["skills_and_experience"] = skills_section.get_text(
                                    separator=" \n ", strip=True
                                )
                            else:
                                skills_header = jd_soup.find(
                                    lambda tag: (
                                        tag.name in ["h2", "h3"]
                                        and tag.get_text()
                                        and "skills and experience"
                                        in tag.get_text().lower()
                                    )
                                )
                                if skills_header:
                                    skills_div = skills_header.find_parent(
                                        "div", class_="job-details__paragraph"
                                    )
                                    if skills_div:
                                        data["skills_and_experience"] = (
                                            skills_div.get_text(
                                                separator=" \n ", strip=True
                                            )
                                        )
                                    else:
                                        sibling = skills_header.find_next_sibling()
                                        if sibling:
                                            data["skills_and_experience"] = (
                                                sibling.get_text(
                                                    separator=" \n ", strip=True
                                                )
                                            )
                            break  # Success
                        except Exception as e:
                            print(f"Error JD {jd_link}: {e}")
                            if jd_retry == 1:
                                break

                results.append(data)

    return results


import pandas as pd


def run_itviec_crawler(limit=20, output_path="data/itviec_jobs.csv"):
    """
    Orchestrates the scraping and saving of ITviec jobs.
    """
    print(f"\n[*] Starting ITviec Crawler (Limit: {limit})...")
    data = scrap_itviec(limit=limit)

    if data:
        df = pd.DataFrame(data)
        # Ensure the directory exists
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"[SUCCESS] Saved {len(df)} jobs to {output_path}")
        except Exception as e:
            print(f"[WARN] Could not save ITviec data locally: {e}")
            print("[INFO] Data remains in memory for cloud sync if active.")
        return df
    else:
        print("[!] No data collected from ITviec.")
        return None


if __name__ == "__main__":
    run_itviec_crawler()
