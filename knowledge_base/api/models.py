from django.db import models

class AIConfig(models.Model):
    text_generation_provider = models.CharField(max_length=50, default='openai')
    text_generation_api_key = models.CharField(max_length=255, blank=True, null=True)
    text_generation_base_url = models.CharField(max_length=255, default='https://api.openai.com/v1')
    text_generation_model_name = models.CharField(max_length=100, default='gpt-4o')
    text_generation_temperature = models.FloatField(default=0.7)
    
    embedding_provider = models.CharField(max_length=50, default='openai')
    embedding_api_key = models.CharField(max_length=255, blank=True, null=True)
    embedding_base_url = models.CharField(max_length=255, default='https://api.openai.com/v1')
    embedding_model_name = models.CharField(max_length=100, default='text-embedding-3-large')
    embedding_dimension = models.IntegerField(default=1024)
    
    rerank_provider = models.CharField(max_length=50, default='cohere')
    rerank_api_key = models.CharField(max_length=255, blank=True, null=True)
    rerank_base_url = models.CharField(max_length=255, default='https://api.cohere.com/v1')
    rerank_model_name = models.CharField(max_length=100, default='rerank-english-v3.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return 'AI Configuration'
