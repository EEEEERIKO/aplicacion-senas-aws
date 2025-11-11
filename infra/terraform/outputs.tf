output "api_endpoint" {
  description = "API Gateway invoke URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "dynamodb_table" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.app_table.name
}

output "github_actions_role_arn" {
  description = "IAM Role ARN that GitHub Actions can assume via OIDC"
  value       = aws_iam_role.github_actions_role.arn
}
