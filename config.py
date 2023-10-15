REGION_NAME = "ap-northeast-2"

VPC_NAME = "elkvpc"
VPC_CIDR = "172.40.0.0/16"
INGRESS_PORTS = "22,80"

SUBNET_NAME = "pub-a"
CIDR_SUBSTITUTE = "11"
ROUTE_TABLE_NAME = "rt-pub"

KEY_NAME = "awselk"
INSTANCE_NAME = "elk-server"
INSTANCE_TYPE = "t2.medium"
INSTANCE_AMI = "ami-04341a215040f91bb"  # ami of x86 ubuntu image
