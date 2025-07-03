# 🔧 Configuration Guide

## Overview

This guide covers all configuration options available in the Bitsy AI Assistant. Proper configuration ensures optimal performance and integration with your institution's specific needs.

![Configuration Overview - Add Screenshot Here]
_Screenshot Placeholder: Configuration dashboard or settings interface_

## Environment Configuration

### Creating Environment File

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=Bitsy - BITS College AI Assistant
COLLEGE_NAME=BITS College
BRAND_COLOR=#7EC143
DEBUG_MODE=false

# Database Configuration
DB_PATH=./data/chatbot.db
DB_BACKUP_ENABLED=true
DB_BACKUP_INTERVAL=24h

# NLP Model Settings
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_md
MODEL_CACHE_DIR=./models

# Similarity Thresholds
MATCH_THRESHOLD=0.45
SEMANTIC_WEIGHT=0.6
FUZZY_WEIGHT=0.25
OVERLAP_WEIGHT=0.15

# Audio Settings
TTS_LANGUAGE=en
TTS_SLOW=false
AUDIO_ENABLED=true
AUDIO_FORMAT=mp3

# UI Configuration
SIDEBAR_EXPANDED=true
THEME_MODE=auto
MAX_CHAT_HISTORY=100
ENABLE_BOOKMARKS=true

# Analytics Configuration
ANALYTICS_ENABLED=true
DASHBOARD_PORT=8502
METRICS_RETENTION_DAYS=365

# Performance Settings
MAX_CONCURRENT_USERS=50
CACHE_SIZE=1000
RESPONSE_TIMEOUT=30
```

![Environment File Example - Add Screenshot Here]
_Screenshot Placeholder: Environment file in code editor_

## NLP Configuration

### Model Selection

![Model Configuration - Add Screenshot Here]
_Screenshot Placeholder: Model selection interface or configuration_

#### Sentence Transformers Models

Choose based on your needs:

| Model                  | Size  | Performance | Use Case                 |
| ---------------------- | ----- | ----------- | ------------------------ |
| `all-MiniLM-L6-v2`     | 80MB  | Fast        | Production (Recommended) |
| `all-mpnet-base-v2`    | 420MB | Best        | High accuracy needed     |
| `all-distilroberta-v1` | 290MB | Balanced    | Multilingual support     |

```python
# In nlp_agent.py
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Change as needed
```

#### Spacy Models

```bash
# English models
python -m spacy download en_core_web_sm    # 13MB, basic
python -m spacy download en_core_web_md    # 40MB, recommended
python -m spacy download en_core_web_lg    # 560MB, best accuracy

# Other languages
python -m spacy download es_core_news_sm   # Spanish
python -m spacy download fr_core_news_sm   # French
```

### Similarity Tuning

![Similarity Tuning - Add Screenshot Here]
_Screenshot Placeholder: Similarity parameter adjustment interface_

Fine-tune these parameters based on your FAQ content:

```python
# Conservative (fewer false positives)
MATCH_THRESHOLD = 0.65
SEMANTIC_WEIGHT = 0.7
FUZZY_WEIGHT = 0.2
OVERLAP_WEIGHT = 0.1

# Aggressive (more responses, some false positives)
MATCH_THRESHOLD = 0.35
SEMANTIC_WEIGHT = 0.5
FUZZY_WEIGHT = 0.3
OVERLAP_WEIGHT = 0.2

