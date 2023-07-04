from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import csv
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging


app = Flask(__name__)
CORS(app)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

job_data = []


@app.route('/run-script', methods=['POST', 'OPTIONS'])
def run_script():
    global job_data

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        } 
        return ('', 204, headers)
    
    elif request.method == 'POST':
        data = request.get_json()
        query = data['query']
        location = data['location']
        try: 
            jobs = scraper(query, location)
            job_data = jobs
            return jsonify({'jobs': jobs})
        except Exception as e:
            app.logger.error(f"Failed to scrape jobs. Error: {e}")
            return jsonify({"error": str(e)}), 500

   
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    return response


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        data = pd.read_csv('job_results.csv')
        return jsonify(data.to_dict('records'))
    except Exception as e:
        app.logger.error(f"Failed to read job_results.csv. Error: {e}")


def scraper(query, location):
    num_pages = 1
    start_list = [page * 10 for page in range(num_pages)]
    base_url = 'https://www.indeed.com'

    options = Options()
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for start in start_list:
        url = base_url + f'/jobs?q={query}&l={location}&start={start}'
        print(f"Scraping URL: {url}")
        driver.execute_script(f"window.open('{url}', 'tab{start}');")
        time.sleep(1)

    with open(f'job_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Job Title', 'Company', 'Location', 'Job Link', 'Salary'])
        for start in start_list:
            driver.switch_to.window(f'tab{start}')

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.find_all('td', {'class': 'resultContent'})

            for job in items:
                try:
                    s_link = job.find('a').get('href')
                    job_title = job.find('span', title=True).text.strip()
                    company = job.find('span', class_='companyName').text.strip()
                    location = job.find('div', class_='companyLocation').text.strip()
                    if job.find('div', class_='metadata salary-snippet-container'):
                        salary = job.find('div', class_='metadata salary-snippet-container').text
                    elif job.find('div', class_='metadata estimated-salary-container'):
                        salary = job.find('div', class_='metadata estimated-salary-container').text
                    else:
                        salary = ""

                    job_link = base_url + s_link

                    job_info = [job_title, company, location, job_link, salary]
                    writer.writerow(job_info)
                    job_data.append({
                        'Job Title': job_title,
                        'Company': company,
                        'Location': location,
                        'Job Link': job_link,
                        'Salary': salary
                    })
                except Exception as e:
                    app.logger.error(f"Failed to process a job. Error: {e}")

            driver.close()

    driver.quit()
    return job_data

if __name__ == '__main__':
    app.run(debug=True)