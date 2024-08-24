from aws_cdk import Stack, aws_iam as iam, aws_lambda, aws_apigateway as apigw
from constructs import Construct
from bedrock_hitl.constructs.step_functions import StepFunctions
from aws_solutions_constructs import aws_apigateway_lambda as apigw_lambda


class ExpenseApprovalStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        step_function_role = iam.Role(
            self,
            'StepFunctionRole',
            assumed_by=iam.ServicePrincipal('states.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaRole')],
        )

        # Attach additional policies directly to the role
        step_function_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    'bedrock:InvokeModel',  # Allows invoking Amazon Bedrock models
                    'events:PutEvents',  # Allows putting events in Amazon EventBridge
                    'xray:PutTraceSegments',  # Allows AWS X-Ray actions
                    'xray:PutTelemetryRecords',
                    'xray:GetSamplingRules',
                    'xray:GetSamplingTargets',
                ],
                resources=['*'],  # You can specify more granular resource ARNs
            )
        )

        # Convert Bedrock to JSON Schema Lambda
        convert_response_to_schema = aws_lambda.Function(
            self,
            'ConvertResponseToSchema',
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler='convert_response_to_schema.handler',
            code=aws_lambda.Code.from_asset('bedrock_hitl/functions'),
        )
        convert_response_to_schema.grant_invoke(iam.ServicePrincipal('states.amazonaws.com'))

        # Send Notification for Human Review
        send_notification_for_human_review = aws_lambda.Function(
            self,
            'SendHumanReview',
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler='send_notification_for_human_review.handler',
            code=aws_lambda.Code.from_asset('bedrock_hitl/functions'),
        )
        send_notification_for_human_review.grant_invoke(iam.ServicePrincipal('states.amazonaws.com'))

        # Step functions
        step_function = StepFunctions(
            self,
            'HITLStepFunctions',
            convert_response_to_schema=convert_response_to_schema,
            step_function_role=step_function_role,
            send_notification_for_human_review=send_notification_for_human_review,
        )

        # Human Review API
        apigw_lambda.ApiGatewayToLambda(
            self,
            'HumanReviewAPI',
            lambda_function_props=aws_lambda.FunctionProps(
                runtime=aws_lambda.Runtime.PYTHON_3_11,
                code=aws_lambda.Code.from_asset('bedrock_hitl/functions'),
                handler='human_review.handler',
                environment={'STEP_FUNCTION_ARN': step_function.state_machine_arn},
            ),
            api_gateway_props=apigw.RestApiProps(endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL])),
        )