# Balanced (recommended starting point)
MATCH_THRESHOLD = 0.45
SEMANTIC_WEIGHT = 0.6
FUZZY_WEIGHT = 0.25
OVERLAP_WEIGHT = 0.15
```

## FAQ Configuration

### Structure Guidelines

![FAQ Structure - Add Screenshot Here]
_Screenshot Placeholder: FAQ JSON structure with annotations_

```json
{
  "intent": "unique_identifier",
  "patterns": [
    "Primary way to ask the question",
    "Alternative phrasing",
    "Common misspelling: 'registrtion process'"
  ],
  "response": "Clear, concise answer with actionable information",
  "category": "academic|administrative|general",
  "confidence_boost": 0.1,
  "related_intents": ["related_intent_1", "related_intent_2"]
}
```

### Best Practices

![FAQ Best Practices - Add Screenshot Here]
_Screenshot Placeholder: FAQ editing interface with guidelines_

#### Pattern Writing

- Include 3-5 variations per intent
- Add common misspellings
- Use natural language
- Include domain-specific terms

#### Response Writing

- Keep responses under 200 words
- Include specific steps when applicable
- Provide contact information for complex issues
- Use consistent formatting

### Categories

Organize your FAQ by categories:

```json
{
  "categories": {
    "academic": {
      "color": "#007bff",
      "icon": "🎓",
      "description": "Course registration, grades, academic policies"
    },
    "administrative": {
      "color": "#28a745",
      "icon": "📋",
      "description": "Fees, transcripts, administrative procedures"
    },
    "campus_life": {
      "color": "#ffc107",
      "icon": "🏫",
      "description": "Housing, dining, campus facilities"
    }
  }
}
```

## UI Customization

### Branding

![Branding Configuration - Add Screenshot Here]
_Screenshot Placeholder: Branding customization interface_

#### Colors

```css
/* Primary brand color */
:root {
  --brand-primary: #7ec143;
  --brand-secondary: #5a9b32;
  --brand-accent: #4a7c28;
}

