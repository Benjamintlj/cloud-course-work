import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as S3 from "aws-cdk-lib/aws-s3";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";

export class StorageStack extends cdk.Stack {

    readonly usersDynamoDbTable: DynamoDB.Table;
    readonly tripsDynamoDbTable: DynamoDB.Table;
    readonly tokensDynamoDbTable: DynamoDB.Table;
    readonly failedRequestDynamoDbTable: DynamoDB.Table;
    readonly lambdaBucket: S3.IBucket;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        this.lambdaBucket = S3.Bucket.fromBucketArn(
            this, 
            'cloudCourseWorkLambdaBucket', 
            'arn:aws:s3:::prod-cloudcourseworkstor-cloudcourseworklambdabuc-p2uc3m8jxde9'
        );

        // Create a Users DynamoDB table
        this.usersDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkUsersDynamoDbTable', {
            partitionKey: {
                name: 'user_id',
                type: DynamoDB.AttributeType.NUMBER
            },
        });

        // Secondary index for email
        this.usersDynamoDbTable.addGlobalSecondaryIndex({
            indexName: 'email-index',
            partitionKey: {
                name: 'email',
                type: DynamoDB.AttributeType.STRING
            }
        });

        // Create a Trips DynamoDB table
        this.tripsDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkTripsDynamoDbTable', {
            partitionKey: {
                name: 'trip_id',
                type: DynamoDB.AttributeType.NUMBER
            }
        });

        // Secondary index for admin_id
        this.tripsDynamoDbTable.addGlobalSecondaryIndex({
            indexName: 'admin_id-index',
            partitionKey: {
                name: 'admin_id',
                type: DynamoDB.AttributeType.NUMBER
            }
        });

        // Secondary index for location
        this.tripsDynamoDbTable.addGlobalSecondaryIndex({
            indexName: 'location-index',
            partitionKey: {
                name: 'location',
                type: DynamoDB.AttributeType.STRING
            }
        });

        // Create a Tokens DynamoDB table
        this.tokensDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkTokensDynamoDbTable', {
            partitionKey: {
                name: 'user_id',
                type: DynamoDB.AttributeType.NUMBER
            }
        });

        this.failedRequestDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkFailedRequestsDynamoDbTable', {
            partitionKey: {
                name: 'request_id',
                type: DynamoDB.AttributeType.NUMBER
            }
        });
    }
}