# Trip Mgr lambda

### How to run the project locally
```bash
```

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

### Prepare and push zip lambda to s3
```bash
zip -r out/tripMgr.zip src/*
aws s3 cp out/tripMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-ocdtc3iwmdvh/tripMgr.zip
```