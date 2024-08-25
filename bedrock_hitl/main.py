from aws_cdk import Stack, aws_iam as iam, aws_lambda as _lambda, aws_apigateway as apigateway
from constructs import Construct
from bedrock_hitl.constructs.step_functions import StepFunctions
from bedrock_hitl.constructs.human_review_api import HumanReviewAPI
from aws_solutions_constructs.aws_apigateway_lambda import ApiGatewayToLambda


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
        convert_response_to_schema = _lambda.Function(
            self,
            'ConvertResponseToSchema',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='convert_response_to_schema.handler',
            code=_lambda.Code.from_asset('bedrock_hitl/functions'),
        )
        convert_response_to_schema.grant_invoke(iam.ServicePrincipal('states.amazonaws.com'))

        # Send Notification for Human Review
        send_notification_for_human_review = _lambda.Function(
            self,
            'SendHumanReview',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='send_notification_for_human_review.handler',
            code=_lambda.Code.from_asset('bedrock_hitl/functions'),
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
        HumanReviewAPI(self, 'HumanReviewAPI', step_function=step_function)
