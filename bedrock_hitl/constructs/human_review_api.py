from constructs import Construct
from aws_cdk import aws_iam as iam, aws_lambda as _lambda, aws_apigateway as apigateway, aws_stepfunctions as sfn
from aws_solutions_constructs.aws_apigateway_lambda import ApiGatewayToLambda


class HumanReviewAPI(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        step_function: sfn.StateMachine = kwargs.pop('step_function', None)

        # Call the base class constructor
        super().__init__(scope, construct_id, **kwargs)

        review_lambda = _lambda.Function(
            self,
            'ReviewLambda',
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset('bedrock_hitl/functions'),
            handler='human_review.handler',
            environment={'STATE_MACHINE_ARN': step_function.state_machine_arn},
        )

        review_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=['states:SendTaskSuccess', 'states:SendTaskFailure', 'states:SendTaskHeartbeat'],
                resources=[step_function.state_machine_arn],
            )
        )

        # Use the L3 construct to create API Gateway and integrate with Lambda
        api_gateway_lambda = ApiGatewayToLambda(
            self,
            'ReviewApiGatewayLambda',
            existing_lambda_obj=review_lambda,
            api_gateway_props={'restApiName': 'ReviewApi', 'description': 'This service handles reviews.'},
        )

        # Add the POST /review endpoint
        review_resource = api_gateway_lambda.api_gateway.root.add_resource('review')
        review_resource.add_method('POST', authorization_type=apigateway.AuthorizationType.NONE)
