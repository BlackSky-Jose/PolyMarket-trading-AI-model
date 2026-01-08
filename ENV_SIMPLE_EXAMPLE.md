# Simplest .env File Example

## Minimal Required Configuration

Create a file named `.env` in the project root with at least these two variables:

```env
POLYGON_WALLET_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef12345678
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Complete Example

For full functionality, use this:

```env
# Required for trading
POLYGON_WALLET_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef12345678

# Required for AI features
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - MongoDB (history storage)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=polymarket_agent

# Optional - News API
NEWSAPI_API_KEY=your_newsapi_key_here

# Optional - Tavily Search
TAVILY_API_KEY=your_tavily_key_here
```

## Quick Setup

1. Copy the minimal example above
2. Replace `0x1234567890abcdef1234567890abcdef12345678` with your actual Polygon wallet private key
3. Replace `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual OpenAI API key
4. Save as `.env` in the project root

## Notes

- **POLYGON_WALLET_PRIVATE_KEY**: Your Polygon wallet private key (starts with `0x`)
- **OPENAI_API_KEY**: Your OpenAI API key (starts with `sk-`)
- The private key will be automatically saved to MongoDB when the project runs
- MongoDB connection URL is encoded in the code (no need to set it manually for private key storage)
