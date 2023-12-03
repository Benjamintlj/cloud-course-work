import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as S3 from "aws-cdk-lib/aws-s3";

export class StorageStack extends cdk.Stack {

    readonly lambdaBucket: S3.Bucket;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        this.lambdaBucket = new S3.Bucket(this, 'cloudCourseWorkLambdaBucket', {
            versioned: false,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });
    }
}