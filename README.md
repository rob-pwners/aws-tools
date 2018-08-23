# aws-tools

## EC2 UserData Privesc
Usage: python ec2_userdata_privesc.py AWS_KEY_ID AWS_SECRET "oneliner to add to the userdata"

### Info
Userdata of an EC2 instance runs on startup as root. The tool requires the below permissions:
* Describe Instances
* Describe Instance Attributes
* Modify Instance Attributes
* Stop Instances
* Start Instances

The tool will check for these permissions before executing the privilege escalation.

### Sources
The idea for this was taken from RhinoSecurity Labs who also got the idea from [dagrz](https://github.com/dagrz/aws_pwn/blob/master/elevation/bouncy_bouncy_cloudy_cloud.py).