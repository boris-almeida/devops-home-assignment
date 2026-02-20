variable "name" {
  type        = string
  description = "Project name prefix"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "cidr_block" {
  type        = string
  description = "VPC CIDR"
}

variable "az_count" {
  type        = number
  description = "How many AZs to use (2 recommended)"
  default     = 2
}
