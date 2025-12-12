# Mental Health Platform - Terraform Infrastructure
# Deploy to Kenya (Nairobi) and South Africa (Cape Town) regions

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure AWS Provider for Kenya (Nairobi) region
provider "aws" {
  region = "af-south-1" # Cape Town (closest to Kenya)
  alias  = "kenya"
  
  default_tags {
    tags = {
      Project     = "mental-health-platform"
      Environment = var.environment
      Region      = "kenya"
    }
  }
}

# Configure AWS Provider for South Africa (Cape Town) region
provider "aws" {
  region = "af-south-1" # Cape Town
  alias  = "south-africa"
  
  default_tags {
    tags = {
      Project     = "mental-health-platform"
      Environment = var.environment
      Region      = "south-africa"
    }
  }
}

# Variables are defined in variables.tf

# VPC for Kenya region
resource "aws_vpc" "kenya_vpc" {
  provider = aws.kenya
  
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-kenya-vpc"
  }
}

# Internet Gateway for Kenya
resource "aws_internet_gateway" "kenya_igw" {
  provider = aws.kenya
  
  vpc_id = aws_vpc.kenya_vpc.id
  
  tags = {
    Name = "${var.project_name}-kenya-igw"
  }
}

# Public Subnets for Kenya
resource "aws_subnet" "kenya_public_subnets" {
  provider = aws.kenya
  
  count = 2
  
  vpc_id                  = aws_vpc.kenya_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.kenya_azs.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-kenya-public-subnet-${count.index + 1}"
  }
}

# Private Subnets for Kenya
resource "aws_subnet" "kenya_private_subnets" {
  provider = aws.kenya
  
  count = 2
  
  vpc_id            = aws_vpc.kenya_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.kenya_azs.names[count.index]
  
  tags = {
    Name = "${var.project_name}-kenya-private-subnet-${count.index + 1}"
  }
}

# Availability Zones for Kenya
data "aws_availability_zones" "kenya_azs" {
  provider = aws.kenya
  state    = "available"
}

# Route Table for Public Subnets (Kenya)
resource "aws_route_table" "kenya_public_rt" {
  provider = aws.kenya
  
  vpc_id = aws_vpc.kenya_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.kenya_igw.id
  }
  
  tags = {
    Name = "${var.project_name}-kenya-public-rt"
  }
}

# Route Table Associations for Public Subnets (Kenya)
resource "aws_route_table_association" "kenya_public_rta" {
  provider = aws.kenya
  
  count = length(aws_subnet.kenya_public_subnets)
  
  subnet_id      = aws_subnet.kenya_public_subnets[count.index].id
  route_table_id = aws_route_table.kenya_public_rt.id
}

# NAT Gateway for Private Subnets (Kenya)
resource "aws_eip" "kenya_nat_eip" {
  provider = aws.kenya
  
  domain = "vpc"
  
  tags = {
    Name = "${var.project_name}-kenya-nat-eip"
  }
}

resource "aws_nat_gateway" "kenya_nat" {
  provider = aws.kenya
  
  allocation_id = aws_eip.kenya_nat_eip.id
  subnet_id     = aws_subnet.kenya_public_subnets[0].id
  
  tags = {
    Name = "${var.project_name}-kenya-nat"
  }
}

# Route Table for Private Subnets (Kenya)
resource "aws_route_table" "kenya_private_rt" {
  provider = aws.kenya
  
  vpc_id = aws_vpc.kenya_vpc.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.kenya_nat.id
  }
  
  tags = {
    Name = "${var.project_name}-kenya-private-rt"
  }
}

# Route Table Associations for Private Subnets (Kenya)
resource "aws_route_table_association" "kenya_private_rta" {
  provider = aws.kenya
  
  count = length(aws_subnet.kenya_private_subnets)
  
  subnet_id      = aws_subnet.kenya_private_subnets[count.index].id
  route_table_id = aws_route_table.kenya_private_rt.id
}

# Security Group for ECS Services (Kenya)
resource "aws_security_group" "kenya_ecs_sg" {
  provider = aws.kenya
  
  name_prefix = "${var.project_name}-kenya-ecs-"
  vpc_id      = aws_vpc.kenya_vpc.id
  
  # HTTP traffic from ALB
  ingress {
    from_port       = 8000
    to_port         = 8007
    protocol        = "tcp"
    security_groups = [aws_security_group.kenya_alb_sg.id]
  }
  
  # HTTPS traffic from ALB
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.kenya_alb_sg.id]
  }
  
  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-kenya-ecs-sg"
  }
}

# Security Group for ALB (Kenya)
resource "aws_security_group" "kenya_alb_sg" {
  provider = aws.kenya
  
  name_prefix = "${var.project_name}-kenya-alb-"
  vpc_id      = aws_vpc.kenya_vpc.id
  
  # HTTP traffic from internet
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS traffic from internet
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-kenya-alb-sg"
  }
}

# Security Group for RDS (Kenya)
resource "aws_security_group" "kenya_rds_sg" {
  provider = aws.kenya
  
  name_prefix = "${var.project_name}-kenya-rds-"
  vpc_id      = aws_vpc.kenya_vpc.id
  
  # PostgreSQL traffic from ECS
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.kenya_ecs_sg.id]
  }
  
  tags = {
    Name = "${var.project_name}-kenya-rds-sg"
  }
}

# Security Group for ElastiCache (Kenya)
resource "aws_security_group" "kenya_redis_sg" {
  provider = aws.kenya
  
  name_prefix = "${var.project_name}-kenya-redis-"
  vpc_id      = aws_vpc.kenya_vpc.id
  
  # Redis traffic from ECS
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.kenya_ecs_sg.id]
  }
  
  tags = {
    Name = "${var.project_name}-kenya-redis-sg"
  }
}

