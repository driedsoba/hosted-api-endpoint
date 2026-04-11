module "compute" {
  source = "./modules/compute"

  function_name      = local.function_name
  lambda_memory_size = var.lambda_memory_size
  lambda_timeout     = var.lambda_timeout
  environment        = var.environment
  tags               = local.common_tags
}

module "network" {
  source = "./modules/network"

  project_name        = var.project_name
  environment         = var.environment
  lambda_function_arn = module.compute.function_arn
  lambda_invoke_arn   = module.compute.invoke_arn
  tags                = local.common_tags
}
