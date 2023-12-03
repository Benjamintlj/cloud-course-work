import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {EcsStack} from "./ecs-stack";
import {VpcStack} from "./vpc-stack";
import {genericLambdaStack} from "./generic-lambda-stack";
import {StorageStack} from "./storage-stack";


export class AppStage extends cdk.Stage {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // create vpc
        const vpcStack = new VpcStack(this, 'CloudCourseWorkVpcStack', {})

        // create ecs, load balancer, and auto-scaling cluster
        const ecsStack = new EcsStack(this, 'CloudCourseWorkEcsStack', {
            vpc: vpcStack.vpc,
        });

        // create s3 bucket
        const storageStack = new StorageStack(this, 'CloudCourseWorkStorageStack', {});

        // create lambdas
        const tripMgrStack = new genericLambdaStack(this, 'CloudCourseWorkTripMgrStack', {
            name: 'tripMgr',
            s3Bucket: storageStack.lambdaBucket,
            s3Key: 'tripMgr.zip',
        });
    }
}