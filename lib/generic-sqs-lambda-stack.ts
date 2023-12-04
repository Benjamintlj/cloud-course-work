import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import {IBucket} from "aws-cdk-lib/aws-s3";
import * as sqs from "aws-cdk-lib/aws-sqs"
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as ssm from 'aws-cdk-lib/aws-ssm';

interface SqsLambdaStackProps extends cdk.StackProps {
    name: string;
    s3Bucket: IBucket;
    s3Key: string;
}

export class genericSqsLambdaStack extends cdk.Stack {

    readonly sqsQueue: sqs.Queue;
    readonly lambdaFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: SqsLambdaStackProps) {
        super(scope, id, props);

        const queueName = props.name + 'Queue';

        this.sqsQueue = new sqs.Queue(this, queueName, {
            queueName: queueName,
        });

        const urlParameterName = props.name + 'QueueUrl';

        new ssm.StringParameter(this, urlParameterName, {
            parameterName: urlParameterName,
            stringValue: this.sqsQueue.queueUrl,
        });

        this.lambdaFunction = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'src/index.main',
            code: lambda.Code.fromBucket(props.s3Bucket, props.s3Key),
            timeout: cdk.Duration.seconds(10),
        });

        const eventSource = new lambdaEventSources.SqsEventSource(this.sqsQueue);

        this.lambdaFunction.addEventSource(eventSource);
    }
}