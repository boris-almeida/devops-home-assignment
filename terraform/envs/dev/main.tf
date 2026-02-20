module "vpc" {
  source = "../../modules/vpc"

  name        = var.project_name
  environment = var.environment

  cidr_block = "10.0.0.0/16"

  az_count = 2
}

module "eks" {
  source = "../../modules/eks"

  name        = var.project_name
  environment = var.environment

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}

