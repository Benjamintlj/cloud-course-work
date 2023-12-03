import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {EcsStack} from "./ecs-stack";
import {VpcStack} from "./vpc-stack";


export class AppStage extends cdk.Stage {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const vpcStack = new VpcStack(this, 'CloudCourseWorkVpcStack', {})
        const ecsStack = new EcsStack(this, 'CloudCourseWorkEcsStack', {
            vpc: vpcStack.vpc,
        });
    }
}