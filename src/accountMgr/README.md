# Account Mgr Lambda

### How to run the project locally


### How to test the project locally with moto


### Create the environment


### Update the environment 
```bash
pip freeze > requirements.txt
```


### Prepare and push zip lambda to s3
```bash
zip -r out/accountMgr.zip src/*
aws s3 cp out/accountMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9/tripMgr.zip
```