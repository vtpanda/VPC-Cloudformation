#!/bin/bash
#profile must be set up
#region is taken from the profile that is sent


# Things to add:
# 1. Add command line switch for creating natgateway or not
# 2. Add command line switch for removing natgateway
# 3. Add vpcname to commandline
# 4. Add profile name to commandline
# 5. Add deployment path to commandline
# 6. Add ability to update stack
# 7. Pull out Routes, NetworkAclEntryies, and SecurityGroups into their own stacks
# 7.1 Perhaps we can figure out how to have different sets of routes and NetworkAclEntries based on different stacks
# 8. Look into seeing if we should do stack-sets



cmd=$1
vpcname=UsEast1VPC1
profile=myaws
region=$(aws configure get region --profile $profile)
deploymentfolders3=s3://vtpanda-deployment-$region/vpc/$vpcname
deploymentfolderhttp=https://s3.amazonaws.com/vtpanda-deployment-$region/vpc/$vpcname


#####Don't worry about these parameters
vpcstackname=$vpcname
subnetstackname=$vpcname-Subnet-$region
natgatewaystackname=$vpcname-NatGateway-$region
######


if [[ -z "$cmd" ]]; then
    cmd=create
fi

if [[ "$cmd" == "remove" ]]; then
  echo "Undeploying."

  # echo "Removing files from S3."
  # aws s3 rm $deploymentfolders3/ --recursive --region $region --profile $profile

  # echo "Deleting stack $natgatewaystackname."
  # aws cloudformation delete-stack --stack-name $natgatewaystackname --region $region --profile $profile
  # aws cloudformation wait stack-delete-complete --stack-name $natgatewaystackname --region $region --profile $profile
  # if test "$?" != "0"
  # then
  #     echo "$natgatewaystackname Did Not Return in a Timely Manner"
  #     exit $?
  # fi
  # echo "$natgatewaystackname Deleted Successfully"


  echo "Deleting stack $subnetstackname."
  aws cloudformation delete-stack --stack-name $subnetstackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $subnetstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$subnetstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$subnetstackname Deleted Successfully"


  echo "Deleting stack $vpcstackname."
  aws cloudformation delete-stack --stack-name $vpcstackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $vpcstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$vpcstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$vpcstackname Deleted Successfully"

  echo "Undeploy done."


elif [[ "$cmd" == "update" ]]; then

  echo "This hasn't been implemented yet."

elif [[ "$cmd" == "create" ]]; then

  echo "Deploying."

  echo "Uploading files to S3"
  aws s3 cp ./CreateVPC.json $deploymentfolders3/CreateVPC.json --region $region --profile $profile
  aws s3 cp ./CreateSubnets-US-East-1.json $deploymentfolders3/CreateSubnets-US-East-1.json --region $region --profile $profile
  aws s3 cp ./CreateNatGateway-US-East-1.json $deploymentfolders3/CreateNatGateway-US-East-1.json --region $region --profile $profile
  aws s3 cp ./deploy.sh $deploymentfolders3/deploy.sh --region $region --profile $profile


  echo "Deploying the stack $vpcstackname"
  aws cloudformation create-stack --stack-name $vpcstackname --template-url $deploymentfolderhttp/CreateVPC.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $vpcstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$vpcstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$vpcstackname Deployed Successfully"

  echo "Deploying the stack $subnetstackname"
  aws cloudformation create-stack --stack-name $subnetstackname --template-url $deploymentfolderhttp/CreateSubnets-US-East-1.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $subnetstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$subnetstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$subnetstackname Deployed Successfully"

  # echo "Deploying the stack $natgatewaystackname"
  # aws cloudformation create-stack --stack-name $natgatewaystackname --template-url $deploymentfolderhttp/CreateNatGateway-US-East-1.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  # aws cloudformation wait stack-create-complete --stack-name $natgatewaystackname --region $region --profile $profile
  # if test "$?" != "0"
  # then
  #     echo "$natgatewaystackname Did Not Return in a Timely Manner"
  #     exit $?
  # fi
  # echo "$natgatewaystackname Deployed Successfully"

  echo "Deploy Done."
else
  echo "Invalid Command"
fi
