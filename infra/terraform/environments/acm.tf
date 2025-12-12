# AWS Certificate Manager (ACM) for SSL certificates

# Request SSL certificate for domain
resource "aws_acm_certificate" "kenya_cert" {
  provider = aws.kenya
  
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  subject_alternative_names = [
    "*.${var.domain_name}"
  ]
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Name = "${var.project_name}-kenya-cert"
  }
}

# Certificate validation (requires DNS records to be added)
resource "aws_acm_certificate_validation" "kenya_cert" {
  provider = aws.kenya
  
  certificate_arn = aws_acm_certificate.kenya_cert.arn
  
  # Note: This requires DNS validation records to be added manually
  # or via Route53 if using AWS DNS
  # For now, this is commented out - uncomment after DNS validation
  # validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Output certificate ARN for use with ALB
output "kenya_certificate_arn" {
  description = "ARN of the SSL certificate"
  value       = aws_acm_certificate.kenya_cert.arn
}

