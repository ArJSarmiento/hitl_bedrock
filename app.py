import os
from aws_cdk import App, Environment
from bedrock_hitl.main import ExpenseApprovalStack

# for development, use account/region from cdk cli
dev_env = Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region='us-east-1')

app = App()
ExpenseApprovalStack(app, 'bedrock-hitl-dev', env=dev_env)
# ExpenseApprovalStack(app, "bedrock_hitl-prod", env=prod_env)

app.synth()
