import * as cdk from 'aws-cdk-lib';
import {Construct} from "constructs";
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as DynamoDB from "aws-cdk-lib/aws-dynamodb";
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2'; // Import ELBv2 for Application Load Balancer
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from "aws-cdk-lib/aws-sqs";


interface EcsStackProps extends cdk.StackProps {
    vpc: ec2.Vpc;
    environmentVariables: { [key: string]: string };
    lambda_resources: lambda.Function[];
    tokenDynamoDbTable: DynamoDB.Table;
    failedRequestsSQSQueue: sqs.Queue;
}

export class EcsStack extends cdk.Stack {

    constructor(scope: Construct, id: string, props: EcsStackProps) {
        super(scope, id, props);

        // Create an ECS cluster
        const cluster = new ecs.Cluster(this, 'cloudCourseCluster', {
            vpc: props.vpc,
        });

        // Add capacity to it
        cluster.addCapacity('cloudCourseAutoScalingGroupCapacity', {
            instanceType: new ec2.InstanceType("t4g.micro"),
            machineImage: ecs.EcsOptimizedImage.amazonLinux2(ecs.AmiHardwareType.ARM),
            desiredCapacity: 1,
            minCapacity: 1,
            maxCapacity: 2,
        });

        const repository = ecr.Repository.fromRepositoryName(this, 'MyRepository', 'cloud-course-work-ecs-repo');

        // Create a task definition and expose port 80
        const taskDefinition = new ecs.Ec2TaskDefinition(this, 'cloudCourseTaskDef');

        // Add IAM permissions
        taskDefinition.taskRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('SecretsManagerReadWrite'));

        // Create environment variables from props
        const environmentVariables: Record<string, string> = {};
        for (const [key, url] of Object.entries(props.environmentVariables)) {
            environmentVariables[key] = url;
        }

        // Add container to task definition
        const container = taskDefinition.addContainer('cloudCourseContainer', {
            image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
            memoryLimitMiB: 256,
            environment: environmentVariables,
        });

        container.addPortMappings({
            containerPort: 80,
            hostPort: 0,
            protocol: ecs.Protocol.TCP
        });

        // Instantiate an Amazon ECS Service
        const ECSService = new ecs.Ec2Service(this, 'cloudCourseService', { cluster, taskDefinition });

        // Add a load balancer and expose the service on port 80
        const loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'cloudCourseLoadBalancer', {
            vpc: props.vpc,
            internetFacing: true
        });
        const listener = loadBalancer.addListener('Listener', {port: 80});
        const TargetGroup = listener.addTargets('cloudCourseECSServiceTargetGroup', {
            port: 80,
            targets: [ECSService.loadBalancerTarget({
                containerName: 'cloudCourseContainer',
                containerPort: 80
            })]
        });

        // Grant permissions
        for (const lambda_function of props.lambda_resources) {
            lambda_function.grantInvoke(taskDefinition.taskRole);
        }

        props.tokenDynamoDbTable.grantReadWriteData(taskDefinition.taskRole);

        // Grant write permissions to SQS
        props.failedRequestsSQSQueue.grantSendMessages(taskDefinition.taskRole);
    }
}
