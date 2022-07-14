import boto3
import json
import datetime
import requests
import logging
from utils import read_secrets
from linkedin_api import Linkedin

LINKEDIN_USERNAME = 'saahil301@gmail.com'
LINKEDIN_PASSWORD = read_secrets()['LINKEDIN_PASSWORD']
LINKEDIN_PROFILE = 'saahil-chadha'

BUCKET_NAME = 'content-saahil-chadha'
OBJECT_KEY = 'content.json'

SLACK_HOOK = 'https://hooks.slack.com/services/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'

ID = 'id'
NAME = 'name'
EXPERIENCES = 'experiences'
DATE = 'date'
TITLE = 'title'
POSITION = 'position'
DESCRIPTION = 'description'
ICON = 'icon'

logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        profile = api.get_profile(LINKEDIN_PROFILE)

        education_experiences = []
        for school in profile['education']:
            start_year = school['timePeriod']['startDate']['year']
            try: 
                end_year = school['timePeriod']['endDate']['year']
            except KeyError: 
                end_year = 'Present'
            degree = school.get('fieldOfStudy')
            school_name = school['schoolName']
            description = school.get('activities')
            school_data = {
                DATE: f"{start_year} - {end_year}",
                TITLE: degree,
                POSITION: school_name,
                DESCRIPTION: description,
                ICON: 'icon-school'
            }
            education_experiences.append(school_data)
        
        education_data = {
            ID: 'Education',
            NAME: 'Education',
            EXPERIENCES: education_experiences
        }

        work_experiences = []
        for experience in profile['experience']:
            start_date = experience['timePeriod']['startDate']
            start_month = datetime.datetime.strptime(str(start_date['month']), "%m").strftime("%B")
            start_year = start_date['year']
            start_month_year = f"{start_month} {start_year}"

            try:
                end_date = experience['timePeriod']['endDate']
                end_month = datetime.datetime.strptime(str(end_date['month']), "%m").strftime("%B")
                end_year = end_date['year']
                end_month_year = f"{end_month} {end_year}"
            except KeyError: 
                end_month_year = 'Present'

            title = experience['title']
            company = experience['companyName']
            description = experience['description']

            experience_data = {
                DATE: f"{start_month_year} - {end_month_year}",
                TITLE: title,
                POSITION: company,
                DESCRIPTION: description,
                ICON: 'icon-code'
            }
            work_experiences.append(experience_data)
        
        work_data = {
            ID: 'Experience',
            NAME: 'Work Experience',
            EXPERIENCES: work_experiences
        }

        award_experiences = []
        for honor in profile['honors']: 
            year = str(honor['issueDate']['year'])
            title = honor['title']
            issuer = honor['issuer']
            description = honor['description']
            honor_data = {
                DATE: year,
                TITLE: title,
                POSITION: issuer,
                DESCRIPTION: description,
                ICON: 'icon-trophy'
            }
            award_experiences.append(honor_data)
        
        award_data = {
            ID: 'Awards',
            NAME: 'Awards',
            EXPERIENCES: award_experiences
        }

        data = {"data": [education_data, work_data, award_data]}

        s3 = boto3.client('s3')
        original_content = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=OBJECT_KEY
        )['Body'].read().decode('UTF-8')
        
        if json.loads(original_content) != data:
            s3.put_object(
                Body=(bytes(json.dumps(data).encode('UTF-8'))),
                Bucket=BUCKET_NAME,
                Key=OBJECT_KEY
            )

            success_msg = 'Successfully synced LinkedIn!'
            print(success_msg)
            requests.post(
                url=SLACK_HOOK,
                json = {
                    "text": success_msg
                }
            )
        else: 
            print('No changes found')
    except Exception as e:
        error_msg = f"ERROR when syncing LinkedIn! - {e}"
        print(error_msg)
        requests.post(
            url=SLACK_HOOK,
            json = {
                "text": error_msg
            }
        )
