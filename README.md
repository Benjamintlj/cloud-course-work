# Service-Centric & Cloud Computing - Assignment
This project is broken up into two parts:
1. The CDK this defines the infrastructure, including the pipeline which deploys the application, 
   defined in the `lib` directory.
2. The applications which can be found within the `src` directory. Which is made up of the following:
   1. ECS (container orchestration service), this is acts as a gateway & authenticator to the lambdas and other APIs.
   2. accountMgr (lambda), manages accounts.
   3. tripMgr (lambda), manages trips.

## CDK Notes
This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

### Useful commands for deploying & interacting with the CDK

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
