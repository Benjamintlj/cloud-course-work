# ECS running FastAPI

### How to run the project locally
```bash
TRIP_MGR_ARN="arn:aws:lambda:eu-west-1:203163753194:function:prod-CloudCourseWorkTripM-CloudCourseWorkTripMgr2C-ZvY6GC6vguAg"

docker build -t cloud-course-work-ecs-image . 
docker run -p 4003:80 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION -e TRIP_MGR_ARN=$TRIP_MGR_ARN cloud-course-work-ecs-image
```
It will be running on [localhost:4003](http://localhost:4003/).

### Create the environment


### Update the environment (make sure you are in the right environment)
```bash
pip freeze > requirements.txt
```

### Push to ECR
```bash
docker build -t cloud-course-work-ecs-image . 
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 203163753194.dkr.ecr.eu-west-1.amazonaws.com
docker tag cloud-course-work-ecs-image:latest 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
docker push 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
```