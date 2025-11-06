variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "use_localstack" {
  description = "When true, terraform resources will target LocalStack endpoints (for local testing)."
  type        = bool
  default     = false
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
  default     = "app-content"
}

variable "s3_bucket_name" {
  description = "S3 bucket for assets"
  type        = string
  default     = "aplicacion-senas-assets"
}

variable "lambda_s3_bucket" {
  description = "S3 bucket where lambda zip/image is uploaded (for terraform deploy)"
  type        = string
  default     = ""
}

variable "lambda_s3_key" {
  description = "S3 key for the lambda deployment package (zip)"
  type        = string
  default     = ""
}

variable "lambda_handler" {
  description = "Lambda handler (for zip packaging), e.g. lambda_handler.handler"
  type        = string
  default     = "lambda_handler.handler"
}
