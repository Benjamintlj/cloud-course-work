import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {Bucket} from "aws-cdk-lib/aws-s3";

export class EcsStack extends cdk.Stack {

    public readonly bucket: Bucket;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // create a s3
        this.bucket = new Bucket(this, 'TestBucket123', {
            versioned: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            bucketName: 'test-bucket-123'
        });
    }
}
