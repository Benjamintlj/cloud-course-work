import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";

interface LambdaStackProps extends cdk.StackProps {
    name: string;
    assetPath: string;
}

export class genericLambdaStack extends cdk.Stack {

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        const fn = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'index.main',
            code: lambda.Code.fromAsset(props.assetPath),
            timeout: cdk.Duration.seconds(10),
        });
    }
}