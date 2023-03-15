"""Code for generation and deploy lambda to AWS"""
import json
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
from aws_cdk import Stack, Duration


class LambdaConstruct:
    """Class with static methods that are used to build and deploy lambdas."""

    #pylint: disable=too-many-arguments
    @staticmethod
    def create_lambda(
            stack: Stack,
            config: dict,
            lambda_name: str,
            role: iam.Role,
            memory_size: int = None,
            duration: Duration = None) -> aws_lambda.Function:
        """Method called by construct for creating lambda."""

        env_vars = json.loads(config['global'][f"{lambda_name}Environment"])
        if not duration:
            duration = Duration.minutes(amount=10)

        return LambdaConstruct.create_lambda_function(
            stack=stack,
            config=config,
            lambda_name=lambda_name,
            role=role,
            env_vars=env_vars,
            memory_size=memory_size,
            duration=duration
        )

    @staticmethod
    def create_lambda_function(
            stack: Stack,
            config: dict,
            lambda_name: str,
            role: iam.Role,
            env_vars: dict,
            duration: Duration,
            memory_size: int = None) -> aws_lambda.Function:
        """Methods for generic lambda creation."""

        lambda_path = config['global'][f"{lambda_name}HndlrPath"]
        handler = config['global'][f"{lambda_name}Hndlr"]
        function_id = f"{config['global']['app-name']}-{lambda_name}-Id"
        function_name = f"{config['global']['app-name']}-{lambda_name}"

        dict_props = {
            "function_name": function_name,
            "code": aws_lambda.Code.from_asset(path=lambda_path),
            "handler": handler,
            "runtime": aws_lambda.Runtime.PYTHON_3_8,
            "role": role,
            "environment": env_vars,
            "timeout": duration,
            "memory_size": memory_size, 
            "architecture": aws_lambda.Architecture.X86_64
        }

        return aws_lambda.Function(scope=stack, id=function_id, **dict_props)

    @staticmethod
    def get_sfn_execute_policy(step_function_arn: str) -> iam.PolicyStatement:
        """Returns policy statements for executing step function."""
        policy_statement = iam.PolicyStatement()
        policy_statement.effect = iam.Effect.ALLOW
        policy_statement.add_actions("states:StartExecution")
        policy_statement.add_resources(step_function_arn)
        return policy_statement

    @staticmethod
    def get_cloudwatch_policy(lambda_logs_arn: str) -> iam.PolicyStatement:
        """Returns policy statement for creating logs."""
        policy_statement = iam.PolicyStatement()
        policy_statement.effect = iam.Effect.ALLOW
        policy_statement.add_actions("cloudwatch:PutMetricData")
        policy_statement.add_actions("logs:CreateLogGroup")
        policy_statement.add_actions("logs:CreateLogStream")
        policy_statement.add_actions("logs:GetQueryResults")
        policy_statement.add_actions("logs:PutLogEvents")
        policy_statement.add_actions("logs:StartQuery")
        policy_statement.add_resources(lambda_logs_arn)
        return policy_statement