import requests
import base64
from flask import Flask, render_template, request
from flask_cors import CORS
from flask.json import jsonify
from flask_frozen import Freezer

app = Flask(__name__)
CORS(app)
freezer = Freezer(app)

def get_jwt():
    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }

    data = {
        'client_id': 'c003a37f-024f-462a-b36d-b001be4cd24a',
        'client_secret': '32a39620-32b3-4307-9aa1-511e3d7f48a8',
        'grant_type': 'client_credentials'
    }

    response = requests.post(
        'https://rest.arbeitsagentur.de/oauth/gettoken_cc', headers=headers, data=data, verify=False)

    return response.json()


def search(jwt, what, where, industry, jobtype, page, size):
    params = (
        ('angebotsart', int(jobtype)),
        ('page', page),
        ('pav', 'false'),
        ('size', size),
        ('umkreis', '25'),
        ('was', what),
        ('wo', where),
        ('berufsfeld', industry)
    )

    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get('https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs',
                            headers=headers, params=params, verify=False)
    return response.json()


def job_details(jwt, job_ref):

    headers = {
        'User-Agent': 'Jobsuche/2.9.3 (de.arbeitsagentur.jobboerse; build:1078; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get(
        f'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v2/jobdetails/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
        headers=headers, verify=False)

    return response.json()


def company_logo(jwt, hashId):
    
    headers = {
        'User-Agent': 'Jobsuche/2.9.3 (de.arbeitsagentur.jobboerse; build:1078; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
        'accept': 'image/png',
    }
    
    response = requests.get(
        f'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/ed/v1/arbeitgeberlogo/{hashId}',
        headers=headers, verify=False)

    return {"img": response.text, "status": response.status_code}

@app.route('/job-search')
def api_job_search():
    what = request.args.get('what', None)
    where = request.args.get('where', None)
    industry = request.args.get('industry', None)
    jobtype = request.args.get('type', 1)
    page_no = request.args.get('page_no', 1)
    page_size = request.args.get('page_size', 10)
    
    access_token = get_jwt()["access_token"]
    search_result = search(access_token, what, where, industry, jobtype, page_no,  page_size)
    results = []
    if search_result.get('stellenangebote'):
        for result in search_result['stellenangebote']:
            details = job_details(access_token, result["refnr"])
            details["logo"] = company_logo(access_token, result["hashId"])
            results.append(details)
    
    finalResults = {
        "jobs": results,
        "maxResults": search_result.get('maxErgebnisse')
    }
    
    return jsonify(finalResults)


if __name__ == '__main__':
    # app.run()
    freezer.freeze()
