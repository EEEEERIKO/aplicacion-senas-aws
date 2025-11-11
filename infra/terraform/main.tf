locals {
  project = "aplicacion-senas-aws"
}

# S3 bucket to hold lambda artifacts
resource "aws_s3_bucket" "artifacts" {
  bucket = "${local.project}-artifacts-${random_id.bucket_suffix.hex}"

  # Secure bucket defaults
  acl = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "expire-temp-uploads"
    enabled = true

    expiration {
      days = 365
    }
  }

  tags = {
    Name = "${local.project}-artifacts"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# DynamoDB table for app data
resource "aws_dynamodb_table" "app_table" {
  name         = "aplicacion-senas-content"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # Additional attributes and GSIs for better queries (from legacy infra)
  attribute {
    name = "entity_type"
    type = "S"
  }

  attribute {
    name = "topic_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  global_secondary_index {
    name               = "gsi1-entity-type-created-at"
    hash_key           = "entity_type"
    range_key          = "created_at"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "gsi2-topic-sortkey"
    hash_key           = "topic_id"
    range_key          = "SK"
    projection_type    = "ALL"
  }

  # Security defaults
  server_side_encryption {
    enabled     = true
    kms_key_arn = null
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "aplicacion-senas-content"
  }
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_exec" {
  name = "${local.project}-lambda-exec"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Policy to allow Lambda to write logs and access DynamoDB
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.project}-lambda-policy"
  role = aws_iam_role.lambda_exec.id

  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:log-group:/aws/lambda/*"]
  }

  statement {
    sid    = "DynamoAccess"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [aws_dynamodb_table.app_table.arn]
  }
}

# Package and upload a simple user-service lambda
data "archive_file" "user_service_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../services/lambda/user_service"
  output_path = "${path.module}/../../services/lambda/user_service/user_service.zip"
}

resource "aws_s3_bucket_object" "user_service_zip" {
  bucket = aws_s3_bucket.artifacts.id
  key    = "user_service.zip"
  source = data.archive_file.user_service_zip.output_path
}

resource "aws_lambda_function" "user_service" {
  function_name = "${local.project}-user-service"
  s3_bucket     = aws_s3_bucket.artifacts.id
  s3_key        = aws_s3_bucket_object.user_service_zip.key
  handler       = "app.lambda_handler"
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.app_table.name
      APP_AWS_REGION = var.aws_region
    }
  }

  depends_on = [aws_iam_role_policy.lambda_policy]
}

# API Gateway (HTTP API) and integration to lambda
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${local.project}-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.http_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.user_service.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "all_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /v1/auth/login"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}


resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.project}"
  retention_in_days = 14
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId",
      ip             = "$context.identity.sourceIp",
      requestTime    = "$context.requestTime",
      httpMethod     = "$context.httpMethod",
      routeKey       = "$context.routeKey",
      status         = "$context.status",
      protocol       = "$context.protocol",
      responseLength = "$context.responseLength"
    })
  }

  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_service.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# OIDC provider and IAM role for GitHub Actions (assume role)
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  # NOTE: The thumbprint below is a commonly-used GitHub thumbprint; verify in your account.
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "github_actions_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [var.github_oidc_sub]
    }
  }
}

resource "aws_iam_role" "github_actions_role" {
  name               = "${local.project}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume.json
}

resource "aws_iam_role_policy" "github_actions_policy" {
  name = "${local.project}-github-actions-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:*",
          "lambda:*",
          "apigateway:*",
          "dynamodb:*",
          "iam:PassRole",
          "sts:AssumeRole"
        ],
        Effect = "Allow",
        Resource = [
          aws_s3_bucket.artifacts.arn,
          aws_lambda_function.user_service.arn,
          aws_apigatewayv2_api.http_api.execution_arn,
          aws_dynamodb_table.app_table.arn,
        ]
      }
    ]
  })
}
