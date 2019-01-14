#!/usr/local/bin/python3

import boto3
import watchtower
import logging
import sys
import json
import datetime

today = datetime.datetime.now()

commandargs = '{"profile": "none", "cmd": "create", "vpcname": "WordPress", "uploadbucket": "deploymentbucket", "uploadpath": "vpc/WordPress/"}'

if len(sys.argv) > 1:
    commandargs = sys.argv[1]

params = json.loads(commandargs)


profile = params.get("profile", "none")

if profile == "none":
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
deploymentfolders3 = "s3://" + uploadbucket + "/" + uploadpath
deploymentfolderhttp = "https://s3.amazonaws.com/" + uploadbucket + "/" + uploadpath
######


cloudformation = session.client('cloudformation')
createwaiter = cloudformation.get_waiter('stack_create_complete')
deletewaiter = cloudformation.get_waiter('stack_delete_complete')
s3 = session.client('s3')



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('VPC-load-process-' + vpcname + '-'+str((today-datetime.datetime(1970,1,1)).total_seconds()))
logGroup = '/VPC-load-process/' + vpcname
logger.addHandler(watchtower.CloudWatchLogHandler(log_group=logGroup))


msg = 'Beginning Process'
print(msg)
logger.info(msg)

if cmd == "create":
    msg = 'Create process started'
    print(msg)
    logger.info(msg)


    try:
        msg = 'Uploading Files'
        print(msg)
        logger.info(msg)
        s3.upload_file(Filename="./CreateVPC.json", Bucket=uploadbucket, Key=uploadpath + "CreateVPC.json")
        s3.upload_file(Filename="./CreateSubnet-US-East-1.json", Bucket=uploadbucket, Key=uploadpath + "CreateSubnet-US-East-1.json")
        s3.upload_file(Filename="./CreateNatGateway-US-East-1.json", Bucket=uploadbucket, Key=uploadpath + "CreateNatGateway-US-East-1.json")
        s3.upload_file(Filename="./CreateAllNetworkACLEntry.json", Bucket=uploadbucket, Key=uploadpath + "CreateAllNetworkACLEntry.json")
        s3.upload_file(Filename="./CreateAllSecurityGroup.json", Bucket=uploadbucket, Key=uploadpath + "CreateAllSecurityGroup.json")
        s3.upload_file(Filename="./CreateAllNetworkACLEntryNoPublicSSH.json", Bucket=uploadbucket, Key=uploadpath + "CreateAllNetworkACLEntryNoPublicSSH.json")
        s3.upload_file(Filename="./CreateAllSecurityGroupNoPublicSSH.json", Bucket=uploadbucket, Key=uploadpath + "CreateAllSecurityGroupNoPublicSSH.json")
        s3.upload_file(Filename="./deploy.sh", Bucket=uploadbucket, Key=uploadpath + "deploy.sh")
        s3.upload_file(Filename="./deploy.py", Bucket=uploadbucket, Key=uploadpath + "deploy.py")
        s3.upload_file(Filename="./deploy-parameters.json", Bucket=uploadbucket, Key=uploadpath + "deploy-parameters.json")
        msg = 'Done Uploading Files'
        print(msg)
        logger.info(msg)


        msg = "Deploying the stack " + vpcstackname
        print(msg)
        logger.info(msg)

        response = cloudformation.create_stack(StackName=vpcstackname, TemplateURL=deploymentfolderhttp + "CreateVPC.json", Parameters= [ { "ParameterKey": "VPCName", "ParameterValue": vpcname } ] )

        vpcstackid = response["StackId"]

        createwaiter.wait(StackName=vpcstackname,
        WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 120
        })

        msg = vpcstackname + " Deployed Successfully with StackId: " + vpcstackid
        print(msg)
        logger.info(msg)
    except:
        msg = "Something bad just happened."
        print(msg)
        logger.info(msg)
    msg = "Create process finished"
    print(msg)
    logger.info(msg)
if cmd == "remove":
    msg = 'Remove process started'
    print(msg)
    logger.info(msg)

    try:
        msg = "Removing the stack " + vpcstackname
        print(msg)
        logger.info(msg)

        cloudformation.delete_stack(StackName=vpcstackname)

        deletewaiter.wait(StackName=vpcstackname,
        WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 120
        })

        msg = vpcstackname + " Removed Successfully"
        print(msg)
        logger.info(msg)
    except:
        msg = "Something bad just happened."
        print(msg)
        logger.info(msg)
        
    msg = 'Remove process finished'
    print(msg)
    logger.info(msg)
