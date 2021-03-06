# LinkedInToPersonalWebsite

Using AWS Lambda, S3, and API Gateway to keep my [personal website](http://saahilchadha.com/) synced with my LinkedIn. What's the point of a personal website that is literally just the same as my LinkedIn? Great question, we'll see...

![Diagram](https://github.com/saahilchadha1/LinkedInToPersonalWebsite/blob/master/LinkedInToGithubPagesDiagram.drawio.png?raw=true)

## API Gateway 
``` 
GET /api/get_content

200 status code
[
  {
    "id": "Education",
    "name": "Education",
    "experiences": [
      {
        "date": "2018-2021",
        "title": "Bachelor of Arts in Computer Science, Pre-Med",
        "position": "The University of California, Berkeley",
        "description": "Relevant Coursework: Data Structures, Artificial Intelligence, Probability, Statistics",
        "icon": "icon-school"
      }, ...
    ]
  }, ...
]

500 status code
{
  "msg": "Unable to complete request -- {localized error string}"
}
```

## Lambdas
### GetContent Lambda
API Gateway proxy lambda. Simply reads the `content.json` file from the `Content` S3 bucket and returns it as indicated above. 

### SyncContent Lambda 
This is part of the ingestion pipeline. Triggered by a monthly CloudWatch job, it reads gets the latest profile information from the LinkedIn API, transforms the profile information into a properly formatted JSON, and compares with the existing `content.json` file in the `Content` S3 bucket. If there are any differences, it overwrites the `content.json` file with the newer version and sends a Slack notification.

## Secrets
For now, my LinkedIn password is stored in a gitignore'd `secrets.json` file in the `Lambdas/SyncContent/` directory

## Deploying to AWS Lambda
Since this is a small project, I just zip up the lambda handler and runtime dependencies e.g. 
```
cd Lambdas/SyncContent/package/
zip -r ../my-deployment-package.zip .
cd ..
zip -g my-deployment-package.zip lambda_function.py utils.py secrets.json 
```