# Account Mgr Lambda

### How to run the project locally


### How to test the project locally with moto


### Create the environment


### Update the environment 
```bash
pip freeze > requirements.txt
```


### Prepare and push zip lambda to s3
Note: you will manually have to install any updates or new packages to package with
```pip install -t location packageName```
```bash
deactivate
rm out/accountMgr.zip
rm -r package
mkdir package
cd package
# specify the packages you want to install here
pip install -t . requests==2.28.2
# ---------------------------------------------
zip -r ../out/accountMgr.zip .
cd ..
zip -r out/accountMgr.zip src
aws s3 cp out/accountMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9/accountMgr.zip
```