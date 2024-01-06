# Failed Trip Mgr Lambda
Stores failed requests on dynamodb.

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
_Note: that no other dependencies are required for this lambda._
```bash
zip -r out/failedRequestMgr.zip src/* -x __pycache__/
aws s3 cp out/failedRequestMgr.zip s3://prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9/failedRequestMgr.zip
aws lambda update-function-code --function-name arn:aws:lambda:eu-west-1:203163753194:function:prod-CloudCourseWorkFaile-CloudCourseWorkFailedReq-XzjLnsosQFlt --s3-bucket prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9 --s3-key failedRequestMgr.zip
q
```
