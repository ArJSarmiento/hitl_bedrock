from projen.awscdk import AwsCdkPythonApp

project = AwsCdkPythonApp(
    author_email='rneljan@gmail.com',
    author_name='ArJSarmiento',
    cdk_version='2.1.0',
    module_name='bedrock_hitl',
    name='bedrock_hitl',
    poetry=True,
    version='0.1.0',
)

project.synth()
