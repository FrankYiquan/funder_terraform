data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = var.layer_source_dir
  output_path = "${path.module}/layer.zip"
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = var.layer_name
  filename            = data.archive_file.layer_zip.output_path
  compatible_runtimes = ["python3.11"]
}
