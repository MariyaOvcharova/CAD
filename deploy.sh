#!/bin/bash

STACK=${1:-sis3-dev}
REGION=eu-north-1

aws cloudformation deploy --region $REGION --stack-name $STACK --template-file template.yaml --capabilities CAPABILITY_IAM

REPO=$(aws cloudformation describe-stacks --region $REGION --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='RepositoryUri'].OutputValue" --output text)
NAME=$(aws cloudformation describe-stacks --region $REGION --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='RepositoryName'].OutputValue" --output text)
TAG=$(git rev-parse --short HEAD)

if ! aws ecr describe-images --region $REGION --repository-name $NAME --image-ids imageTag=$TAG > /dev/null 2>&1; then
  aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${REPO%%/*}
  docker build --platform linux/amd64 -t $REPO:$TAG app/
  docker push $REPO:$TAG
fi

aws cloudformation deploy --region $REGION --stack-name $STACK --template-file template.yaml --capabilities CAPABILITY_IAM --parameter-overrides ImageTag=$TAG

aws cloudformation describe-stacks --region $REGION --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='AppUrl'].OutputValue" --output text
