############################################################
# Minimal Terraform resources for AWS (DynamoDB, S3, Lambda, API Gateway)
# This is an opinionated scaffold. Customize values and policies for production.
############################################################

resource "aws_s3_bucket" "assets" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_acl" "assets_acl" {
  bucket = aws_s3_bucket.assets.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets_encryption" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "assets_block" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "assets_versioning" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "assets_lifecycle" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id      = "expire-temp-uploads"
    status  = "Enabled"

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

resource "aws_dynamodb_table" "app_table" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
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

  # SECURITY: Enable encryption at rest with AWS managed key
  server_side_encryption {
    enabled     = true
    kms_key_arn = null  # null = use AWS managed key; set to aws_kms_key.*.arn for CMK
  }

  # Enable point-in-time recovery for data durability
  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Environment = "production"
    Project     = "aplicacion-senas"
    ManagedBy   = "terraform"
  }
}

########################################
# IAM role for Lambda with limited permissions
########################################
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "aplicacion_senas_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "aplicacion_senas_lambda_policy"
  description = "Allow Lambda to access DynamoDB and S3 with least privilege."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "DynamoDBAccess"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:BatchWriteItem",
        ]
        Effect = "Allow"
        Resource = [
          aws_dynamodb_table.app_table.arn,
          "${aws_dynamodb_table.app_table.arn}/index/*"
        ]
      },
      {
        Sid = "S3ReadAccess"
        Action = [
          "s3:GetObject",
        ]
        Effect   = "Allow"
        Resource = ["${aws_s3_bucket.assets.arn}/*"]
      },
      {
        Sid = "CloudWatchLogsAccess"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect = "Allow"
        Resource = "arn:aws:logs:*:*:log-group:/aws/lambda/aplicacion-senas-api:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

################################################
# Lambda function (expects a deployment package in S3)
################################################
resource "aws_lambda_function" "api" {
  filename         = var.lambda_s3_key != "" ? "" : null
  function_name    = "aplicacion-senas-api"
  role             = aws_iam_role.lambda_role.arn
  handler          = var.lambda_handler
  runtime          = "python3.11"

  # If using S3 packaging via terraform, set s3_bucket and s3_key
  s3_bucket = var.lambda_s3_bucket != "" ? var.lambda_s3_bucket : null
  s3_key    = var.lambda_s3_key != "" ? var.lambda_s3_key : null

  # Keep small ephemeral timeout for API lambda; increase as needed
  timeout = 15

  environment {
    variables = {
      DYNAMO_TABLE = var.dynamodb_table_name
      S3_BUCKET     = var.s3_bucket_name
    }
  }
}

################################################
# API Gateway (HTTP API) and integration to Lambda
################################################
resource "aws_apigatewayv2_api" "http_api" {
  name          = "aplicacion-senas-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_allowed_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "all_routes" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/aplicacion-senas-api"
  retention_in_days = 7
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
