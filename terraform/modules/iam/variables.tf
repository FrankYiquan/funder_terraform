variable "grant_bucket_arn" {
  type = string
}

variable "linking_bucket_arn" {
  type = string
}

variable "sqs_queue_arns" {
  type = list(string)
}
