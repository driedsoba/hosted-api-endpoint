resource "aws_lambda_function" "api" {
  function_name    = var.function_name
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_handler.handler"
  runtime          = "python3.12"
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  filename         = "${path.module}/../../../lambda_package.zip"
  source_code_hash = filebase64sha256("${path.module}/../../../lambda_package.zip")

  tags = var.tags
}
