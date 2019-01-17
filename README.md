# VPC-Cloudformation
This set of CloudFormation scripts sets up a reference VPC.

## Installation
To use this, do the following:
1. install python3
2. install boto3 -
```
pip3 install boto3
```
3. install watchtower -
```
pip3 install watchtower
```
4. install awscli -
```
pip3 install awscli
```
5. Make sure to set up a profile configuration in your AWS CLI by running the following:
```
aws configure --profile <profile name>
```
Enter your AWS Access Key Id and AWS Secret Access Key.  Enter us-east-1 for your region, and whichever output format you'd like (I use json).

6. Create an S3 bucket to upload deployment and cloudformation scripts to.

## Running
1. Open the delpoy-parameters.json file and edit the following:
  * profile - profile name defined in your AWS configuration
  * vpcname - identifier of the VPC you'd like to create; this will be used in the name of all of the components
  * uploadbucket - S3 bucket to upload deployment scripts and cloudformation scripts at runtime
  * uploadpath - path to upload scripts to within the S3 bucket
  * natgateway - [yes|no] - when running the create command, determines whether to create Nat Gateways in the two public subnets; note that Nat Gateways incur AWS charges, so don't leave these running if you don't need them
2. The following commands are available:
  * ./deploy.sh create - creates the entire VPC, Subnets, Internet Gateay, NACL's, Security Groups, Route Tables;
    * If the natgateway parameter is set to yes, then it also creates the Nat Gateways, their associated Elastic IP Addresses, entries in the private Route Tables, and entries in the private NACL's.
  * ./deploy.sh remove - remove the entire VPC and associated bits and pieces, including the Nat Gateways
  * ./deploy.sh addnatgateway - creates the Nat Gateways, their associated Elastic IP Addresses, entries in the private Route Tables, and entries in the private NACL's.
    * Assumes that the VPC has already been created, but without the Nat Gatways
  * ./deploy.sh removenatgateway - removes the Nat Gateways, their associated Elastic IP Addresses, entries in the private Route Tables, and entries in the private NACL's.
    * Leaves the rest of the VPC intact.

## Notes
* The SSH ports for the public subnets won't be quite perfect.  The SSH ports in the public NACL's will be open to the world, however they will be limited to within the VPC for the two public security groups: "Public - WebDMZ" and "Public - SSHDMZ".  The idea is that you really only want to allow SSH access into boxes from specific IP addresses.  Therefore, to give yourself SSH access to boxes that are in either "Public - WebDMZ" or "Public - SSHDMZ", you need to manually go in to those security groups and allow your IP address.
* This currently only works on macOS/Linux.
* This also currently only works with the us-east-1 region.  (At some point I might create future release to allow deployment into additional regions.)
