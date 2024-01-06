import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import {IBucket} from "aws-cdk-lib/aws-s3";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";
import * as sqs from 'aws-cdk-lib/aws-sqs';

interface LambdaAndSqsStackStackProps extends cdk.StackProps {
    name: string;
    s3Bucket: IBucket;
    s3Key: string;
    failedRequestsDynamodbTable: DynamoDB.Table;
}

export class LambdaAndSqsStack extends cdk.Stack {

    readonly lambdaFunction: lambda.Function;
    readonly sqsQueue: sqs.Queue;

    constructor(scope: Construct, id: string, props: LambdaAndSqsStackStackProps) {
        super(scope, id, props);

        // create lambda
        this.lambdaFunction = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'src.index.main',
            code: lambda.Code.fromBucket(props.s3Bucket, props.s3Key),
            timeout: cdk.Duration.seconds(10),
            architecture: lambda.Architecture.ARM_64,
            environment: {
                'FAILED_REQUESTS_DYNAMODB_TABLE': props.failedRequestsDynamodbTable.tableName,
            }
        });

        // give lambda access to dynamodb
        props.failedRequestsDynamodbTable.grantReadWriteData(this.lambdaFunction);

        // create SQS
        this.sqsQueue = new sqs.Queue(this, `${props.name}SQS`, {
            visibilityTimeout: cdk.Duration.seconds(30),
        });

        new lambda.EventSourceMapping(this, `${props.name}EventSourceMapTrigger`, {
            target: this.lambdaFunction,
            eventSourceArn: this.sqsQueue.queueArn,
        });

        this.sqsQueue.grantConsumeMessages(this.lambdaFunction);
    }
}