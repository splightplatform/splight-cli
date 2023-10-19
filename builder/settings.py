from pydantic_settings import BaseSettings


class AWSConfig(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str


aws_config = AWSConfig()
