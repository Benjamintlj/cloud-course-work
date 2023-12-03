# ECS running FastAPI

### How to run the project locally
```bash
docker build -t cloud-course-work-ecs-image . 
docker run -p 4991:80 cloud-course-work-ecs-image
```
It will be running on [localhost:4991](http://localhost:4991/).

### Create the environment
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Update the environment (make sure you are in the right environment)
```bash
source venv/bin/activate
pip freeze > requirements.txt
```

### Push to ECR
```bash
docker build -t cloud-course-work-ecs-image . 
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 203163753194.dkr.ecr.eu-west-1.amazonaws.com
docker tag cloud-course-work-ecs-image:latest 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
docker push 203163753194.dkr.ecr.eu-west-1.amazonaws.com/cloud-course-work-ecs-repo:latest
```