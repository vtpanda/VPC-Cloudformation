#!/usr/local/bin/python3

import boto3
import watchtower
import logging
import sys
import json
import datetime
from botocore.exceptions import ClientError


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
deploymentfolders3 = "s3://" + uploadbucket + "/" + uploadpath
deploymentfolderhttp = "https://s3.amazonaws.com/" + uploadbucket + "/" + uploadpath

filelist = []
filelist.append({ "FileName": "deploy.sh" })
filelist.append({ "FileName": "deploy.py" })
filelist.append({ "FileName": "deploy-parameters.json" })

stacklist = []
stacklist.append({ "StackName": vpcname, "StackTemplateName": "CreateVPC.json" })
stacklist.append({ "StackName": vpcname + "-Subnet-" + region, "StackTemplateName": "CreateSubnet-US-East-1.json" })
# stacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway-US-East-1.json" })
# stacklist.append({ "StackName": vpcname + "-NaclEntry-" + region, "StackTemplateName": "CreateNetworkACLEntry.json" })
# stacklist.append({ "StackName": vpcname + "-SecurityGroup-" + region, "StackTemplateName": "CreateSecurityGroup.json" })
stacklist.append({ "StackName": vpcname + "-NaclEntryNoPublicSSH-" + region, "StackTemplateName": "CreateNetworkACLEntryNoPublicSSH.json" })
stacklist.append({ "StackName": vpcname + "-SecurityGroupNoSSH-" + region, "StackTemplateName": "CreateSecurityGroupNoPublicSSH.json" })

deletestacklist = []
deletestacklist.append({ "StackName": vpcname + "-SecurityGroupNoSSH-" + region, "StackTemplateName": "CreateSecurityGroupNoPublicSSH.json" })
deletestacklist.append({ "StackName": vpcname + "-NaclEntryNoPublicSSH-" + region, "StackTemplateName": "CreateNetworkACLEntryNoPublicSSH.json" })
# deletestacklist.append({ "StackName": vpcname + "-SecurityGroup-" + region, "StackTemplateName": "CreateSecurityGroup.json" })
# deletestacklist.append({ "StackName": vpcname + "-NaclEntry-" + region, "StackTemplateName": "CreateNetworkACLEntry.json" })
# deletestacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway-US-East-1.json" })
deletestacklist.append({ "StackName": vpcname + "-Subnet-" + region, "StackTemplateName": "CreateSubnet-US-East-1.json" })
deletestacklist.append({ "StackName": vpcname, "StackTemplateName": "CreateVPC.json" })

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
logger.info(msg)

if cmd == "create":
    msg = 'Create process started'
    logger.info(msg)


    try:
        msg = 'Uploading Files'
        logger.info(msg)

        for x in filelist:
            s3.upload_file(Filename="./" + x["FileName"], Bucket=uploadbucket, Key=uploadpath + x["FileName"])

        for y in stacklist:
            s3.upload_file(Filename="./" + y["StackTemplateName"], Bucket=uploadbucket, Key=uploadpath + y["StackTemplateName"])

        msg = 'Done Uploading Files'
        logger.info(msg)

        for z in stacklist:
            msg = "Deploying the stack " + z["StackName"]
            logger.info(msg)

            response = cloudformation.create_stack(StackName=z["StackName"], TemplateURL=deploymentfolderhttp + z["StackTemplateName"], Parameters= [ { "ParameterKey": "VPCName", "ParameterValue": vpcname } ] )

            vpcstackid = response["StackId"]

            createwaiter.wait(StackName=z["StackName"],
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 120
            })

            msg = z["StackName"] + " Deployed Successfully with StackId: " + vpcstackid
            logger.info(msg)


    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=True)

    msg = "Create process finished"
    logger.info(msg)

elif cmd == "remove":
    msg = 'Remove process started'
    logger.info(msg)

    try:
        for z in deletestacklist:
            msg = "Removing the stack " + z["StackName"]
            logger.info(msg)

            cloudformation.delete_stack(StackName=z["StackName"])

            deletewaiter.wait(StackName=z["StackName"],
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 120
            })

            msg = z["StackName"] + " Removed Successfully"
            logger.info(msg)

    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=True)

    msg = 'Remove process finished'
    logger.info(msg)

elif cmd == "update":
    msg = 'Update process has not been implemented yet.'
    logger.info(msg)
    # msg = 'Update process started'
    # logger.info(msg)
    #
    #
    # msg = 'Update process finished'
    # logger.info(msg)

else:
    msg = 'Invalid Command'
    logger.error(msg)

msg = 'Ending Process'
logger.info(msg)
