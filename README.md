# aws-elk-demo

From Logstach to Kibana via Elasticsearch on Ubuntu 20.04

1. [AWS EC2 Setup](#aws-ec2-setup)
1. [ELK Installation on Ubuntu Instance](#elk-installation-on-ec2-instance)
1. [Elasticsearch CRUD](#elasticsearch-crud)

## AWS EC2 Setup

Every logic to initiate EC2 instance is implemented using boto3 API. This means that you will need Python virtual environment to follow this demo. 

```
python3 --version  # Python 3.9.6
python3 -m venv venv
pip install -r requirements.txt
source venv/bin/activate
```

Then, execute following command to create every resource to initiate EC2 instance. Note that your own administrator profile (or IAM user profile with appropriate roles) has to be prepared prior to this demo(ex. `admin.kim`). For more details on the codes executed on this command, refer to [this link](https://github.com/sunsikim/aws-ec2-workspace-setup).

```
python main.py create admin.kim
```

To fetch launch command of public URL of instance that has been just created, execute following command with your own profile name(like `admin.kim`). This works because initial state of the instance will be *'running'*.

```
python main.py instance describe admin.kim
```

To stop the instance to prevent unnecessary cost charge or restart the stopped instance, type in following command with your own profile name.

```
python main.py instance [stop|start] admin.kim
```

To delete every resource created during this demo, execute following command. As always, `admin.kim` stands for your own profile name.

```
python main.py delete admin.kim
```

## ELK Installation on EC2 Instance

After instance being launched, whole tutorial starts from making sure that JDK is installed in the instance.

```
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk
java -version  # check if JDK is installed successfully
```

This demo will use 7.2.0 version of ELK services. Thus, downloading version specific deb binary file would be simplest installation solution. That being said, type in following commands:

```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.2.0-amd64.deb
wget https://artifacts.elastic.co/downloads/logstash/logstash-7.2.0.deb
wget https://artifacts.elastic.co/downloads/kibana/kibana-7.2.0-amd64.deb
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.2.0-amd64.deb
```

Next, install each service from installed deb packages

```
sudo dpkg -i elasticsearch-7.2.0-amd64.deb
sudo dpkg -i logstash-7.2.0.deb
sudo dpkg -i kibana-7.2.0-amd64.deb
sudo dpkg -i filebeat-7.2.0-amd64.deb
```

To check if Elasticsearch is properly installed, start the service and check out its status using following commands:

```
sudo service elasticsearch start
sudo service elasticsearch status
```

You should see something like this:

```
elasticsearch.service - Elasticsearch
    Loaded: loaded (/lib/systemd/system/elasticsearch.service; disabled; vendor preset: enabled)
    Active: active (running) since Thu 2023-10-19 14:08:47 UTC; 1s ago
    Docs: http://www.elastic.co
Main PID: 6023 (java)
    Tasks: 2 (limit: 4686)
    Memory: 921.7M
    ...
```

## Elasticsearch CRUD

Since Python3 and git are pre-installed in Ubuntu 20.04, just clone the current repository into the instance to have codes to download example dataset to work with from [this link](https://archive.ics.uci.edu/dataset/53/iris).

```
sudo apt install -y python3-pip
sudo apt install -y python3-venv
git clone https://github.com/sunsikim/aws-elk-demo.git
cd aws-elk-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Execute logics implemented in `preprocess.py` by using following command

```
python main.py preprocess
```

## Create index and insert data

In short, there are three steps to follow.

1. Create **type** within **index**.
1. Define **mapping** of created **type**.
1. Insert data using POST request with `bulk` option.

```
curl -XPUT localhost:9200/datasets?pretty
curl -XPOST localhost:9200/datasets/iris/_bulk?pretty \
    -H 'Content-Type: application/json' \
    --data-binary @data/iris_data.json
curl -XGET localhost:9200/datasets/iris/0?pretty  # check if data is inserted properly

```