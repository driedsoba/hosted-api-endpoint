variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "fun-facts-api"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-southeast-1"
}

variable "lambda_memory_size" {
  description = "Memory allocated to the Lambda function in MB"
  type        = number
  default     = 256

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 3008
    error_message = "Lambda memory must be between 128 and 3008 MB."
  }
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30

  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
