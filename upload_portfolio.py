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

s3 = boto3.resource('s3')
code_bucket = s3.Bucket('codebuild-portfolio')
project_bucket = s3.Bucket('portfolio.semantiqlabs.com')

ram_stored_zip = StringIO.StringIO()

code_bucket.download_fileobj('CodeBuildPortfolio',ram_stored_zip)

with zipfile.ZipFile(ram_stored_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        project_bucket.upload_fileobj(obj,nm,
          ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
        project_bucket.Object(nm).Acl().put(ACL='public-read')
