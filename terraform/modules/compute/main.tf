data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/../../../package"
  output_path = "${path.module}/../../../lambda_package.zip"
}

#checkov:skip=CKV_AWS_272:Code signing requires AWS Signer - out of scope for this project
#checkov:skip=CKV_AWS_116:Lambda is invoked synchronously via API Gateway - DLQ does not apply
#checkov:skip=CKV_AWS_117:Lambda does not access VPC resources - VPC placement unnecessary
#checkov:skip=CKV_AWS_50:X-Ray tracing incurs cost beyond free tier - out of scope
#checkov:skip=CKV_AWS_115:Account concurrency limit too low to reserve executions
resource "aws_lambda_function" "api" {
  function_name    = var.function_name
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_handler.handler"
  runtime          = "python3.12"
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  filename         = data.archive_file.lambda_package.output_path
  source_code_hash = data.archive_file.lambda_package.output_base64sha256

  environment {
    variables = {
      API_STAGE_PREFIX = "/${var.environment}"
    }
  }

  tags = var.tags
}
