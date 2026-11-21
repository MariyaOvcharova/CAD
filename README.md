# SIS 3 + Practice 7: orders system, CloudFormation, GitHub Actions (OIDC)

Region eu-north-1. `template.yaml` creates VPC, SNS -> SQS (+DLQ) -> idempotent Lambda, ECR, ECS Fargate behind an ALB.

## Deploy by hand (from a clean checkout)
    ./deploy.sh sis3-dev

## Deploy by pipeline (Practice 7)
Every push to `main` runs `.github/workflows/deploy.yml`:
1. lint (cfn-lint) and compile check
2. assume the AWS role with OIDC (no access keys are stored)
3. create/update the stack `sis3-ci`
4. build the image, tag = commit SHA, push to ECR
5. deploy the stack with `ImageTag=<commit SHA>` (new task definition revision)
6. smoke test: `curl /health` through the ALB

The role ARN is in the repository variable `DEPLOY_ROLE_ARN`. Nothing secret is stored in GitHub.

## Delete
    aws cloudformation delete-stack --stack-name sis3-ci
