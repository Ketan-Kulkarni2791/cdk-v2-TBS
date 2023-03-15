"""Module to hold helper methods for CDK IAM creation"""
from typing import List
from aws_cdk import Stack
import aws_cdk.aws_iam as iam


class IAMConstruct:
    """Class holds methods for IAM resource creation"""

    @staticmethod
    def create_role(stack: Stack, config: dict, role_name: str,
                    assumed_by: List[str]) -> iam.Role:
        """Create role utilized by lambda, glue, step function, or the stack itself."""
        services = list(map(lambda x: iam.ServicePrincipal(
            f"{x}.amazonaws.com"), assumed_by))
        return iam.Role(
            scope=stack,
            id=f"{config['global']['appNameShort']}-{role_name}-role-id",
            role_name=f"{config['global']['appNameShort']}{role_name}-role",
            assumed_by=iam.CompositePrincipal(*services)
        )

    @staticmethod
    def create_managed_policy(
            stack: Stack,
            config: dict,
            policy_name: str,
            statements: List[iam.PolicyStatement]) -> iam.ManagedPolicy:
        """Create managed policy for lambda roles with permissions for specific services."""
        return iam.ManagedPolicy(
            scope=stack,
            id=f"{config['global']['app-name']}-{policy_name}-policy-id",
            managed_policy_name=f"{config['global']['app-name']}-{policy_name}-policy",
            statements=statements
        )