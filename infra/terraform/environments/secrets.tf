# AWS Secrets Manager configuration for sensitive data

# JWT Secret Key
resource "aws_secretsmanager_secret" "jwt_secret" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-jwt-secret"
  description             = "JWT secret key for authentication"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-jwt-secret"
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret_key
}

# OpenAI API Key
resource "aws_secretsmanager_secret" "openai_api_key" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-openai-api-key"
  description             = "OpenAI API key"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-openai-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key != "" ? var.openai_api_key : "placeholder"
}

# Azure Speech Key
resource "aws_secretsmanager_secret" "azure_speech_key" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-azure-speech-key"
  description             = "Azure Speech Services API key"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-azure-speech-key"
  }
}

resource "aws_secretsmanager_secret_version" "azure_speech_key" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.azure_speech_key.id
  secret_string = var.azure_speech_key != "" ? var.azure_speech_key : "placeholder"
}

# Azure Text Analytics Key
resource "aws_secretsmanager_secret" "azure_text_analytics_key" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-azure-text-analytics-key"
  description             = "Azure Text Analytics API key"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-azure-text-analytics-key"
  }
}

resource "aws_secretsmanager_secret_version" "azure_text_analytics_key" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.azure_text_analytics_key.id
  secret_string = var.azure_speech_key != "" ? var.azure_speech_key : "placeholder"
}

# Hume AI API Key
resource "aws_secretsmanager_secret" "hume_api_key" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-hume-api-key"
  description             = "Hume AI API key"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-hume-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "hume_api_key" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.hume_api_key.id
  secret_string = var.hume_api_key != "" ? var.hume_api_key : "placeholder"
}

# Pinecone API Key
resource "aws_secretsmanager_secret" "pinecone_api_key" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-pinecone-api-key"
  description             = "Pinecone API key"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-pinecone-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "pinecone_api_key" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.pinecone_api_key.id
  secret_string = var.pinecone_api_key != "" ? var.pinecone_api_key : "placeholder"
}

# Twilio Account SID
resource "aws_secretsmanager_secret" "twilio_account_sid" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-twilio-account-sid"
  description             = "Twilio Account SID"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-twilio-account-sid"
  }
}

resource "aws_secretsmanager_secret_version" "twilio_account_sid" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.twilio_account_sid.id
  secret_string = var.twilio_account_sid != "" ? var.twilio_account_sid : "placeholder"
}

# Twilio Auth Token
resource "aws_secretsmanager_secret" "twilio_auth_token" {
  provider = aws.kenya
  
  name                    = "${var.project_name}-${var.environment}-twilio-auth-token"
  description             = "Twilio Auth Token"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-twilio-auth-token"
  }
}

resource "aws_secretsmanager_secret_version" "twilio_auth_token" {
  provider = aws.kenya
  
  secret_id     = aws_secretsmanager_secret.twilio_auth_token.id
  secret_string = var.twilio_auth_token != "" ? var.twilio_auth_token : "placeholder"
}

# IAM Policy for ECS tasks to read secrets
resource "aws_iam_role_policy" "kenya_ecs_task_secrets_policy" {
  provider = aws.kenya
  
  name = "${var.project_name}-kenya-ecs-task-secrets-policy"
  role = aws_iam_role.kenya_ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.jwt_secret.arn,
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.azure_speech_key.arn,
          aws_secretsmanager_secret.azure_text_analytics_key.arn,
          aws_secretsmanager_secret.hume_api_key.arn,
          aws_secretsmanager_secret.pinecone_api_key.arn,
          aws_secretsmanager_secret.twilio_account_sid.arn,
          aws_secretsmanager_secret.twilio_auth_token.arn
        ]
      }
    ]
  })
}

