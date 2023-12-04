# Trip Mgr lambda

### How to run the project locally
1. install aws cli sam
2. install the pycharm plugin aws toolkit
3. edit the run configuration:
    1.  runtime: python3.9
    2.  architecture: arm64 (if you are on an m1 mac)
    3.  handler: index.main
    4.  input: use the SQS template and edit it to your needs

### How to test the project locally with moto


### Create the environment
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```

### Update the environment (make sure you are in the right environment)
```bash
source venv/bin/activate
pip freeze > src/requirements.txt
```

### Prepare and push zip lambda to s3
```bash
zip -r out/tripMgr.zip src/* -x src/requirements.txt
aws s3 cp out/tripMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-ocdtc3iwmdvh/tripMgr.zip
```