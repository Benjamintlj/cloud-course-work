import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import {IBucket} from "aws-cdk-lib/aws-s3";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";
import * as Sqs from "aws-cdk-lib/aws-sqs";

interface LambdaStackProps extends cdk.StackProps {
    name: string;
    s3Bucket: IBucket;
    s3Key: string;
    dynamoTable?: DynamoDB.Table;
}

export class genericLambdaStack extends cdk.Stack {

    readonly lambdaFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        // create sqs that the lambda can write to
        const sqsName = props.name + 'Dlq';

        const dlq = new Sqs.Queue(this, sqsName, {
            queueName: sqsName,
        });

        // create lambda
        this.lambdaFunction = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'src/index.main',
            code: lambda.Code.fromBucket(props.s3Bucket, props.s3Key),
            timeout: cdk.Duration.seconds(10),
            environment: {
                'DYNAMO_TABLE': props.dynamoTable ? props.dynamoTable.tableName : '',
                'DLQ_QUEUE_URL': dlq.queueUrl,
            }
        });

        // grant lambda send message access to sqs
        dlq.grantSendMessages(this.lambdaFunction);

        // grant lambda read/write access to dynamodb
        if (props.dynamoTable) {
            props.dynamoTable.grantReadWriteData(this.lambdaFunction);
        }
    }
}