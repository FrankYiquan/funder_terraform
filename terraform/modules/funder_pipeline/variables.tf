variable "name"                 { type = string }
variable "lambda_source_dir"    { type = string }
variable "handler"              { type = string }
variable "layers"               { type = list(string) }
variable "lambda_role_arn"      { type = string }
variable "grant_bucket_name"    { type = string }
variable "linking_bucket_name"  { type = string }
