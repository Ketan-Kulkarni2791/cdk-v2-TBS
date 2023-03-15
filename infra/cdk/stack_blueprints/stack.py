"""Main python file_key for adding resources to the application stack."""
from typing import Dict, Any
import aws_cdk
import aws_cdk.aws_lambda as _lambda
from constructs import Construct

from .iam_construct import IAMConstruct
from .lambda_construct import LambdaConstruct
from .lambda_layer_construct import LambdaLayerConstruct


class MainProjectStack(aws_cdk.Stack):
    """Build the app stacks and its resources."""
    def __init__(self, env_var: str, scope: Construct, 
                 app_id: str, config: dict, **kwargs: Dict[str, Any]) -> None:
        """Creates the cloudformation templates for the projects."""
        super().__init__(scope, app_id, **kwargs)
        self.env_var = env_var
        self.config = config
        MainProjectStack.create_stack(self, self.env_var, config=config)

    @staticmethod
    def create_stack(stack: aws_cdk.Stack, env: str, config: dict) -> None:
        """Create and add the resources to the application stack"""

        print(env)
        # Lambda Layers --------------------------------------------------------
        MainProjectStack.create_layers_for_lambdas(
            stack=stack,
            config=config
        )

        # Infra for Lambda function creation -------------------------------------
        lambdas = MainProjectStack.create_lambda_functions(
            stack=stack,
            config=config
        )
        print(lambdas)

    @staticmethod
    def create_layers_for_lambdas(
            stack: aws_cdk.Stack,
            config: dict) -> Dict[str, _lambda.LayerVersion]:
        """Method to create layers."""
        layers = {}
        # requirement layer for general ----------------------------------------------------
        layers["pandas"] = LambdaLayerConstruct.create_lambda_layer(
            stack=stack,
            config=config,
            layer_name="pandas_layer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8
            ]
        )
        layers["psycopg2"] = LambdaLayerConstruct.create_lambda_layer(
            stack=stack,
            config=config,
            layer_name="psycopg2_layer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8
            ]
        )
        return layers

    @staticmethod
    def create_lambda_functions(
            stack: aws_cdk.Stack,
            config: dict) -> Dict[str, _lambda.Function]:
        """Create placeholder lambda function and roles."""

        lambdas = {}

        trigger_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            config=config,
            policy_name="trigger_policy",
            statements=[
                LambdaConstruct.get_sfn_execute_policy(
                    config['global']['stepFunctionArn']  
                ),
                LambdaConstruct.get_cloudwatch_policy(
                    config['global']['trigger_lambdaLogsArn']
                )
            ]
        )

        trigger_role = IAMConstruct.create_role(
            stack=stack,
            config=config,
            role_name="trigger",
            assumed_by=["lambda"]   
        )

        trigger_role.add_managed_policy(trigger_policy)

        lambdas["trigger_lambda"] = LambdaConstruct.create_lambda(
            stack=stack,
            config=config,
            lambda_name="trigger_lambda",
            role=trigger_role,
            duration=aws_cdk.Duration.minutes(amount=15),
            memory_size=3008
        )

        return lambdas