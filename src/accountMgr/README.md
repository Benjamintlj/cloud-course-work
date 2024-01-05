# Account Mgr Lambda
Creates and manages accounts in the accounts dynamodb table.

### Create the environment
1. Create a `venv` directory
2. Create a new interpreter in PyCharm with python 3.9 and link it to the `venv` directory
3. Link requirements.txt to pycharm in Settings > Tools > Python Integrated Tools
4. Install the dependencies from requirements.txt

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