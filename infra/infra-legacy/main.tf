############################################################
# Legacy infra main.tf (archived)
############################################################

resource "aws_s3_bucket" "assets" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_acl" "assets_acl" {
  bucket = aws_s3_bucket.assets.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets_encryption" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "assets_block" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "assets_versioning" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "assets_lifecycle" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id      = "expire-temp-uploads"
    status  = "Enabled"

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

resource "aws_dynamodb_table" "app_table" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
  attribute {
    name = "entity_type"
    type = "S"
  }
  attribute {
    name = "topic_id"
    type = "S"
  }
  attribute {
    name = "created_at"
    type = "S"
  }

  global_secondary_index {
    name               = "gsi1-entity-type-created-at"
    hash_key           = "entity_type"
    range_key          = "created_at"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "gsi2-topic-sortkey"
    hash_key           = "topic_id"
    range_key          = "SK"
    projection_type    = "ALL"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = null
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Environment = "production"
    Project     = "aplicacion-senas"
    ManagedBy   = "terraform"
  }
}

################################################
## Legacy IAM/Lambda/API definitions omitted for brevity
