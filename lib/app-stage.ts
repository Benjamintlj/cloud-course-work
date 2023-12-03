import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {EcsStack} from "./ecs-stack";
import {VpcStack} from "./vpc-stack";
import {genericLambdaStack} from "./generic-lambda-stack";


export class AppStage extends cdk.Stage {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // create vpc
        const vpcStack = new VpcStack(this, 'CloudCourseWorkVpcStack', {})

        // create ecs, load balancer, and auto-scaling cluster
        const ecsStack = new EcsStack(this, 'CloudCourseWorkEcsStack', {
            vpc: vpcStack.vpc,
        });

        // create lambdas
        const tripMgrStack = new genericLambdaStack(this, 'tripMgrStack', {
            name: 'tripMgr',
            assetPath: 'src/tripMgr/out/tripMgr.zip',
        });
    }
}