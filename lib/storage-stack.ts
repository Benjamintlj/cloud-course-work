import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as S3 from "aws-cdk-lib/aws-s3";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";

export class StorageStack extends cdk.Stack {

    readonly lambdaBucket: S3.Bucket;
    readonly masterDynamoDbTable: DynamoDB.Table;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // TODO: set this to the existing S3 bucket
        this.lambdaBucket = new S3.Bucket(this, 'cloudCourseWorkLambdaBucket', {
            versioned: false,
            removalPolicy: cdk.RemovalPolicy.RETAIN
        });

        this.masterDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkMasterDynamoDbTable', {
            partitionKey: {
                name: 'pk',
                type: DynamoDB.AttributeType.STRING
            },
            sortKey: {
                name: 'sk',
                type: DynamoDB.AttributeType.NUMBER
            }
        });
    }
}