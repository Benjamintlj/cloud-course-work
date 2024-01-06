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
    usersDynamodbTable?: DynamoDB.Table;
    tripsDynamodbTable?: DynamoDB.Table;
}

export class genericLambdaStack extends cdk.Stack {

    readonly lambdaFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        // create lambda
        this.lambdaFunction = new lambda.Function(this, props.name, {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'src.index.main',
            code: lambda.Code.fromBucket(props.s3Bucket, props.s3Key),
            timeout: cdk.Duration.seconds(10),
            architecture: lambda.Architecture.ARM_64,
            environment: {
                'USERS_DYNAMODB_TABLE': props.usersDynamodbTable ? props.usersDynamodbTable.tableName : '',
                'TRIPS_DYNAMODB_TABLE': props.tripsDynamodbTable ? props.tripsDynamodbTable.tableName : '',
            }
        });

        // grant lambda read/write access to dynamodb
        if (props.usersDynamodbTable) {
            props.usersDynamodbTable.grantReadWriteData(this.lambdaFunction);
        }

        if (props.tripsDynamodbTable) {
            props.tripsDynamodbTable.grantReadWriteData(this.lambdaFunction);
        }
    }
}