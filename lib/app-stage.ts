import {Construct} from "constructs";
import * as cdk from "aws-cdk-lib";
import {EcsStack} from "./ecs-stack";


export class AppStage extends cdk.Stage {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const ecsStack = new EcsStack(this, 'CloudCourseWorkEcsStack', {});
    }
}