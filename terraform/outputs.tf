output "api_gateway_url" {
  description = "Base URL of the deployed API"
  value       = module.network.api_gateway_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.compute.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.compute.function_arn
}

output "api_key_value" {
  description = "API key for authenticating requests"
  value       = module.network.api_key_value
  sensitive   = true
}
