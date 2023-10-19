from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    S3_BUCKET_NAME: str


s3_settings = S3Settings()
