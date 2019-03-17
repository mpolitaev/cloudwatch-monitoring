#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta
from aws_discovery import aws_client

parser = argparse.ArgumentParser(description="Get specified AWS CloudWatch metric.")
parser.add_argument('region', type=str, help='AWS Region.')
parser.add_argument('namespace', type=str, help='Namespace, like "AWS/EC2".')
parser.add_argument('metricname', type=str, help='Metric to monitor, like "CPU usage".')
parser.add_argument('dimensions', type=str, help='Dimensions.')
parser.add_argument('period', type=int, help='The granularity, of the returned data points.')
parser.add_argument('statistics', type=str, help='Type of aggregation for data points.')
args = parser.parse_args()


def get_metric(cln, namespace, metricname, dimensions, period, statistics):
    endtime = datetime.utcnow()
    starttime = endtime - timedelta(seconds=period)
    dim = [{'Name': d.split('=')[0], 'Value': d.split('=')[1]} for d in dimensions.split(',')]
    metric = cln.get_metric_statistics(
        Namespace=namespace,
        MetricName=metricname,
        Dimensions=dim,
        StartTime=starttime,
        EndTime=endtime,
        Period=period,
        Statistics=[statistics]
    )
    if metric['Datapoints'] != []:
        print(metric['Datapoints'][0][statistics])
    else:
        print('NO_DATAPOINTS')


client = aws_client('cloudwatch', args.region)
get_metric(client, args.namespace, args.metricname, args.dimensions, args.period, args.statistics)
