from typing import TypedDict, Optional
import requests
from bs4 import BeautifulSoup

Entry = TypedDict('Entry', {
    'elem_id': str,
    'title': str,
    'url': str,
    'company': str,
    'address': str,
    'benefits': Optional[str],
    'salary': Optional[str],
    'skills_and_experience': Optional[str]
}, total=False)


# simulate a login to get salary range
# get this session from real login, this may expires after a while
# to retrieve the session id from cookie: https://developers.google.com/web/tools/chrome-devtools/storage/cookies
# then copy the string of key "_ITViec_session" at site itviec.com and paste it here
session = '[b1695776a7dcd41e]'

# Common headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://itviec.com/',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
}

def scrap_itviec(page_num: int, limit: int) -> list[Entry]:
    results: list[Entry] = []
    
    queries = ['backend', 'fullstack-developer', 'java']
    
    # Create a session to persist cookies and headers
    req_session = requests.Session()
    req_session.headers.update(headers)
    if session and session != '[input the string of _ITViec_session]':
        req_session.cookies.set('_ITViec_session', session, domain='itviec.com')
    
    # Track seen IDs to avoid duplicates across different queries
    seen_ids = set()
    
    for query in queries:
        url = f'https://itviec.com/it-jobs/{query}?page={page_num}'
        try:
            page = req_session.get(url, timeout=15)
            if page.status_code == 403:
                print(f"Warning: Got 403 for {url}. ITViec is blocking the request.")
                continue
            page.raise_for_status()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(page.content, 'html.parser')

        elems = soup.find_all(class_='job-card')

        for elem in elems:
            job_key = elem.attrs.get('data-job-key', '')
            if job_key in seen_ids:
                continue
            
            if len(results) >= limit:
                return results

            seen_ids.add(job_key)
            data: Entry = dict()
            data['elem_id'] = job_key
            title_elem = elem.find(class_='job-card-title') or elem.find('h3')
            data['title'] = title_elem.text.strip() if title_elem else ''
            
            # The URL for content is in data-search--job-selection-job-url-value
            job_url = elem.attrs.get('data-search--job-selection-job-url-value')
            if not job_url:
                a_tag = elem.find('a', {'data-search--job-selection-target': 'jobTitle'})
                if a_tag and 'href' in a_tag.attrs:
                    job_url = a_tag['href']
            
            data['url'] = job_url
            data['skills_and_experience'] = ''
            data['company'] = ''
            data['address'] = ''
            data['salary'] = ''
            data['benefits'] = ''

            # Get company name
            company_elem = elem.find(class_='ims-2') or elem.find('a', href=lambda x: x and '/companies/' in x)
            if company_elem:
                data['company'] = company_elem.text.strip()

            # Get address from listing if available (often in a div with map-pin icon)
            address_div = elem.find('div', title=True)
            if address_div and 'map-pin' in str(address_div.find_previous_sibling()):
                 data['address'] = address_div.get('title')
            else:
                 # Fallback search for title attribute which often contains the location
                 loc_elem = elem.find(lambda tag: tag.name == 'div' and tag.has_attr('title') and not tag.has_attr('class'))
                 if loc_elem:
                     data['address'] = loc_elem.get('title')

            # Get salary status from listing
            salary_elem = elem.find(class_='sign-in-view-salary') or elem.find(class_='salary')
            if salary_elem:
                data['salary'] = salary_elem.text.strip()

            if data['url']:
                # ensure url has leading slash
                if not data['url'].startswith('/'):
                    data['url'] = '/' + data['url']
                jd_link = f"https://itviec.com{data['url']}"
                try:
                    # The link we got usually points to /content which is an HTML fragment
                    jd_page = req_session.get(jd_link, timeout=10)
                    jd_page.raise_for_status()
                    jd_soup = BeautifulSoup(jd_page.content, 'html.parser')
                    
                    # Update company/address from JD if missing
                    if not data['company']:
                        company_header = jd_soup.find(class_='normal-text text-rich-grey') or jd_soup.find('a', href=lambda x: x and '/companies/' in x)
                        data['company'] = company_header.text.strip() if company_header else ''
                    
                    if not data['address']:
                        # The overview section often has the address
                        address_span = jd_soup.find('span', class_='small-text text-rich-grey')
                        data['address'] = address_span.text.strip() if address_span else ''
                    
                    # Extract skills and experience - it's often in its own <section>
                    skills_section = jd_soup.find('section', class_='job-experiences')
                    if skills_section:
                        data['skills_and_experience'] = skills_section.get_text(separator=' \n ', strip=True)
                    else:
                        # Fallback to header search
                        skills_header = jd_soup.find(lambda tag: tag.name in ['h2', 'h3'] and tag.get_text() and 'skills and experience' in tag.get_text().lower())
                        if skills_header:
                            skills_div = skills_header.find_parent('div', class_='job-details__paragraph')
                            if skills_div:
                                data['skills_and_experience'] = skills_div.get_text(separator=' \n ', strip=True)
                            else:
                                sibling = skills_header.find_next_sibling()
                                if sibling:
                                    data['skills_and_experience'] = sibling.get_text(separator=' \n ', strip=True)
                except Exception as e:
                    print(f"Error fetching JD from {jd_link}: {e}")

            results.append(data)

    return results
