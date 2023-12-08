# Trip Mgr lambda

### How to run the project locally


### How to test the project locally with moto


### Create the environment


### Update the environment (make sure you are in the right environment)
```bash
pip freeze > requirements.txt
```

### Prepare and push zip lambda to s3
```bash
zip -r out/tripMgr.zip src/* -x __pycache__/
aws s3 cp out/tripMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9/tripMgr.zip
```