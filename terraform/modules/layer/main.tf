data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = var.layer_source_dir
  output_path = "${path.module}/${var.layer_name}.zip"
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = var.layer_name
  filename            = data.archive_file.layer_zip.output_path
  source_code_hash    = data.archive_file.layer_zip.output_base64sha256
  compatible_runtimes = ["python3.11"]
}
