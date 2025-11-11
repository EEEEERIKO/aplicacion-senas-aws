variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "github_repo" {
  description = "GitHub repository in the form owner/repo (used for OIDC role condition)"
  type        = string
}

variable "github_oidc_sub" {
  description = "Condition sub for GitHub OIDC, e.g. repo:OWNER/REPO:ref:refs/heads/main"
  type        = string
  default     = "repo:EEEEERIKO/aplicacion-senas-aws:ref:refs/heads/main"
}

variable "lambda_runtime" {
  description = "Lambda runtime to use"
  type        = string
  default     = "python3.10"
}