# ECS Cluster (Kenya)
resource "aws_ecs_cluster" "kenya_cluster" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "${var.project_name}-kenya-cluster"
  }
}

# ECS Cluster Capacity Providers (Kenya)
resource "aws_ecs_cluster_capacity_providers" "kenya_cluster" {
  provider = aws.kenya
  
  cluster_name       = aws_ecs_cluster.kenya_cluster.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# Application Load Balancer (Kenya)
resource "aws_lb" "kenya_alb" {
  provider = aws.kenya
  
  name               = "${var.project_name}-kenya-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.kenya_alb_sg.id]
  subnets            = aws_subnet.kenya_public_subnets[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Name = "${var.project_name}-kenya-alb"
  }
}

# Target Group for API Gateway (Kenya)
resource "aws_lb_target_group" "kenya_api_gateway_tg" {
  provider = aws.kenya
  
  name     = "${var.project_name}-kenya-api-gateway-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.kenya_vpc.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Name = "${var.project_name}-kenya-api-gateway-tg"
  }
}

# ALB Listener (Kenya)
resource "aws_lb_listener" "kenya_alb_listener" {
  provider = aws.kenya
  
  load_balancer_arn = aws_lb.kenya_alb.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kenya_api_gateway_tg.arn
  }
}

# RDS Subnet Group (Kenya)
resource "aws_db_subnet_group" "kenya_rds_subnet_group" {
  provider = aws.kenya
  
  name       = "${var.project_name}-kenya-rds-subnet-group"
  subnet_ids = aws_subnet.kenya_private_subnets[*].id
  
  tags = {
    Name = "${var.project_name}-kenya-rds-subnet-group"
  }
}

# RDS Instance (Kenya)
resource "aws_db_instance" "kenya_rds" {
  provider = aws.kenya
  
  identifier = "${var.project_name}-kenya-rds"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = "mental_health"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.kenya_rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.kenya_rds_subnet_group.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  deletion_protection = false
  
  tags = {
    Name = "${var.project_name}-kenya-rds"
  }
}

# ElastiCache Subnet Group (Kenya)
resource "aws_elasticache_subnet_group" "kenya_redis_subnet_group" {
  provider = aws.kenya
  
  name       = "${var.project_name}-kenya-redis-subnet-group"
  subnet_ids = aws_subnet.kenya_private_subnets[*].id
}

# ElastiCache Redis Cluster (Kenya)
resource "aws_elasticache_replication_group" "kenya_redis" {
  provider = aws.kenya
  
  replication_group_id       = "${var.project_name}-kenya-redis"
  description                = "Redis cluster for ${var.project_name} in Kenya"
  
  node_type            = "cache.t3.micro"
  port                 = 6379
  parameter_group_name = "default.redis7"
  
  num_cache_clusters = 1
  
  subnet_group_name  = aws_elasticache_subnet_group.kenya_redis_subnet_group.name
  security_group_ids = [aws_security_group.kenya_redis_sg.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "${var.project_name}-kenya-redis"
  }
}

# S3 Bucket for Audio Storage (Kenya)
resource "aws_s3_bucket" "kenya_audio_storage" {
  provider = aws.kenya
  
  bucket = "${var.project_name}-kenya-audio-storage-${var.environment}"
  
  tags = {
    Name = "${var.project_name}-kenya-audio-storage"
  }
}

# S3 Bucket Versioning (Kenya)
resource "aws_s3_bucket_versioning" "kenya_audio_storage_versioning" {
  provider = aws.kenya
  
  bucket = aws_s3_bucket.kenya_audio_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Encryption (Kenya)
resource "aws_s3_bucket_server_side_encryption_configuration" "kenya_audio_storage_encryption" {
  provider = aws.kenya
  
  bucket = aws_s3_bucket.kenya_audio_storage.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block (Kenya)
resource "aws_s3_bucket_public_access_block" "kenya_audio_storage_pab" {
  provider = aws.kenya
  
  bucket = aws_s3_bucket.kenya_audio_storage.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudWatch Log Group (Kenya)
resource "aws_cloudwatch_log_group" "kenya_app_logs" {
  provider = aws.kenya
  
  name              = "/aws/ecs/${var.project_name}-kenya"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-kenya-app-logs"
  }
}

# IAM Role for ECS Task Execution (Kenya)
resource "aws_iam_role" "kenya_ecs_task_execution_role" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-ecs-task-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Role Policy for ECS Task Execution (Kenya)
resource "aws_iam_role_policy_attachment" "kenya_ecs_task_execution_role_policy" {
  provider = aws.kenya
  
  role       = aws_iam_role.kenya_ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Task (Kenya)
resource "aws_iam_role" "kenya_ecs_task_role" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for ECS Task (Kenya)
resource "aws_iam_role_policy" "kenya_ecs_task_policy" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-ecs-task-policy"
  role = aws_iam_role.kenya_ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.kenya_audio_storage.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.kenya_app_logs.arn}:*"
      }
    ]
  })
}

# Sensitive variables are defined in variables.tf

# Outputs
output "kenya_alb_dns_name" {
  description = "DNS name of the Kenya ALB"
  value       = aws_lb.kenya_alb.dns_name
}

output "kenya_rds_endpoint" {
  description = "RDS endpoint for Kenya"
  value       = aws_db_instance.kenya_rds.endpoint
  sensitive   = true
}

output "kenya_redis_endpoint" {
  description = "Redis endpoint for Kenya"
  value       = aws_elasticache_replication_group.kenya_redis.primary_endpoint_address
  sensitive   = true
}

output "kenya_s3_bucket_name" {
  description = "S3 bucket name for Kenya audio storage"
  value       = aws_s3_bucket.kenya_audio_storage.bucket
}
