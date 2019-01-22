import boto3
import watchtower
import logging
import sys
import json
import datetime
from botocore.exceptions import ClientError

def perform_installation(filelist, stacklist):
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

def perform_removal(deletestacklist):
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


today = datetime.datetime.now()

# if __name__ == "__main__":


commandargs = ''

cmd = "none"

if len(sys.argv) > 2:
    commandargs = sys.argv[2]

if len(sys.argv) > 1:
    cmd = sys.argv[1]


params = json.loads(commandargs)


profile = params.get("profile", "none")

if profile == "none":
    session = boto3.Session()
else:
    session = boto3.Session(profile_name=profile)


vpcname = params.get("vpcname", "none")
uploadbucket = params.get("uploadbucket", "none")
uploadpath = params.get("uploadpath", "none")
natgateway = params.get("natgateway", "no")
region = session.region_name
deploymentfolders3 = "s3://" + uploadbucket + "/" + uploadpath
deploymentfolderhttp = "https://s3.amazonaws.com/" + uploadbucket + "/" + uploadpath

cloudformation = session.client('cloudformation')
createwaiter = cloudformation.get_waiter('stack_create_complete')
deletewaiter = cloudformation.get_waiter('stack_delete_complete')
s3 = session.client('s3')



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('VPC-load-process-' + vpcname + '-'+str((today-datetime.datetime(1970,1,1)).total_seconds()))
logGroup = '/VPC-load-process/' + vpcname
logger.addHandler(watchtower.CloudWatchLogHandler(log_group=logGroup, boto3_session=session))


msg = 'Beginning Process'
logger.info(msg)

if cmd == "create":
    msg = 'Create process started'
    logger.info(msg)

    filelist = []
    filelist.append({ "FileName": "deploy.sh" })
    filelist.append({ "FileName": "deploy.py" })
    filelist.append({ "FileName": "deploy-parameters.json" })

    stacklist = []
    stacklist.append({ "StackName": vpcname, "StackTemplateName": "CreateVPC.json" })
    stacklist.append({ "StackName": vpcname + "-Subnet-" + region, "StackTemplateName": "CreateSubnet-US-East-1.json" })
    stacklist.append({ "StackName": vpcname + "-NaclEntry-" + region, "StackTemplateName": "CreateNetworkACLEntry.json" })
    stacklist.append({ "StackName": vpcname + "-SecurityGroup-" + region, "StackTemplateName": "CreateSecurityGroup.json" })


    if natgateway == "yes":
        stacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway.json" })

    perform_installation(filelist, stacklist)

    msg = "Create process finished"
    logger.info(msg)
elif cmd == "addnatgateway":
    msg = 'Add NAT Gateway process started'
    logger.info(msg)

    filelist = []
    filelist.append({ "FileName": "deploy.sh" })
    filelist.append({ "FileName": "deploy.py" })
    filelist.append({ "FileName": "deploy-parameters.json" })

    stacklist = []
    stacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway.json" })

    perform_installation(filelist, stacklist)

    msg = "Add NAT Gateway process finished"
    logger.info(msg)
elif cmd == "removenatgateway":
    msg = 'Remove NAT Gateway process started'
    logger.info(msg)

    deletestacklist = []
    deletestacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway.json" })

    perform_removal(deletestacklist)

    msg = "Remove NAT Gateway process finished"
    logger.info(msg)
elif cmd == "remove":
    msg = 'Remove process started'
    logger.info(msg)

    deletestacklist = []
    deletestacklist.append({ "StackName": vpcname + "-NatGateway-" + region, "StackTemplateName": "CreateNatGateway.json" })
    deletestacklist.append({ "StackName": vpcname + "-SecurityGroup-" + region, "StackTemplateName": "CreateSecurityGroup.json" })
    deletestacklist.append({ "StackName": vpcname + "-NaclEntry-" + region, "StackTemplateName": "CreateNetworkACLEntry.json" })
    deletestacklist.append({ "StackName": vpcname + "-Subnet-" + region, "StackTemplateName": "CreateSubnet-US-East-1.json" })
    deletestacklist.append({ "StackName": vpcname, "StackTemplateName": "CreateVPC.json" })


    perform_removal(deletestacklist)

    msg = 'Remove process finished'
    logger.info(msg)


else:
    msg = 'Invalid Command: ' + cmd
    logger.error(msg)

msg = 'Ending Process'
logger.info(msg)
