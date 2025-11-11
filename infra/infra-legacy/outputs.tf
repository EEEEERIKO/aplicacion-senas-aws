output "api_endpoint" {
  description = "HTTP API endpoint URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "dynamodb_table" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.app_table.name
}

output "s3_bucket" {
  description = "S3 bucket name for assets"
  value       = aws_s3_bucket.assets.bucket
}
