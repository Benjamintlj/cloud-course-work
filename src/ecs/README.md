# ECS running FastAPI
Acts as a gateway & authenticator to the lambdas and other APIs.

### How to run the project locally
```bash
docker build -t cloud-course-work-ecs-image . 
docker run -p 4003:80 --env-file .env -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY cloud-course-work-ecs-image
```
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
It will be running on [localhost:4003](http://localhost:4003/).

### Create the environment
1. Create a `venv` directory
2. Create a new interpreter in PyCharm with python 3.9 and link it to the `venv` directory
3. Link requirements.txt to pycharm in Settings > Tools > Python Integrated Tools
4. Install the dependencies from requirements.txt


### Run the project locally and not inside a container
Prerequisite: you must have the environment set up and be singed in to aws cli.
```bash
export FAILED_REQUEST_SQS_QUEUE="https://sqs.eu-west-1.amazonaws.com/203163753194/prod-CloudCourseWorkFailedRequest-CloudCourseWorkFailedRequestMgrSQ-LJerBDUtL5wr"
export TRIP_MGR_ARN="arn:aws:lambda:eu-west-1:203163753194:function:prod-CloudCourseWorkTripM-CloudCourseWorkTripMgr2C-eLL8llBozOko"
export USER_MGR_ARN="arn:aws:lambda:eu-west-1:203163753194:function:prod-CloudCourseWorkAccou-CloudCourseWorkAccountMg-hUGTc4n0SnjO"
export TOKEN_DYNAMODB_TABLE="prod-CloudCourseWorkStorageStack-cloudCourseWorkTokensDynamoDbTableE313728A-SV35MP511AZK"
uvicorn src.main:app --host=0.0.0.0 --port=80
```

### Update the environment (make sure you are in the right environment)
```bash
pip freeze > requirements.txt
```

### Push to ECR
_**NOTE: DO NOT INCLUDE THE `.env` FILE!!!**_
```bash
docker build -t cloud-course-work-ecs-image . 
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 203163753194.dkr.ecr.eu-west-1.amazonaws.com
docker tag cloud-course-work-ecs-image:latest 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
docker push 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
```