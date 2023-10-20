REGION_NAME = "ap-northeast-2"

VPC_NAME = "elkvpc"
VPC_CIDR = "172.40.0.0/16"
INGRESS_PORTS = "22,80,443,5601"  # 443: HTTPS, 5601: Kibana

SUBNET_NAME = "pub-a"
CIDR_SUBSTITUTE = "11"
ROUTE_TABLE_NAME = "rt-pub"

KEY_NAME = "awselk"
INSTANCE_NAME = "elk-server"
INSTANCE_TYPE = "t2.medium"
INSTANCE_AMI = "ami-04341a215040f91bb"  # ami of x86 Ubuntu 20.04 image

DATA_URL = "https://archive.ics.uci.edu/static/public/53/iris.zip"
ARCHIVE_NAME = DATA_URL.split("/")[-1]