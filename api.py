import logging
import time

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

db = SQLAlchemy()
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///listings.db'
db.init_app(app)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

job_data = []


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    job_link = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(255), nullable=False)
    isFavorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Listing('{self.job_title}', '{self.company}', '{self.location}', '{self.job_link}', '{self.salary}', '{self.isFavorite}')"

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'job_link': self.job_link,
            'salary': self.salary,
            'isFavorite': self.isFavorite
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    job_link = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Favorite('{self.job_title}', '{self.company}', '{self.location}', '{self.job_link}', '{self.salary}')"

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'job_link': self.job_link,
            'salary': self.salary,
        }


@app.route('/run-script', methods=['POST', 'OPTIONS'])
def run_script():
    global job_data
    job_data = []

    db.create_all()

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
            Listing.query.delete()
            db.session.commit()

            jobs = scraper(query, location)
            job_data = jobs
            return jsonify({'jobs': jobs})
        except Exception as e:
            app.logger.error(f"Failed to scrape jobs. Error: {e}")
            return jsonify({"error": str(e)}), 500


@app.route('/api/favorites/<int:job_id>', methods=['POST', 'OPTIONS'])
def add_favorite(job_id):

    db.create_all()

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    elif request.method == 'POST':
        try:
            listing = Listing.query.get(job_id)
            if listing:
                existing_favorite = Favorite.query.filter_by(
                    listing_id=listing.id).first()
                if existing_favorite is None:
                    favorite = Favorite(
                        listing_id=listing.id,
                        job_title=listing.job_title,
                        company=listing.company,
                        location=listing.location,
                        job_link=listing.job_link,
                        salary=listing.salary,
                    )
                    db.session.add(favorite)
                    db.session.commit()
                return jsonify({'message': 'Marked as favorite'}), 200
            else:
                return jsonify({"error": f"No listing with id {item_id}"}), 404
        except Exception as e:
            app.logger.error(f"Failed to mark listing as favorite. Error: {e}")
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
        data = Listing.query.all()
        if data:
            return jsonify([item.to_dict() for item in data])
        else:
            return jsonify([]), 200
    except Exception as e:
        app.logger.error(f"Failed to read listings.db. Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        data = Favorite.query.all()
        return jsonify([item.to_dict() for item in data]), 200
    except Exception as e:
        app.logger.error(f"Failed to read favorites. Error: {e}")
        return jsonify({"error": str(e)}), 500


def scraper(query, location):
    num_pages = 1
    start_list = [page * 10 for page in range(num_pages)]
    base_url = 'https://www.indeed.com'

    options = Options()
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    for start in start_list:
        url = base_url + f'/jobs?q={query}&l={location}&start={start}'
        print(f"Scraping URL: {url}")
        driver.execute_script(f"window.open('{url}', 'tab{start}');")
        time.sleep(1)

    for start in start_list:
        driver.switch_to.window(f'tab{start}')

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('td', {'class': 'resultContent'})

        for job in items:
            try:
                job_link_text = job.find('a').get('href')
                job_title = job.find('span', title=True).text.strip()
                company = job.find(
                    'span', class_='companyName').text.strip()
                location = job.find(
                    'div', class_='companyLocation').text.strip()
                isFavorite = False
                if job.find('div', class_='metadata salary-snippet-container'):
                    salary = job.find(
                        'div', class_='metadata salary-snippet-container').text
                elif job.find('div', class_='metadata estimated-salary-container'):
                    salary = job.find(
                        'div', class_='metadata estimated-salary-container').text
                else:
                    salary = ""

                job_link = base_url + job_link_text

                job_info = Listing(job_title=job_title, company=company,
                                   location=location, job_link=job_link, salary=salary, isFavorite=isFavorite)
                db.session.add(job_info)
                db.session.commit()
                job_data.append({
                    'Job Title': job_title,
                    'Company': company,
                    'Location': location,
                    'Job Link': job_link,
                    'Salary': salary,
                    'Favorite': isFavorite
                })
            except Exception as e:
                app.logger.error(f"Failed to process a job. Error: {e}")

        driver.close()

    driver.quit()
    return job_data


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
