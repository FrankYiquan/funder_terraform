output "lambda_arn" {
  value = aws_lambda_function.lambda.arn
}

output "queue_arn" {
  value = aws_sqs_queue.queue.arn
}
