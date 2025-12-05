# DLQ
resource "aws_sqs_queue" "dlq" {
  name = "${var.name}-DLQ"
}

# SQS Queue
resource "aws_sqs_queue" "queue" {
  name = "${var.name}-Queue"

  visibility_timeout_seconds = 45
  message_retention_seconds  = 1800

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 2
  })
}

# Package Lambda Code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.lambda_source_dir
  output_path = "${path.module}/${var.name}.zip"
}

# Lambda Function
resource "aws_lambda_function" "lambda" {
  function_name = "${var.name}-Lambda"
  handler       = var.handler
  runtime       = "python3.11"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  layers = var.layers
  role   = var.lambda_role_arn

  environment {
    variables = {
      GRANT_BUCKET   = var.grant_bucket_name
      LINKING_BUCKET = var.linking_bucket_name
    }
  }

  timeout = 30
}

# SQS → Lambda
resource "aws_lambda_event_source_mapping" "mapping" {
  event_source_arn = aws_sqs_queue.queue.arn
  function_name    = aws_lambda_function.lambda.arn
  batch_size       = 1

  depends_on = [
    aws_lambda_function.lambda,
    aws_sqs_queue.queue,
    aws_sqs_queue.dlq
  ]
}

