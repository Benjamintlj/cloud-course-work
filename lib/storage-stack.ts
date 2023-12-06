import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as S3 from "aws-cdk-lib/aws-s3";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";

export class StorageStack extends cdk.Stack {

    readonly lambdaBucket: S3.Bucket;
    readonly usersDynamoDbTable: DynamoDB.Table;
    readonly tripsDynamoDbTable: DynamoDB.Table;
    readonly masterDynamoDbTable: DynamoDB.Table;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // TODO: set this to the existing S3 bucket
        this.lambdaBucket = new S3.Bucket(this, 'cloudCourseWorkLambdaBucket', {
            versioned: false,
            removalPolicy: cdk.RemovalPolicy.RETAIN
        });

        // Create a Users DynamoDB table
        this.usersDynamoDbTable = new DynamoDB.Table(this, 'cloudCourseWorkUsersDynamoDbTable', {
            partitionKey: {
                name: 'userId',
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
                name: 'tripId',
                type: DynamoDB.AttributeType.NUMBER
            },
            sortKey: {
                name: 'start_date',
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
    }
}