# ECS Task Definitions for all microservices

# Task execution role (already defined in main.tf, but adding policy for ECR)
resource "aws_iam_role_policy" "kenya_ecs_task_execution_ecr" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-ecs-task-execution-ecr"
  role = aws_iam_role.kenya_ecs_task_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Task definition for API Gateway
resource "aws_ecs_task_definition" "kenya_api_gateway" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-api-gateway"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "api-gateway"
    image = "${var.container_registry}/${var.project_name}/api-gateway:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    secrets = [
      { name = "JWT_SECRET_KEY", valueFrom = aws_secretsmanager_secret.jwt_secret.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "api-gateway"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-api-gateway-task"
  }
}

# Task definition for Speech Processing
resource "aws_ecs_task_definition" "kenya_speech_processing" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-speech-processing"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "speech-processing"
    image = "${var.container_registry}/${var.project_name}/speech-processing:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment },
      { name = "AZURE_SPEECH_REGION", value = "eastus" }
    ]
    
    secrets = [
      { name = "OPENAI_API_KEY", valueFrom = aws_secretsmanager_secret.openai_api_key.arn },
      { name = "AZURE_SPEECH_KEY", valueFrom = aws_secretsmanager_secret.azure_speech_key.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "speech-processing"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-speech-processing-task"
  }
}

# Task definition for Emotion Analysis
resource "aws_ecs_task_definition" "kenya_emotion_analysis" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-emotion-analysis"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "emotion-analysis"
    image = "${var.container_registry}/${var.project_name}/emotion-analysis:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    secrets = [
      { name = "HUME_API_KEY", valueFrom = aws_secretsmanager_secret.hume_api_key.arn },
      { name = "AZURE_TEXT_ANALYTICS_KEY", valueFrom = aws_secretsmanager_secret.azure_text_analytics_key.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "emotion-analysis"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-emotion-analysis-task"
  }
}

# Task definition for Conversation Engine
resource "aws_ecs_task_definition" "kenya_conversation_engine" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-conversation-engine"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "conversation-engine"
    image = "${var.container_registry}/${var.project_name}/conversation-engine:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    secrets = [
      { name = "OPENAI_API_KEY", valueFrom = aws_secretsmanager_secret.openai_api_key.arn },
      { name = "PINECONE_API_KEY", valueFrom = aws_secretsmanager_secret.pinecone_api_key.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "conversation-engine"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-conversation-engine-task"
  }
}

# Task definition for Crisis Detection
resource "aws_ecs_task_definition" "kenya_crisis_detection" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-crisis-detection"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "crisis-detection"
    image = "${var.container_registry}/${var.project_name}/crisis-detection:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    secrets = [
      { name = "TWILIO_ACCOUNT_SID", valueFrom = aws_secretsmanager_secret.twilio_account_sid.arn },
      { name = "TWILIO_AUTH_TOKEN", valueFrom = aws_secretsmanager_secret.twilio_auth_token.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "crisis-detection"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-crisis-detection-task"
  }
}

# Task definition for Safety Moderation
resource "aws_ecs_task_definition" "kenya_safety_moderation" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-safety-moderation"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "safety-moderation"
    image = "${var.container_registry}/${var.project_name}/safety-moderation:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "safety-moderation"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-safety-moderation-task"
  }
}

# Task definition for Sync Service
resource "aws_ecs_task_definition" "kenya_sync_service" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-sync-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "sync-service"
    image = "${var.container_registry}/${var.project_name}/sync-service:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "CELERY_BROKER_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379/0" },
      { name = "CELERY_RESULT_BACKEND", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379/0" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "sync-service"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-sync-service-task"
  }
}

# Task definition for Cultural Context
resource "aws_ecs_task_definition" "kenya_cultural_context" {
  provider = aws.kenya
  
  family                   = "${var.project_name}-kenya-cultural-context"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.kenya_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.kenya_ecs_task_role.arn
  
  container_definitions = jsonencode([{
    name  = "cultural-context"
    image = "${var.container_registry}/${var.project_name}/cultural-context:${var.container_image_tag}"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "DATABASE_URL", value = "postgresql://postgres:${var.db_password}@${aws_db_instance.kenya_rds.endpoint}/mental_health" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.kenya_redis.primary_endpoint_address}:6379" },
      { name = "ENVIRONMENT", value = var.environment }
    ]
    
    secrets = [
      { name = "PINECONE_API_KEY", valueFrom = aws_secretsmanager_secret.pinecone_api_key.arn }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.kenya_app_logs.name
        "awslogs-region"         = "af-south-1"
        "awslogs-stream-prefix"  = "cultural-context"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
  
  tags = {
    Name = "${var.project_name}-kenya-cultural-context-task"
  }
}

