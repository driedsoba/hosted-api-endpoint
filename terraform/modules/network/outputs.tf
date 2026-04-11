output "api_gateway_url" {
  description = "Base URL of the deployed API"
  value       = aws_api_gateway_stage.api.invoke_url
}

output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.api.id
}

output "api_key_value" {
  description = "API key for authenticating requests"
  value       = aws_api_gateway_api_key.api.value
  sensitive   = true
}
