"""Main python file_key for adding resources to the application stack."""
from typing import Dict, Any
import aws_cdk
from constructs import Construct
import aws_cdk.aws_kms as kms
import aws_cdk.aws_sns as sns
import aws_cdk.aws_lambda as _lambda

from .iam_construct import IAMConstruct
from .kms_construct import KMSConstruct
from .sns_construct import SNSConstruct
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

        # KMS infra setup ------------------------------------------------------
        kms_pol_doc = IAMConstruct.get_kms_policy_document()

        kms_key = KMSConstruct.create_kms_key(
            stack=stack,
            config=config,
            policy_doc=kms_pol_doc
        )
        print(kms_key)

        # SNS Infra Setup -----------------------------------------------------
        sns_topic = MainProjectStack.setup_sns_topic(
            config,
            kms_key,
            stack
        )

        # IAM Role Setup --------------------------------------------------------
        stack_role = MainProjectStack.create_stack_role(
            config=config,
            stack=stack,
            kms_key=kms_key,
            sns_topic=sns_topic,
            source_buckt_arn=config['global']['bucket_name'],
            source_bucket_kms_arn=config['global']['src_kms_arn']
        )
        print(stack_role)

        # Lambda Layers --------------------------------------------------------
        layer = MainProjectStack.create_layers_for_lambdas(
            stack=stack,
            config=config
        )

        # Infra for Lambda function creation -------------------------------------
        lambdas = MainProjectStack.create_lambda_functions(
            stack=stack,
            config=config,
            kms_key=kms_key,
            layers=layer,
            sns_topic=sns_topic
        )
        print(lambdas)

    @staticmethod
    def setup_sns_topic(
            config: dict,
            kms_key: kms.Key,
            stack: aws_cdk.Stack) -> sns.Topic:
        """Set up the SNS Topic and returns the SNS Topic Object."""
        sns_topic = SNSConstruct.create_sns_topic(
            stack=stack,
            config=config,
            kms_key=kms_key
        )
        SNSConstruct.subscribe_email(config=config, topic=sns_topic)
        return sns_topic

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

    # @staticmethod
    # def create_lambda_functions(
    #         stack: aws_cdk.Stack,
    #         config: dict,
    #         kms_key: kms.Key,
    #         sns_topic: sns.Topic,
    #         layers: Dict[str, _lambda.LayerVersion] = None) -> Dict[str, _lambda.Function]:
    #     """Create placeholder lambda function and roles."""