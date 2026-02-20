variable "aws_profile" {
  type        = string
  description = "AWS CLI profile name"
  default     = "sandbox"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Name prefix for resources"
  default     = "devops-home"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "dev"
}
