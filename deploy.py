#!/usr/local/bin/python3

import boto3
import watchtower
import logging
import sys
import json

commandargs = '{"profile": "none", "cmd": "create", "vpcname": "WordPress", "uploadbucket": "deploymentbucket", "uploadpath": "/vpc/WordPress/"}'

if len(sys.argv) > 1:
    commandargs = sys.argv[1]

params = json.loads(commandargs)


profile = params.get("profile", "none")

if profile = "none":
    session = boto3.Session()
else:
    session = boto3.Session(profile_name=profile)

cmd = params.get("cmd", "create")
vpcname = params.get("vpcname", "none")
uploadbucket = params.get("uploadbucket", "none")
uploadpath = params.get("uploadpath", "none")

#####Don't worry about these parameters
region = session.region_name
vpcstackname = vpcname
subnetstackname = vpcname + "-Subnet-" + region
natgatewaystackname = vpcname + "-NatGateway-" + region
naclentrystackname = vpcname + "-NaclEntry-" + region
securitygroupstackname = vpcname + "-SecurityGroup-" + region
deploymentfolders3 = "s3://" + uploadbucket + uploadpath
deploymentfolderhttp = "https://s3.amazonaws.com/" + uploadbucket + uploadpath
######


cloudformation = session.client('cloudformation')
s3 = session.client('s3')



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('VPC-load-process-' + vpcname + '-'+str((today-datetime.datetime(1970,1,1)).total_seconds()))
logGroup = '/VPC-load-process-' + vpcname
logger.addHandler(watchtower.CloudWatchLogHandler(log_group=logGroup))


msg = 'Beginning Process'
print(msg)
logger.info(msg)

if cmd = "create" then:
    msg = 'Uploading Files'
    print(msg)
    logger.info(msg)
    s3.upload_file(Filename="./CreateVPC.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateVPC.json")
    s3.upload_file(Filename="./CreateSubnet-US-East-1.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateSubnet-US-East-1.json")
    s3.upload_file(Filename="./CreateNatGateway-US-East-1.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateNatGateway-US-East-1.json")
    s3.upload_file(Filename="./CreateAllNetworkACLEntry.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateAllNetworkACLEntry.json")
    s3.upload_file(Filename="./CreateAllSecurityGroup.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateAllSecurityGroup.json")
    s3.upload_file(Filename="./CreateAllNetworkACLEntryNoPublicSSH.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateAllNetworkACLEntryNoPublicSSH.json")
    s3.upload_file(Filename="./CreateAllSecurityGroupNoPublicSSH.json", Bucket=uploadbucketname, Key=uploadpathname + "CreateAllSecurityGroupNoPublicSSH.json")
    s3.upload_file(Filename="./deploy.sh", Bucket=uploadbucketname, Key=uploadpathname + "deploy.sh")
    s3.upload_file(Filename="./deploy.py", Bucket=uploadbucketname, Key=uploadpathname + "deploy.py")
    s3.upload_file(Filename="./deploy-parameters.json", Bucket=uploadbucketname, Key=uploadpathname + "deploy-parameters.json")
    msg = 'Done Uploading Files'
    print(msg)
    logger.info(msg)


    msg = "Deploying the stack " + vpcstackname
    print(msg)
    logger.info(msg)

    response = cloudformation.create_stack(StackName=vpcstackname, TemplateURL=deploymentfolderhttp, Parameters= [ { "ParameterKey": "VPCName", "ParameterValue": vpcname } ]

    aws cloudformation create-stack --stack-name $vpcstackname --template-url $deploymentfolderhttp/CreateVPC.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
    aws cloudformation wait stack-create-complete --stack-name $vpcstackname --region $region --profile $profile
    if test "$?" != "0"
    then
      echo "$vpcstackname Did Not Return in a Timely Manner"
      exit $?
    fi

    msg = vpcstackname + " Deployed Successfully"
    print(msg)
    logger.info(msg)
