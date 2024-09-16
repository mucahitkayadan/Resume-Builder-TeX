import requests
from bs4 import BeautifulSoup

def parse_indeed_job(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    session.headers.update(headers)
    
    response = session.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url} with status code {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    job_title = soup.find('h1', {'class': 'jobsearch-JobInfoHeader-title'}).text.strip()
    company = soup.find('div', {'class': 'jobsearch-InlineCompanyRating'}).find('div').text.strip()
    location = soup.find('div', {'class': 'jobsearch-JobInfoHeader-subtitle'}).find_all('div')[1].text.strip()
    job_description = soup.find('div', {'class': 'jobsearch-jobDescriptionText'}).text.strip()

    job_details = {
        'title': job_title,
        'company': company,
        'location': location,
        'description': job_description
    }

    return job_details

# Example usage
if __name__ == "__main__":
    url = 'https://www.indeed.com/viewjob?jk=b41d90cb0d2d81c7'
    job_details = parse_indeed_job(url)
    print(job_details)
