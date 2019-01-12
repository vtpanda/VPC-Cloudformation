#!/bin/bash
#profile must be set up
#region is taken from the profile that is sent

cmd=$1
vpcname=WordPress
profile=myaws
region=$(aws configure get region --profile $profile)
deploymentfolders3=s3://vtpanda-deployment-$region/vpc/$vpcname
deploymentfolderhttp=https://s3.amazonaws.com/vtpanda-deployment-$region/vpc/$vpcname


#####Don't worry about these parameters
vpcstackname=$vpcname
subnetstackname=$vpcname-Subnet-$region
natgatewaystackname=$vpcname-NatGateway-$region
naclentrystackname=$vpcname-NaclEntry-$region
securitygroupstackname=$vpcname-SecurityGroup-$region
######


if [[ -z "$cmd" ]]; then
    cmd=create
fi

if [[ "$cmd" == "remove" ]]; then
  echo "Undeploying."

  # echo "Removing files from S3."
  # aws s3 rm $deploymentfolders3/ --recursive --region $region --profile $profile

  echo "Deleting stack $natgatewaystackname."
  aws cloudformation delete-stack --stack-name $natgatewaystackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $natgatewaystackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$natgatewaystackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$natgatewaystackname Deleted Successfully"


  echo "Deleting stack $subnetstackname."
  aws cloudformation delete-stack --stack-name $subnetstackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $subnetstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$subnetstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$subnetstackname Deleted Successfully"

  echo "Deleting stack $securitygroupstackname."
  aws cloudformation delete-stack --stack-name $securitygroupstackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $securitygroupstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$securitygroupstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$securitygroupstackname Deleted Successfully"

  echo "Deleting stack $naclentrystackname."
  aws cloudformation delete-stack --stack-name $naclentrystackname --region $region --profile $profile
  aws cloudformation wait stack-delete-complete --stack-name $naclentrystackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$naclentrystackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$naclentrystackname Deleted Successfully"

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
  aws s3 cp ./CreateSubnet-US-East-1.json $deploymentfolders3/CreateSubnet-US-East-1.json --region $region --profile $profile
  aws s3 cp ./CreateNatGateway-US-East-1.json $deploymentfolders3/CreateNatGateway-US-East-1.json --region $region --profile $profile
  aws s3 cp ./CreateAllNetworkACLEntry.json $deploymentfolders3/CreateAllNetworkACLEntry.json --region $region --profile $profile
  aws s3 cp ./CreateAllSecurityGroup.json $deploymentfolders3/CreateAllSecurityGroup.json --region $region --profile $profile
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

  echo "Deploying the stack $naclentrystackname"
  aws cloudformation create-stack --stack-name $naclentrystackname --template-url $deploymentfolderhttp/CreateAllNetworkACLEntry.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $naclentrystackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$naclentrystackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$naclentrystackname Deployed Successfully"

  echo "Deploying the stack $securitygroupstackname"
  aws cloudformation create-stack --stack-name $securitygroupstackname --template-url $deploymentfolderhttp/CreateAllSecurityGroup.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $securitygroupstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$securitygroupstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$securitygroupstackname Deployed Successfully"

  echo "Deploying the stack $subnetstackname"
  aws cloudformation create-stack --stack-name $subnetstackname --template-url $deploymentfolderhttp/CreateSubnet-US-East-1.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $subnetstackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$subnetstackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$subnetstackname Deployed Successfully"


  echo "Deploy Done."

elif [[ "$cmd" == "addnatgateway" ]]; then
  echo "$subnetstackname Deployed Successfully"

  echo "Deploying the stack $natgatewaystackname"
  aws cloudformation create-stack --stack-name $natgatewaystackname --template-url $deploymentfolderhttp/CreateNatGateway-US-East-1.json --parameters ParameterKey=VPCName,ParameterValue=$vpcname --region $region --profile $profile
  aws cloudformation wait stack-create-complete --stack-name $natgatewaystackname --region $region --profile $profile
  if test "$?" != "0"
  then
      echo "$natgatewaystackname Did Not Return in a Timely Manner"
      exit $?
  fi
  echo "$natgatewaystackname Deployed Successfully"

else
  echo "Invalid Command"
fi
