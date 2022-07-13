import boto3
def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        content = s3.get_object(
            Bucket='content-saahil-chadha',
            Key='content.json'
        )
        response = {
            "statusCode": 200,
            "body": content['Body'].read().decode('UTF-8')
        }
        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error - {str(e)}"
        }
