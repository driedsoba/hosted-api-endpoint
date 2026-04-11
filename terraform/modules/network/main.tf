#checkov:skip=CKV_AWS_237:Create before destroy is on the deployment resource instead
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-${var.environment}"
  description = "Fun Facts API Gateway"
  tags        = var.tags

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Proxy resource catches all paths and forwards them to Lambda,
# letting FastAPI handle its own routing internally.
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

#checkov:skip=CKV2_AWS_53:Request validation is handled by FastAPI/Pydantic at the application layer
resource "aws_api_gateway_method" "proxy" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.proxy.id
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Root path handler for requests to / (e.g. /docs, /openapi.json)
#checkov:skip=CKV2_AWS_53:Request validation is handled by FastAPI/Pydantic at the application layer
resource "aws_api_gateway_method" "root" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_rest_api.api.root_resource_id
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "root_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_rest_api.api.root_resource_id
  http_method             = aws_api_gateway_method.root.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.root_lambda,
  ]

  # Redeploy when API configuration changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy.http_method,
      aws_api_gateway_method.proxy.authorization,
      aws_api_gateway_method.proxy.api_key_required,
      aws_api_gateway_integration.lambda.uri,
      aws_api_gateway_integration.lambda.integration_http_method,
      aws_api_gateway_integration.lambda.type,
      aws_api_gateway_method.root.http_method,
      aws_api_gateway_method.root.authorization,
      aws_api_gateway_method.root.api_key_required,
      aws_api_gateway_integration.root_lambda.uri,
      aws_api_gateway_integration.root_lambda.integration_http_method,
      aws_api_gateway_integration.root_lambda.type,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

#checkov:skip=CKV2_AWS_51:Client certificate auth not needed - API key auth is sufficient
#checkov:skip=CKV2_AWS_29:WAF incurs cost - out of scope for this project
#checkov:skip=CKV_AWS_76:API Gateway access logging requires a CloudWatch log group - out of scope
#checkov:skip=CKV_AWS_73:X-Ray tracing incurs cost beyond free tier - out of scope
#checkov:skip=CKV_AWS_120:API Gateway caching incurs cost - out of scope
#checkov:skip=CKV2_AWS_4:Logging is handled at application level via request logger middleware
resource "aws_api_gateway_stage" "api" {
  deployment_id = aws_api_gateway_deployment.api.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = var.environment
  tags          = var.tags
}

resource "aws_api_gateway_api_key" "api" {
  name    = "${var.project_name}-${var.environment}-key"
  enabled = true
  tags    = var.tags
}

resource "aws_api_gateway_usage_plan" "api" {
  name = "${var.project_name}-${var.environment}-usage-plan"
  tags = var.tags

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.api.stage_name
  }

  throttle_settings {
    rate_limit  = 10
    burst_limit = 20
  }

  quota_settings {
    limit  = 100
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "api" {
  key_id        = aws_api_gateway_api_key.api.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.api.id
}

# Allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/${var.environment}/*"
}
