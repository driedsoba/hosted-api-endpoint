variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "lambda_memory_size" {
  description = "Memory allocated to the Lambda function in MB"
  type        = number
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
