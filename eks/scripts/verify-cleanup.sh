#!/usr/bin/env bash
# Proves that nothing of the lab cluster is left. Read-only. Exit code 0 = clean, 1 = something is left.
set -uo pipefail
export AWS_REGION="${AWS_REGION:-eu-central-1}" AWS_PAGER=""
CLUSTER="${CLUSTER:-k8s-from-zero}"
left=0
report() { local name=$1 n=$2; if [ "$n" -eq 0 ]; then echo "  gone  $name"; else echo "  LEFT  $name ($n)"; left=$((left + 1)); fi; }
n() { "$@" --output text 2>/dev/null | wc -w | tr -d ' '; }

echo "Resources of the lab cluster $CLUSTER in $AWS_REGION:"
report "EKS cluster"            "$(aws eks describe-cluster --name "$CLUSTER" >/dev/null 2>&1 && echo 1 || echo 0)"
report "CloudFormation stacks"  "$(n aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE CREATE_IN_PROGRESS DELETE_IN_PROGRESS DELETE_FAILED ROLLBACK_COMPLETE --query "StackSummaries[?starts_with(StackName,'eksctl-$CLUSTER-')].StackName")"
report "VPC"                    "$(n aws ec2 describe-vpcs --filters "Name=tag:alpha.eksctl.io/cluster-name,Values=$CLUSTER" --query 'Vpcs[].VpcId')"
report "NAT gateways"           "$(n aws ec2 describe-nat-gateways --filter "Name=tag:alpha.eksctl.io/cluster-name,Values=$CLUSTER" Name=state,Values=pending,available,deleting --query 'NatGateways[].NatGatewayId')"
report "Elastic IPs"            "$(n aws ec2 describe-addresses --filters "Name=tag:alpha.eksctl.io/cluster-name,Values=$CLUSTER" --query 'Addresses[].AllocationId')"
report "EC2 nodes"              "$(n aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=$CLUSTER" Name=instance-state-name,Values=pending,running,stopping,stopped --query 'Reservations[].Instances[].InstanceId')"
report "EBS volumes"            "$(n aws ec2 describe-volumes --filters "Name=tag:eks:cluster-name,Values=$CLUSTER" --query 'Volumes[].VolumeId')"
# load balancers that Kubernetes created for Services of type LoadBalancer carry the tag kubernetes.io/cluster/<name>
lbs=0
for lb in $(aws elb describe-load-balancers --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text 2>/dev/null); do
  aws elb describe-tags --load-balancer-names "$lb" --query "TagDescriptions[].Tags[?Key=='kubernetes.io/cluster/$CLUSTER'][]" \
    --output text 2>/dev/null | grep -q . && lbs=$((lbs + 1))
done
for arn in $(aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerArn' --output text 2>/dev/null); do
  aws elbv2 describe-tags --resource-arns "$arn" --query "TagDescriptions[].Tags[?Key=='kubernetes.io/cluster/$CLUSTER'][]" \
    --output text 2>/dev/null | grep -q . && lbs=$((lbs + 1))
done
report "Load balancers (from Services)" "$lbs"
report "Security groups"        "$(n aws ec2 describe-security-groups --filters "Name=tag:alpha.eksctl.io/cluster-name,Values=$CLUSTER" --query 'SecurityGroups[].GroupId')"
report "IAM roles (eksctl-$CLUSTER-*)" "$(n aws iam list-roles --query "Roles[?starts_with(RoleName,'eksctl-$CLUSTER-')].RoleName")"
echo
if [ "$left" -eq 0 ]; then echo "Clean: nothing of $CLUSTER is left."; else echo "$left kind(s) of resources are still there."; fi
exit $(( left > 0 ))
