import json

"""
Intent: extract the contents of the build bucket codebuild-portfolio and upload the contents to project bucket portfolio.semantiqlabs.com
Steps:
    1. install aws cli
    2. configure aws
    3. using boto3 resource, extract contents of build bucket
    4. store the downloaded content in RAM
    5. upload tthe contents to project bucket
"""

import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    # TODO implement

    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:092781121214:PortfolioDeploy')

    try:
        job = event["CodePipeline.job"]["data"]["inputArtifacts"][0]["location"]["s3Location"]
        print(job)

        # code_bucket = s3.Bucket('codebuild-portfolio')
        code_bucket = s3.Bucket(job["bucketName"])
        object_key = job["objectKey"]
        project_bucket = s3.Bucket('portfolio.semantiqlabs.com')

        ram_stored_zip = StringIO.StringIO()

        code_bucket.download_fileobj(object_key,ram_stored_zip)

        with zipfile.ZipFile(ram_stored_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                project_bucket.upload_fileobj(obj,nm,
                  ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                project_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject='Portfolio deployed', Message='Porfolio changes deployed successfully')
        print("deployed")

        code_pipeline = boto3.client('codepipeline')
        code_pipeline.put_job_success_result(jobId=event["CodePipeline.job"]["id"])

    except:
        topic.publish(Subject='Portfolio deployment failed', Message='Porfolio changes deployment failed, check the cloudwatch errors for more info')
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('deployment complete')
    }
