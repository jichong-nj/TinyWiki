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
    embedding_input_type = models.CharField(max_length=20, default='query', choices=[('query', 'query'), ('document', 'document')])
    
    rerank_provider = models.CharField(max_length=50, default='cohere')
    rerank_api_key = models.CharField(max_length=255, blank=True, null=True)
    rerank_base_url = models.CharField(max_length=255, default='https://api.cohere.com/v1')
    rerank_model_name = models.CharField(max_length=100, default='rerank-english-v3.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return 'AI Configuration'
    
    def to_dict(self):
        return {
            'textGeneration': {
                'provider': self.text_generation_provider,
                'apiKey': self.text_generation_api_key or '',
                'baseUrl': self.text_generation_base_url,
                'modelName': self.text_generation_model_name,
                'temperature': self.text_generation_temperature
            },
            'embedding': {
                'provider': self.embedding_provider,
                'apiKey': self.embedding_api_key or '',
                'baseUrl': self.embedding_base_url,
                'modelName': self.embedding_model_name,
                'dimension': self.embedding_dimension,
                'inputType': self.embedding_input_type
            },
            'rerank': {
                'provider': self.rerank_provider,
                'apiKey': self.rerank_api_key or '',
                'baseUrl': self.rerank_base_url,
                'modelName': self.rerank_model_name
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        config = cls.objects.first() or cls()
        config.text_generation_provider = data.get('textGeneration', {}).get('provider', 'openai')
        config.text_generation_api_key = data.get('textGeneration', {}).get('apiKey')
        config.text_generation_base_url = data.get('textGeneration', {}).get('baseUrl', 'https://api.openai.com/v1')
        config.text_generation_model_name = data.get('textGeneration', {}).get('modelName', 'gpt-4o')
        config.text_generation_temperature = data.get('textGeneration', {}).get('temperature', 0.7)
        
        config.embedding_provider = data.get('embedding', {}).get('provider', 'openai')
        config.embedding_api_key = data.get('embedding', {}).get('apiKey')
        config.embedding_base_url = data.get('embedding', {}).get('baseUrl', 'https://api.openai.com/v1')
        config.embedding_model_name = data.get('embedding', {}).get('modelName', 'text-embedding-3-large')
        config.embedding_dimension = data.get('embedding', {}).get('dimension', 1024)
        config.embedding_input_type = data.get('embedding', {}).get('inputType', 'query')
        
        config.rerank_provider = data.get('rerank', {}).get('provider', 'cohere')
        config.rerank_api_key = data.get('rerank', {}).get('apiKey')
        config.rerank_base_url = data.get('rerank', {}).get('baseUrl', 'https://api.cohere.com/v1')
        config.rerank_model_name = data.get('rerank', {}).get('modelName', 'rerank-english-v3.0')
        
        return config
