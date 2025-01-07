# Example Terraform configuration
provider "aws" {
  region = "us-east-1"
}

# Frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "resumebuildertex-frontend"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3Origin"
  }
  # ... other CloudFront settings
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "resumebuildertex-cluster"
}

# Fargate Service
resource "aws_ecs_service" "api" {
  name            = "resumebuildertex-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  launch_type     = "FARGATE"
  # ... other service settings
} 