import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import {IBucket} from "aws-cdk-lib/aws-s3";

interface LambdaStackProps extends cdk.StackProps {
    name: string;
    s3Bucket: IBucket;
    s3Key: string;
}

export class genericLambdaStack extends cdk.Stack {

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        const fn = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'src/index.main',
            code: lambda.Code.fromBucket(props.s3Bucket, props.s3Key),
            timeout: cdk.Duration.seconds(10),
        });
    }
}