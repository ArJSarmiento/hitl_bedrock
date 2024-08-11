import os
from aws_cdk import App, Environment
from bedrock_hitl.main import MyStack

# for development, use account/region from cdk cli
dev_env = Environment(
  account=os.getenv('CDK_DEFAULT_ACCOUNT'),
  region=os.getenv('CDK_DEFAULT_REGION')
)

app = App()
MyStack(app, "bedrock_hitl-dev", env=dev_env)
# MyStack(app, "bedrock_hitl-prod", env=prod_env)

app.synth()