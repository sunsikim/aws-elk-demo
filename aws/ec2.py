import pathlib
import time
from aws.vpc import fetch_vpc_security_group_id, fetch_subnet_id


def create_key_pair(
        ec2_client,
        key_name: str,
        local_dir: pathlib.Path,
):
    """
    Create key pair to access remote EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param key_name: name of key pair
    :param local_dir: path to directory to save key pair file
    :return: None
    """
    key_info = ec2_client.create_key_pair(
        KeyName=key_name,
        DryRun=False,
        KeyType="rsa",
        KeyFormat="pem",
    )
    key_path = local_dir.joinpath(f"{key_name}.pem")
    with open(key_path, "w") as file:
        file.write(key_info["KeyMaterial"])
    key_path.chmod(0o400)  # python equivalent to 'chmod 400 key_path'


def describe_instance(
        ec2_client,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Print current status of the created instance
    :param ec2_client: EC2 client created by boto3 session
    :param subnet_name: name of subnet where instance is created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to stop
    :return: None
    """
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "subnet-id",
                    "Values": [fetch_subnet_id(ec2_client, vpc_name, subnet_name)]
                },
                {
                    "Name": "tag:Name",
                    "Values": [instance_name]
                }
            ]
        )
        instance_info = response["Reservations"][0]["Instances"][0]
        state = instance_info["State"]["Name"]
        print(f"CURRENT STATE  : {state}")
        if state == "running":
            print(f'LAUNCH COMMAND : ssh -i "awselk.pem" ubuntu@{instance_info["PublicDnsName"]}')
    except Exception:
        print("Instance has not been created yet")


def run_instance(
        ec2_client,
        image_id: str,
        instance_type: str,
        key_name: str,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Launch instance and wait until it gets ready
    :param ec2_client: EC2 client created by boto3 session
    :param image_id: AMI ID which can be found in AMI catalog menu in EC2 console
    :param instance_type: identifier of instance type listed in Instance Types menu in EC2 console
    :param key_name: name of key pair
    :param subnet_name: name of subnet where instance will be created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to be created
    :return: None
    """
    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[
            fetch_vpc_security_group_id(ec2_client, vpc_name),
        ],
        SubnetId=fetch_subnet_id(ec2_client, vpc_name, subnet_name),
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": instance_name}]
            }
        ]
    )
    instance_id = response["Instances"][0]["InstanceId"]
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"


def stop_instance(
        ec2_client,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Stop EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param subnet_name: name of subnet where instance is created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to stop
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [instance_name]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client, vpc_name, subnet_name)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.stop_instances(InstanceIds=[instance_id])
    is_stopped = False
    while not is_stopped:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_stopped = instance_info["State"]["Name"] == "stopped"


def start_instance(
        ec2_client,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Start stopped EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param subnet_name: name of subnet where instance is created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to stop
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [instance_name]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client, vpc_name, subnet_name)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.start_instances(InstanceIds=[instance_id])
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"
        


def reboot_instance(
        ec2_client,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Reboot EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param subnet_name: name of subnet where instance is created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to stop
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [instance_name]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client, vpc_name, subnet_name)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.reboot_instances(InstanceIds=[instance_info["InstanceId"]])
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"


def terminate_instance(
        ec2_client,
        vpc_name: str,
        subnet_name: str,
        instance_name: str,
):
    """
    Associate elastic IP with EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param subnet_name: name of subnet where instance is created
    :param vpc_name: name of VPC where the subnet belongs to
    :param instance_name: name of instance to terminate
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [instance_name]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client, vpc_name, subnet_name)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    is_terminated = False
    while not is_terminated:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_terminated = instance_info["State"]["Name"] == "terminated"


def delete_key_pair(
        ec2_client,
        key_name: str,
        local_dir: pathlib.Path,
):
    """
    Delete created key pair
    :param ec2_client: EC2 client created by boto3 session
    :param key_name: name of key pair
    :param local_dir: path to directory where key pair file was saved
    :return: None
    """
    pathlib.os.remove(local_dir.joinpath(f"{key_name}.pem"))
    ec2_client.delete_key_pair(KeyName=key_name)
