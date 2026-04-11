data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/../../../package"
  output_path = "${path.module}/../../../lambda_package.zip"
}

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
