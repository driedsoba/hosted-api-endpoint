variable "project_name" {
  description = "Project name for API Gateway naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "lambda_function_arn" {
  description = "ARN of the Lambda function to integrate with"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
