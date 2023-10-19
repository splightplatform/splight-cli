from pydantic_settings import BaseSettings


class AWSConfig(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str


aws_config = AWSConfig()
