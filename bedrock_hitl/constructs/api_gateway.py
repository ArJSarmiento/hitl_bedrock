from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigateway, aws_iam as iam, aws_stepfunctions
from constructs import Construct


class HumanReviewAPI(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        step_function: aws_stepfunctions.StateMachine = kwargs.pop('step_function', None)

        super().__init__(scope, construct_id, **kwargs)

        # Create the Lambda function
        lambda_function = _lambda.Function(
            self,
            'HumanReviewLambda',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='lambda_function.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={'STEP_FUNCTION_ARN': step_function.state_machine_arn},
        )

        # Grant the Lambda function permission to call Step Functions
        lambda_function.add_to_role_policy(iam.PolicyStatement(actions=['states:SendTaskSuccess'], resources=['*']))

        # Create an API Gateway REST API resource backed by the Lambda function
        api = apigateway.LambdaRestApi(self, 'HumanReviewLambda', handler=lambda_function, proxy=False)

        # Define a resource and method for the API Gateway
        api_resource = api.root.add_resource('review')
        api_resource.add_method('POST')  # POST /review
