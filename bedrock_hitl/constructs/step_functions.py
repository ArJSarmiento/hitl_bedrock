import json
from aws_cdk import aws_stepfunctions as sfn, aws_lambda, aws_iam
from constructs import Construct


class StepFunctions(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        lamdba_convert_response_to_schema: aws_lambda.Function = kwargs.pop('convert_response_to_schema', None)
        send_notification_for_human_review: aws_lambda.Function = kwargs.pop('send_notification_for_human_review', None)
        step_function_role: aws_iam.Role = kwargs.pop('step_function_role', None)

        # Call the base class constructor
        super().__init__(scope, construct_id, **kwargs)

        # Read the ASL JSON file
        asl_file_config = './bedrock_hitl/asl.json'
        with open(asl_file_config, 'r') as file:
            step_function_definition = json.load(file)

        # Replace the placeholder with the actual Lambda ARN
        step_function_definition['States']['Convert Result to Schema']['Resource'] = (
            lamdba_convert_response_to_schema.function_arn
        )
        step_function_definition['States']['Wait for Human Response']['Parameters']['FunctionName'] = (
            send_notification_for_human_review.function_arn
        )

        # Create the Step Function with the modified definition
        state_machine = sfn.CfnStateMachine(
            self,
            'HITLBedrockStateMachine',
            role_arn=step_function_role.role_arn,
            definition_string=json.dumps(step_function_definition),
        )

        self.state_machine_arn = state_machine.state_machine_name