/* Custom color scheme */
:root {
  --brand-primary: #your-color;
  --brand-secondary: #your-secondary;
  --brand-accent: #your-accent;
}
```

#### Logo and Assets

```python
# In app.py
COLLEGE_LOGO = "assets/logo.png"
FAVICON = "assets/favicon.ico"
BACKGROUND_IMAGE = "assets/background.jpg"
```

### Layout Options

![Layout Configuration - Add Screenshot Here]
_Screenshot Placeholder: Layout options and customization panel_

```python
# Page configuration
st.set_page_config(
    page_title="Your College AI Assistant",
    page_icon="🎓",
    layout="wide",           # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)
```

### Chat Interface

```python
# Chat configuration
CHAT_CONFIG = {
    "max_messages": 100,
    "enable_audio": True,
    "enable_bookmarks": True,
    "show_timestamps": True,
    "enable_feedback": True,
    "auto_scroll": True
}
```

## Database Configuration

### SQLite Settings

![Database Configuration - Add Screenshot Here]
_Screenshot Placeholder: Database configuration and optimization settings_

```python
# Database configuration
DB_CONFIG = {
    "path": "./data/chatbot.db",
    "timeout": 30,
    "check_same_thread": False,
    "auto_vacuum": "FULL",
    "journal_mode": "WAL",
    "synchronous": "NORMAL"
}
```

### Backup Configuration

```python
# Automatic backup settings
BACKUP_CONFIG = {
    "enabled": True,
    "interval_hours": 24,
    "max_backups": 30,
    "compression": True,
    "backup_path": "./backups/"
}
```

### Performance Optimization

```sql
-- Add these indexes for better performance
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp
ON interactions(timestamp);

CREATE INDEX IF NOT EXISTS idx_interactions_session
ON interactions(session_id);

CREATE INDEX IF NOT EXISTS idx_interactions_score
ON interactions(match_score);
```

## Audio Configuration

### Text-to-Speech Settings

![Audio Configuration - Add Screenshot Here]
_Screenshot Placeholder: Audio settings interface_

```python
# gTTS configuration
TTS_CONFIG = {
    "language": "en",
    "slow": False,
    "lang_check": True,
    "pre_processor_funcs": [
        lambda text: text.replace("BITS", "Bits")
    ]
}

# Alternative TTS engines
ALTERNATIVE_TTS = {
    "engine": "pyttsx3",  # For offline TTS
    "voice_id": 0,
    "rate": 200,
    "volume": 0.9
}
```

### Audio Quality

```python
# Audio output settings
AUDIO_CONFIG = {
    "format": "mp3",
    "bitrate": 128,
    "sample_rate": 22050,
    "auto_play": False,
    "volume": 0.8
}
```

## Performance Configuration

### Caching

![Caching Configuration - Add Screenshot Here]
_Screenshot Placeholder: Cache settings and performance metrics_

```python
# Streamlit caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_faq():
    pass

@st.cache_resource  # Cache for session
def load_models():
    pass
```

### Memory Management

```python
# Memory optimization
MEMORY_CONFIG = {
    "max_cache_size": "1GB",
    "model_cache_size": "500MB",
    "clear_cache_interval": 3600,
    "garbage_collection": True
}
```

### Concurrent Users

```python
# Server configuration
SERVER_CONFIG = {
    "max_concurrent_users": 50,
    "request_timeout": 30,
    "keep_alive_timeout": 5,
    "max_request_size": 10  # MB
}
```

## Security Configuration

### Input Validation

![Security Configuration - Add Screenshot Here]
_Screenshot Placeholder: Security settings and validation rules_

```python
# Input sanitization
SECURITY_CONFIG = {
    "max_query_length": 500,
    "allowed_characters": r"[a-zA-Z0-9\s\?\!\.\,\-\']",
    "rate_limiting": {
        "requests_per_minute": 30,
        "requests_per_hour": 500
    },
    "blocked_patterns": [
        r"<script",
        r"javascript:",
        r"onload="
    ]
}
```

### Data Privacy

```python
# Privacy settings
PRIVACY_CONFIG = {
    "anonymize_logs": True,
    "hash_user_ids": True,
    "data_retention_days": 365,
    "encrypt_sensitive_data": True
}
```

## Monitoring Configuration

### Logging

![Logging Configuration - Add Screenshot Here]
_Screenshot Placeholder: Logging configuration interface_

```python
# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/chatbot.log",
    "max_size": "10MB",
    "backup_count": 5,
    "console_output": True
}
```

### Metrics Collection

```python
# Metrics configuration
METRICS_CONFIG = {
    "enabled": True,
    "endpoint": "/metrics",
    "collect_user_metrics": False,
    "performance_tracking": True,
    "error_tracking": True
}
```

## Integration Configuration

### External APIs

![API Integration - Add Screenshot Here]
_Screenshot Placeholder: API integration configuration panel_

```python
# External service integration
INTEGRATION_CONFIG = {
    "student_portal": {
        "enabled": False,
        "api_url": "https://portal.yourschool.edu/api",
        "api_key": "your-api-key",
        "timeout": 10
    },
    "email_system": {
        "enabled": False,
        "smtp_server": "smtp.yourschool.edu",
        "port": 587,
        "use_tls": True
    }
}
```

### Webhooks

```python
# Webhook configuration
WEBHOOK_CONFIG = {
    "escalation_webhook": {
        "url": "https://yourservice.com/escalation",
        "timeout": 5,
        "retry_attempts": 3
    },
    "analytics_webhook": {
        "url": "https://analytics.yourschool.edu/chatbot",
        "batch_size": 100,
        "interval_minutes": 15
    }
}
```

## Testing Configuration

### Test Settings

![Testing Configuration - Add Screenshot Here]
_Screenshot Placeholder: Test configuration and execution interface_

```python
# Test configuration
TEST_CONFIG = {
    "test_db_path": "./test/test_chatbot.db",
    "mock_models": True,
    "test_timeout": 30,
    "coverage_threshold": 80,
    "test_data_path": "./test/data/"
}
```

### Load Testing

```python
# Load test configuration
LOAD_TEST_CONFIG = {
    "concurrent_users": 50,
    "test_duration": 300,  # seconds
    "ramp_up_time": 60,
    "test_scenarios": [
        "basic_query",
        "complex_query",
        "escalation_scenario"
    ]
}
```

## Deployment Configuration

### Production Settings

![Production Configuration - Add Screenshot Here]
_Screenshot Placeholder: Production deployment configuration_

```python
# Production environment
PRODUCTION_CONFIG = {
    "debug": False,
    "host": "0.0.0.0",
    "port": 8501,
    "workers": 4,
    "worker_class": "uvicorn.workers.UvicornWorker",
    "max_requests": 1000,
    "max_requests_jitter": 100
}
```

### Docker Configuration

```dockerfile
# Production Dockerfile optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODEL_CACHE_DIR=/models
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

## Troubleshooting Configuration Issues

### Common Problems

![Troubleshooting Guide - Add Screenshot Here]
_Screenshot Placeholder: Troubleshooting interface with common issues_

1. **Models not loading**: Check internet connection and disk space
2. **Poor response quality**: Adjust similarity thresholds
3. **Slow performance**: Optimize caching and model size
4. **Database errors**: Check file permissions and disk space
5. **Memory issues**: Reduce cache sizes and model complexity
