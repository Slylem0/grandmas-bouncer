#!/usr/bin/env bash
# Run the Decider server on an EC2 GPU instance, reachable only through an SSH tunnel.
#
#   scripts/ec2_decider.sh up       # launch (g6.xlarge, NVIDIA L4 24 GB) and install Decider
#   scripts/ec2_decider.sh tunnel   # forward localhost:8099 -> instance:8099 (leave running)
#   scripts/ec2_decider.sh status
#   scripts/ec2_decider.sh down     # terminate the instance (stops billing)
#
# No inbound port except SSH from your current IP. Decider listens on the instance's 127.0.0.1.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
TYPE="${INSTANCE_TYPE:-g6.xlarge}"
NAME="grandmas-bouncer-decider"
KEY="grandmas-bouncer"
KEY_FILE="$HOME/.ssh/${KEY}.pem"
CHECKPOINT="${CHECKPOINT:-StrandsAgents/strands-decider-2B-qwen3.5-v1-2610}"
AMI_PARAM="/aws/service/deeplearning/ami/x86_64/base-oss-nvidia-driver-gpu-ubuntu-22.04/latest/ami-id"
aws() { command aws --region "$REGION" "$@"; }

instance_id() {
  aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[0].Instances[0].InstanceId' --output text
}
public_ip() {
  aws ec2 describe-instances --instance-ids "$1" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
}

user_data() {
  cat <<EOF
#!/bin/bash
set -eux
sudo -u ubuntu bash -lc 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u ubuntu bash -lc '~/.local/bin/uv venv ~/decider --python 3.12 && ~/.local/bin/uv pip install -p ~/decider strands-decider'
cat >/etc/systemd/system/decider.service <<UNIT
[Unit]
Description=Strands Decider
After=network-online.target
[Service]
User=ubuntu
ExecStart=/home/ubuntu/decider/bin/strands-decider serve ${CHECKPOINT} --device cuda --host 127.0.0.1 --port 8099
Restart=on-failure
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now decider
EOF
}

up() {
  if [[ "$(instance_id)" != "None" ]]; then echo "already exists: $(instance_id)"; return; fi
  if [[ ! -f "$KEY_FILE" ]]; then
    aws ec2 create-key-pair --key-name "$KEY" --query KeyMaterial --output text >"$KEY_FILE"
    chmod 600 "$KEY_FILE"
  fi
  local vpc sg ami my_ip
  vpc=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
  sg=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$NAME" --query 'SecurityGroups[0].GroupId' --output text)
  if [[ "$sg" == "None" ]]; then
    sg=$(aws ec2 create-security-group --group-name "$NAME" --description "SSH only, for the Decider tunnel" --vpc-id "$vpc" --query GroupId --output text)
  fi
  my_ip=$(curl -s https://checkip.amazonaws.com)
  aws ec2 authorize-security-group-ingress --group-id "$sg" --protocol tcp --port 22 --cidr "${my_ip}/32" 2>/dev/null || true
  ami=$(aws ssm get-parameter --name "$AMI_PARAM" --query Parameter.Value --output text)
  aws ec2 run-instances --image-id "$ami" --instance-type "$TYPE" --key-name "$KEY" \
    --security-group-ids "$sg" --user-data "$(user_data)" \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=80,VolumeType=gp3}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME}]" \
    --query 'Instances[0].InstanceId' --output text
  echo "launched; first boot installs Decider and downloads ~4.5 GB (5-10 min). Then: $0 tunnel"
}

tunnel() {
  local id; id=$(instance_id)
  echo "tunnel localhost:8099 -> $id (Ctrl-C to stop)"
  exec ssh -i "$KEY_FILE" -o StrictHostKeyChecking=accept-new -N -L 8099:127.0.0.1:8099 "ubuntu@$(public_ip "$id")"
}

status() {
  local id; id=$(instance_id)
  [[ "$id" == "None" ]] && { echo "no instance"; return; }
  aws ec2 describe-instances --instance-ids "$id" \
    --query 'Reservations[0].Instances[0].[InstanceId,InstanceType,State.Name,PublicIpAddress]' --output text
}

down() {
  local id; id=$(instance_id)
  [[ "$id" == "None" ]] && { echo "no instance"; return; }
  aws ec2 terminate-instances --instance-ids "$id" --query 'TerminatingInstances[0].CurrentState.Name' --output text
}

"${1:-status}"
