from aws_cdk import Stack, aws_iam as iam, aws_lambda
from constructs import Construct
from bedrock_hitl.step_functions import StepFunctions


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
            code=aws_lambda.Code.from_asset('bedrock_hitl/convert_response_to_schema'),
        )
        convert_response_to_schema.grant_invoke(iam.ServicePrincipal('states.amazonaws.com'))

        # Step functions
        StepFunctions(
            self,
            'HITLStepFunctions',
            convert_response_to_schema=convert_response_to_schema,
            step_function_role=step_function_role,
        )
