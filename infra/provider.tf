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

  # When testing with LocalStack, you can set endpoints via environment variables or use 'use_localstack' toggle
  endpoints = var.use_localstack ? {
    dynamodb = "http://localhost:4566"
    s3       = "http://localhost:4566"
    lambda   = "http://localhost:4566"
    apigateway = "http://localhost:4566"
  } : {}
}
