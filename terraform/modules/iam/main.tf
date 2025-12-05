############################################
# Lambda Execution Role
############################################
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-shared-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

############################################
# CloudWatch Logs Permissions (required)
############################################
resource "aws_iam_role_policy" "lambda_logs" {
  name = "lambda-logs-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

############################################
# S3 Write Permissions (your buckets)
############################################
resource "aws_iam_role_policy" "lambda_s3_write" {
  name = "lambda-s3-write-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject"
        ],
        Resource = [
          "${var.grant_bucket_arn}/*",
          "${var.linking_bucket_arn}/*"
        ]
      }
    ]
  })
}

############################################
# SQS Permissions (required for event source mapping)
############################################
resource "aws_iam_role_policy" "lambda_sqs" {
  name = "lambda-sqs-permissions"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ],
        Resource = var.sqs_queue_arn
      }
    ]
  })
}
