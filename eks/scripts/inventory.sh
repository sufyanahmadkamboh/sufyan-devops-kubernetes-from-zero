#!/usr/bin/env bash
# Read-only snapshot of what exists in the region. Run it before creating the cluster and again after deleting it:
# the two outputs must match. It never changes anything.
set -euo pipefail
export AWS_REGION="${AWS_REGION:-eu-central-1}" AWS_PAGER=""
count() { "$@" --output text 2>/dev/null | wc -w | tr -d ' '; }
echo "Region: $AWS_REGION"
echo "EKS clusters:          $(count aws eks list-clusters --query 'clusters[]')"
echo "VPCs:                  $(count aws ec2 describe-vpcs --query 'Vpcs[].VpcId')"
echo "NAT gateways (active): $(count aws ec2 describe-nat-gateways --filter Name=state,Values=pending,available --query 'NatGateways[].NatGatewayId')"
echo "Elastic IPs:           $(count aws ec2 describe-addresses --query 'Addresses[].AllocationId')"
echo "Load balancers:        $(( $(count aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerArn') + $(count aws elb describe-load-balancers --query 'LoadBalancerDescriptions[].LoadBalancerName') ))"
echo "EC2 instances (on):    $(count aws ec2 describe-instances --filters Name=instance-state-name,Values=pending,running --query 'Reservations[].Instances[].InstanceId')"
echo "CloudFormation stacks: $(count aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE CREATE_IN_PROGRESS DELETE_IN_PROGRESS ROLLBACK_COMPLETE --query 'StackSummaries[].StackName')"
