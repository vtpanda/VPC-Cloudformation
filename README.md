# VPC-Cloudformation
This set of CloudFormation scripts sets up a reference VPC.

## Installation (Mac Only)
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

## Running (Mac Only)
1. Open the delpoy-parameters.json file and edit the following:
  * profile - profile name defined in your AWS configuration
  * vpcname - identifier of the VPC you'd like to create; this will be used in the name of all of the components
  * uploadbucket - S3 bucket to upload deployment scripts and cloudformation scripts at runtime
  * uploadpath - path to upload scripts to within the S3 bucket
  * natgateway - [yes|no] - when running the create command, determines whether to create Nat Gateways in the two public subnets; note that Nat Gateways incur AWS charges, so don't leave these running if you don't need them
2. The following commands are available:
```
./deploy.sh create
```
  * Creates the entire VPC, Subnets, Internet Gateway, NACL's, Security Groups, Route Tables;
    * If the natgateway parameter is set to yes, then it also creates the Nat Gateways, their associated Elastic IP Addresses, and entries in the private Route Tables.

  ```
  ./deploy.sh remove
  ```
  * Removes the entire VPC and associated bits and pieces, including the Nat Gateways

  ```
  ./deploy.sh addnatgateway
  ```
  * Creates the Nat Gateways, their associated Elastic IP Addresses, and entries in the private Route Tables.
    * Assumes that the VPC has already been created, but without the Nat Gatways

  ```
  ./deploy.sh removenatgateway
  ```
  * Removes the Nat Gateways, their associated Elastic IP Addresses, and entries in the private Route Tables.
    * Leaves the rest of the VPC intact.

## If you don't have a Mac:
If you don't have a Mac, you can manually build the reference VPC by going into the AWS Console in us-east-1 (Northern Virginia), navigating to CloudFormation, and manually running the following CloudFormation templates, in order:
1. CreateVPC.json
2. CreateSubnet-US-East-1.json
3. CreateNetworkACLEntry.json
4. CreateSecurityGroup.json
5. CreateNatGateway.json (only if you need this; AWS charges for this)

Use the same VPCName value for each of the five templates.

To Uninstall manually, delete each of the stacks in reverse order.

## Notes
* The SSH ports for the public subnets will need to be tweaked to allow access after the VPC is created.  The SSH ports in the public NACL's will be open to the world (which I'm not crazy about, but maybe this is the way to do it), however they will be limited to within the VPC for the two public security groups: "Public - WebDMZ" and "Public - SSHDMZ".  The idea is that you really only want to allow SSH access into boxes from specific IP addresses.  Therefore, to give yourself SSH access to boxes that are in either "Public - WebDMZ" or "Public - SSHDMZ", you need to manually go in to those security groups and allow your IP address.
* This currently only works on macOS/Linux.
* This also currently only works with the us-east-1 region.  (At some point I might create future release to allow deployment into additional regions.)
* I'd like feedback particularly on my NACL permissions and Security Group permissions.  I've taken a crack at a useful set of permissions to cover the common use-case of web server on the front end and database (on either EC2 or RDS) on the backend, along with the need to SSH into the servers.
  * I've just recently opened inbound HTTP(s) ports to the world in the private NACL's in an attempt to make yum work better from the private subnet (which it seems to, most of the time, but not all of the time).  I'm not fond of having these inbound HTTP(s) ports open to to the world in the private subnet, but maybe this is okay.
  * My private subnet still seems a little flaky in terms of permitting yum updates to occur on servers within the private subnet.  I'm getting a fair number of timeouts before it completes.
