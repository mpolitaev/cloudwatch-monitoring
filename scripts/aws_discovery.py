#!/usr/bin/env python3
import argparse
import boto3
import json


def aws_client(service, region):
    return boto3.client(service, region)


def discovery_ec2(cln):
    response = cln.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    return format_to_json([{'{#INSTANCE_ID}': instance.get('InstanceId'),
                            '{#INSTANCE_NAME}': t.get('Value', 'NO_NAME')}
                           for reservation in response['Reservations']
                           for instance in reservation['Instances']
                           for t in instance['Tags'] if t['Key'] == 'Name'])


def discovery_elb(cln):
    response = cln.describe_load_balancers()
    return format_to_json([{'{#ELB_NAME}': l['LoadBalancerName']} for l in response['LoadBalancerDescriptions']])


def discovery_elbv2(cln):
    response = cln.describe_target_groups()
    response_lb = cln.describe_load_balancers()
    return format_to_json([{'{#ELBV2_ARN}': a[a.find('/')+1:],
                            '{#ELBV2_NAME}': l['LoadBalancerName'],
                            '{#ELBV2_TARGET_GROUP_NAME}': t['TargetGroupName'],
                            '{#ELBV2_TARGET_GROUP}': t['TargetGroupArn'][t['TargetGroupArn'].rfind(':')+1:],
                            '{#ELBV2_TYPE}': l['Type'].capitalize()}
                           for t in response['TargetGroups']
                           for a in t['LoadBalancerArns']
                           for l in response_lb['LoadBalancers'] if l['LoadBalancerArn'] == a])


def discovery_efs(cln):
    response = cln.describe_file_systems()
    return format_to_json([{'{#EFS_NAME}': f.get('Name', 'NO_NAME'),
                            '{#EFS_ID}': f.get('FileSystemId', 'NO_NAME')}
                           for f in response['FileSystems']])


def format_to_json(data):
    print(json.dumps({"data": data}, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discovery AWS Services for Zabbix")
    parser.add_argument('service', type=str, choices=['ec2', 'elb', 'elbv2', 'efs', 'cloudwatch'],
                        help='Service which should be discovered')
    parser.add_argument('region', type=str, help='Region for discovery')
    args = parser.parse_args()

    client = aws_client(args.service, args.region)
    globals().get('discovery_' + args.service)(client)
