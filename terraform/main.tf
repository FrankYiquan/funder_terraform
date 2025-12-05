terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ----------------------------
# IMPORT EXISTING S3 BUCKETS
# ----------------------------
data "aws_s3_bucket" "grant" {
  bucket = var.grant_bucket_name
}

data "aws_s3_bucket" "linking" {
  bucket = var.linking_bucket_name
}

# ----------------------------
# IAM ROLE FOR LAMBDA
# ----------------------------
module "lambda_role" {
  source = "./modules/iam"

  grant_bucket_arn   = data.aws_s3_bucket.grant.arn
  linking_bucket_arn = data.aws_s3_bucket.linking.arn

  sqs_queue_arn      = module.nsf.queue_arn   
}


# ----------------------------
# SHARED LAYERS
# ----------------------------
module "shared_utils" {
  source            = "./modules/layer"
  layer_name        = "shared-utils-layer"
  layer_source_dir  = "../lambda-code/layers/shared_utils_layer"
}

module "requests_layer" {
  source            = "./modules/layer"
  layer_name        = "requests-layer"
  layer_source_dir  = "../lambda-code/layers/requests_layer"
}

# ----------------------------
# NSF FUNDERS PIPELINE
# ----------------------------
module "nsf" {
  source             = "./modules/funder_pipeline"
  name               = "NSF2222" #subject to change 
  lambda_source_dir  = "../lambda-code/nsf"
  handler            = "handler.lambda_handler"
  layers             = [module.shared_utils.arn, module.requests_layer.arn]
  lambda_role_arn    = module.lambda_role.arn

  grant_bucket_name  = var.grant_bucket_name
  linking_bucket_name = var.linking_bucket_name
}

# ----------------------------
# NIH FUNDERS PIPELINE
# ----------------------------
# module "nih" {
#   source             = "./modules/funder_pipeline"
#   name               = "NIH"
#   lambda_source_dir  = "../lambda-code/nih"
#   handler            = "handler.lambda_handler"
#   layers             = [module.shared_utils.arn, module.requests_layer.arn]
#   lambda_role_arn    = module.lambda_role.arn

#   grant_bucket_name  = var.grant_bucket_name
#   linking_bucket_name = var.linking_bucket_name
# }
