import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {EcsStack} from "./ecs-stack";
import {VpcStack} from "./vpc-stack";
import {genericLambdaStack} from "./generic-lambda-stack";
import {StorageStack} from "./storage-stack";
import {LambdaAndSqsStack} from "./lambda-and-sqs-stack";


export class AppStage extends cdk.Stage {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // create vpc
        const vpcStack = new VpcStack(this, 'CloudCourseWorkVpcStack', {})

        // create s3 bucket
        const storageStack = new StorageStack(this, 'CloudCourseWorkStorageStack', {});

        // create lambdas
        const tripMgrStack = new genericLambdaStack(this, 'CloudCourseWorkTripMgrStack', {
            name: 'CloudCourseWorkTripMgr',
            s3Bucket: storageStack.lambdaBucket,
            s3Key: 'tripMgr.zip',
            usersDynamodbTable: storageStack.usersDynamoDbTable,
            tripsDynamodbTable: storageStack.tripsDynamoDbTable,
        });

        const accountMgrStack = new genericLambdaStack(this, 'CloudCourseWorkAccountMgrStack', {
            name: 'CloudCourseWorkAccountMgr',
            s3Bucket: storageStack.lambdaBucket,
            s3Key: 'accountMgr.zip',
            usersDynamodbTable: storageStack.usersDynamoDbTable,
            tripsDynamodbTable: storageStack.tripsDynamoDbTable,
        });

        const failedRequestStack = new LambdaAndSqsStack(this, 'CloudCourseWorkFailedRequestStack', {
            name: 'CloudCourseWorkFailedRequestMgr',
            s3Bucket: storageStack.lambdaBucket,
            s3Key: 'failedRequestMgr.zip',
            failedRequestsDynamodbTable: storageStack.failedRequestDynamoDbTable,
        });

        // create ecs, load balancer, and auto-scaling cluster
        const ecsStack = new EcsStack(this, 'CloudCourseWorkEcsStack', {
            vpc: vpcStack.vpc,
            tokenDynamoDbTable: storageStack.tokensDynamoDbTable,
            environmentVariables: {
                'TRIP_MGR_ARN': tripMgrStack.lambdaFunction.functionArn,
                'USER_MGR_ARN': accountMgrStack.lambdaFunction.functionArn,
                'TOKEN_DYNAMODB_TABLE': storageStack.tokensDynamoDbTable.tableName,
                'FAILED_REQUEST_SQS_QUEUE': failedRequestStack.sqsQueue.queueUrl,
                'AWS_DEFAULT_REGION': 'eu-west-1',
            },
            lambda_resources: [
                tripMgrStack.lambdaFunction,
                accountMgrStack.lambdaFunction
            ],
            failedRequestsSQSQueue: failedRequestStack.sqsQueue,
        });
    }
}