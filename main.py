import boto3
import pathlib
import config
import preprocess
import logging
import aws.ec2 as ec2_commands
import aws.vpc as vpc_commands
import typer

app = typer.Typer()
formatter = logging.Formatter(
    fmt="%(asctime)s (%(funcName)s) : %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
stream_handler = logging.StreamHandler(pathlib.os.sys.stdout)
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
local_dir = pathlib.Path(pathlib.os.getcwd())


@app.command("create")
def create_workspace_environment(profile_name: str = typer.Argument(...)):
    session = boto3.Session(
        profile_name=profile_name, 
        region_name=config.REGION_NAME,
    )
    ec2_client = session.client("ec2")

    logger.info("Create VPC")
    vpc_commands.create_vpc(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        vpc_cidr=config.VPC_CIDR,
    )
    vpc_commands.create_vpc_security_group(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        ingress_ports=config.INGRESS_PORTS.split(","),
    )
    vpc_commands.create_vpc_internet_gateway(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
    )

    logger.info("Define subnet within created VPC")
    vpc_commands.create_subnet(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        cidr_substitute=config.CIDR_SUBSTITUTE,
        region_name=config.REGION_NAME,
        az_postfix=config.SUBNET_NAME.split("-")[1],
        is_public=True,
    )
    vpc_commands.create_route_table(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        rt_name=config.ROUTE_TABLE_NAME,
        is_public=True,
    )
    vpc_commands.create_route_table_subnet_association(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        rt_name=config.ROUTE_TABLE_NAME,
    )

    logger.info("Create EC2 instance")
    ec2_commands.create_key_pair(
        ec2_client=ec2_client,
        key_name=config.KEY_NAME,
        local_dir=local_dir,
    )
    ec2_commands.run_instance(
        ec2_client=ec2_client,
        image_id=config.INSTANCE_AMI,
        instance_type=config.INSTANCE_TYPE,
        key_name=config.KEY_NAME,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        instance_name=config.INSTANCE_NAME,
    )
    ec2_commands.describe_instance(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        instance_name=config.INSTANCE_NAME,
    )


@app.command("instance")
def manage_instance(action_type: str = typer.Argument(...), profile_name: str = typer.Argument(...)):
    session = boto3.Session(
        profile_name=profile_name, 
        region_name=config.REGION_NAME,
    )
    ec2_client = session.client("ec2")

    if action_type.lower() == "start":
        ec2_commands.start_instance(
            ec2_client=ec2_client,
            vpc_name=config.VPC_NAME,
            subnet_name=config.SUBNET_NAME,
            instance_name=config.INSTANCE_NAME,
        )
    elif action_type.lower() == "stop":
        ec2_commands.stop_instance(
            ec2_client=ec2_client,
            vpc_name=config.VPC_NAME,
            subnet_name=config.SUBNET_NAME,
            instance_name=config.INSTANCE_NAME,
        )
    elif action_type.lower() == "reboot":
        ec2_commands.reboot_instance(
            ec2_client=ec2_client,
            vpc_name=config.VPC_NAME,
            subnet_name=config.SUBNET_NAME,
            instance_name=config.INSTANCE_NAME,
        )
    elif action_type.lower() == "describe":
        ec2_commands.describe_instance(
            ec2_client=ec2_client,
            vpc_name=config.VPC_NAME,
            subnet_name=config.SUBNET_NAME,
            instance_name=config.INSTANCE_NAME,
        )
    else:
        raise ValueError(
            f"action_type must be one of ('start', 'stop', 'reboot', 'describe'); got: '{action_type}'"
        )


@app.command("delete")
def delete_workspace_environment(profile_name: str = typer.Argument(...)):
    session = boto3.Session(
        profile_name=profile_name, 
        region_name=config.REGION_NAME,
    )
    ec2_client = session.client("ec2")

    logger.info("Terminate EC2 instance and delete corresponding key pair")
    ec2_commands.terminate_instance(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        instance_name=config.INSTANCE_NAME,
    )
    ec2_commands.delete_key_pair(
        ec2_client=ec2_client,
        key_name=config.KEY_NAME,
        local_dir=local_dir,
    )

    logger.info("Delete resources of subnet where terminated instance was created")
    vpc_commands.delete_route_table_subnet_association(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
        rt_name=config.ROUTE_TABLE_NAME,
    )
    vpc_commands.delete_route_table(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        rt_name=config.ROUTE_TABLE_NAME,
    )
    vpc_commands.delete_subnet(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
        subnet_name=config.SUBNET_NAME,
    )

    logger.info("Delete resources of VPC where deleted subnet was created")
    vpc_commands.delete_vpc_security_group(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
    )
    vpc_commands.delete_vpc_internet_gateway(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
    )
    vpc_commands.delete_vpc(
        ec2_client=ec2_client,
        vpc_name=config.VPC_NAME,
    )


@app.command("preprocess")
def prepare_example_data():
    logger.info("Download iris data from source")
    preprocess.download_data()

    logger.info("Transform data into Elasticsearch compatible format")
    preprocess.preprocess_data()


if __name__ == "__main__":
    app()
