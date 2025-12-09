<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git">
    <img src="docs/images/cli.png" alt="Logo" width="466" height="262">
  </a>

<h3 align="center">Polymarket Agents</h3>

  <p align="center">
    Trade autonomously on Polymarket using AI Agents
    <br />
    <a href="https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git">View Demo</a>
    ·
    <a href="https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>


<!-- CONTENT -->
# Polymarket Agents

> 🤖 **AI-powered autonomous trading agents for Polymarket prediction markets**

Polymarket Agents is a modern, open-source framework for building sophisticated AI trading agents on Polymarket. Leverage state-of-the-art LLMs, RAG (Retrieval-Augmented Generation), and superforecasting methodologies to create intelligent trading systems that analyze markets, events, and news to make informed predictions.

**Built with Python 3.12+** | **MIT Licensed** | **Production Ready**

This code is free and publicly available under MIT License open source license ([terms of service](#terms-of-service))!

## Features

- **AI-Powered Trading**: Autonomous trading agents using state-of-the-art LLMs
- **Polymarket Integration**: Full API integration for markets, events, and trading
- **RAG Support**: Local and remote RAG (Retrieval-Augmented Generation) for market analysis
- **Data Sources**: Integration with news providers, web search, and betting services
- **Superforecasting**: Advanced prediction capabilities using superforecaster methodologies
- **Trending Markets**: Get trending markets sorted by 24-hour volume
- **Modern Stack**: Built with Python 3.12+, LangChain, FastAPI, and modern tooling
- **Docker Ready**: Containerized deployment for easy setup

# Getting started

This project requires **Python 3.12+**.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- (Optional) Docker for containerized deployment
- (Optional) NewsAPI key for news integration
- (Optional) Tavily API key for web search

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git
   cd poly-ai-trading-agent
   ```

2. **Create a virtual environment**

   Using `venv` (recommended):
   
   ```bash
   python -m venv .venv
   ```
   
   Or using `uv` (faster):
   
   ```bash
   uv venv
   ```

3. **Activate the virtual environment**

   - On Windows (PowerShell):
   
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   
   - On Windows (CMD):
   
   ```cmd
   .venv\Scripts\activate.bat
   ```
   
   - On macOS and Linux:
   
   ```bash
   source .venv/bin/activate
   ```

4. **Install the project**

   Using pip:
   
   ```bash
   pip install -e .
   ```
   
   Or with development dependencies:
   
   ```bash
   pip install -e ".[dev]"
   ```
   
   Using uv (faster):
   
   ```bash
   uv pip install -e ".[dev]"
   ```

5. **Set up environment variables**

   Create a `.env` file in the project root:
   
   ```bash
   # Copy example if available, or create new
   touch .env
   ```
   
   Add the following environment variables:
   
   ```env
   # Required for trading
   POLYGON_WALLET_PRIVATE_KEY="your_private_key_here"
   
   # Required for AI features
   OPENAI_API_KEY="your_openai_api_key_here"
   
   # Optional - for news integration
   NEWSAPI_API_KEY="your_newsapi_key_here"
   
   # Optional - for web search
   TAVILY_API_KEY="your_tavily_key_here"
   ```

   **Important Notes:**
   - Never commit your `.env` file to version control
   - Keep your `POLYGON_WALLET_PRIVATE_KEY` secure and never share it
   - You can get a NewsAPI key from [newsapi.org](https://newsapi.org/)
   - You can get a Tavily key from [tavily.com](https://tavily.com/)

6. **Load your wallet with USDC** (if trading)
   
   Before executing trades, ensure your Polygon wallet has sufficient USDC balance for trading.

## Usage

### Command Line Interface

The CLI is the primary interface for interacting with Polymarket. All commands follow this format:

```bash
python -m scripts.python.cli <command-name> [options]
```

#### Getting Help

To see all available commands:

```bash
python -m scripts.python.cli --help
```

To get help for a specific command:

```bash
python -m scripts.python.cli <command-name> --help
```

### Detailed Command Reference

#### 1. Get All Markets

Retrieve and display markets from Polymarket.

**Command:**
```bash
python -m scripts.python.cli get-all-markets [--limit LIMIT] [--sort-by SORT_BY]
```

**Parameters:**
- `--limit` (optional): Number of markets to retrieve (default: 5)
- `--sort-by` (optional): Sorting criterion (default: "spread")

**Examples:**

```bash
# Get 10 markets sorted by spread
python -m scripts.python.cli get-all-markets --limit 10 --sort-by spread

# Get 5 markets (default)
python -m scripts.python.cli get-all-markets

# Get 20 markets
python -m scripts.python.cli get-all-markets --limit 20
```

**Output:** Displays a list of markets with details including:
- Market ID
- Question/Title
- Description
- Active status
- Spread
- Outcomes
- Outcome prices

#### 2. Get Trending Markets

Get trending markets sorted by 24-hour volume. This is useful for finding the most active markets.

**Command:**
```bash
python -m scripts.python.cli get-trending-markets [--limit LIMIT]
```

**Parameters:**
- `--limit` (optional): Number of trending markets to retrieve (default: 10)

**Examples:**

```bash
# Get top 10 trending markets
python -m scripts.python.cli get-trending-markets

# Get top 25 trending markets
python -m scripts.python.cli get-trending-markets --limit 25

# Get top 5 trending markets
python -m scripts.python.cli get-trending-markets --limit 5
```

**Output:** Displays trending markets sorted by 24-hour volume, showing the most active markets first.

#### 3. Get All Events

Retrieve and display events from Polymarket.

**Command:**
```bash
python -m scripts.python.cli get-all-events [--limit LIMIT] [--sort-by SORT_BY]
```

**Parameters:**
- `--limit` (optional): Number of events to retrieve (default: 5)
- `--sort-by` (optional): Sorting criterion (default: "number_of_markets")

**Examples:**

```bash
# Get 10 events sorted by number of markets
python -m scripts.python.cli get-all-events --limit 10 --sort-by number_of_markets

# Get 5 events (default)
python -m scripts.python.cli get-all-events
```

**Output:** Displays events with details including:
- Event ID
- Title
- Description
- Active status
- Number of associated markets
- End date

#### 4. Get Relevant News

Search for news articles related to specific keywords. Requires NewsAPI key.

**Command:**
```bash
python -m scripts.python.cli get-relevant-news <keywords>
```

**Parameters:**
- `keywords` (required): Comma-separated keywords to search for

**Examples:**

```bash
# Search for news about Bitcoin
python -m scripts.python.cli get-relevant-news "Bitcoin,crypto"

# Search for news about elections
python -m scripts.python.cli get-relevant-news "election,president"

# Search for multiple keywords
python -m scripts.python.cli get-relevant-news "AI,technology,machine learning"
```

**Output:** Displays news articles with:
- Title
- Description
- Source
- URL
- Published date

#### 5. Ask LLM

Query the LLM with any question. Useful for getting AI-powered insights.

**Command:**
```bash
python -m scripts.python.cli ask-llm "<your question>"
```

**Parameters:**
- `user_input` (required): Your question or prompt

**Examples:**

```bash
# Ask about trading strategies
python -m scripts.python.cli ask-llm "What are the best markets to trade?"

# Ask for market analysis
python -m scripts.python.cli ask-llm "Should I invest in prediction markets?"

# Ask for general questions
python -m scripts.python.cli ask-llm "Explain how prediction markets work"
```

**Output:** Returns AI-generated response based on your question.

#### 6. Ask Polymarket LLM

Query the LLM with context about current Polymarket markets and events. This provides more relevant answers based on actual market data.

**Command:**
```bash
python -m scripts.python.cli ask-polymarket-llm "<your question>"
```

**Parameters:**
- `user_input` (required): Your question about Polymarket

**Examples:**

```bash
# Ask about current markets
python -m scripts.python.cli ask-polymarket-llm "What types of markets are currently trending?"

# Ask for trading recommendations
python -m scripts.python.cli ask-polymarket-llm "Which markets should I focus on for trading?"

# Ask about market opportunities
python -m scripts.python.cli ask-polymarket-llm "What are the best opportunities right now?"
```

**Output:** Returns AI-generated response with context from current Polymarket data.

#### 7. Ask Superforecaster

Get superforecaster predictions for specific events and outcomes. Uses advanced prediction methodologies.

**Command:**
```bash
python -m scripts.python.cli ask-superforecaster <event_title> <market_question> <outcome>
```

**Parameters:**
- `event_title` (required): Title of the event
- `market_question` (required): The market question
- `outcome` (required): The outcome to predict

**Examples:**

```bash
# Get prediction for a specific outcome
python -m scripts.python.cli ask-superforecaster "2024 US Election" "Who will win?" "Candidate A"

# Get prediction for another market
python -m scripts.python.cli ask-superforecaster "Bitcoin Price" "Will Bitcoin reach $100k?" "Yes"
```

**Output:** Returns superforecaster analysis and prediction probability.

#### 8. Create Market

Generate a market idea using AI. The system analyzes current events and markets to suggest new market opportunities.

**Command:**
```bash
python -m scripts.python.cli create-market
```

**Examples:**

```bash
# Generate a market idea
python -m scripts.python.cli create-market
```

**Output:** Displays a generated market description with details about the proposed market.

#### 9. Create Local Markets RAG

Create a local RAG (Retrieval-Augmented Generation) database for markets. This allows for faster local queries.

**Command:**
```bash
python -m scripts.python.cli create-local-markets-rag <local_directory>
```

**Parameters:**
- `local_directory` (required): Directory path where the RAG database will be stored

**Examples:**

```bash
# Create RAG database in ./rag_db directory
python -m scripts.python.cli create-local-markets-rag ./rag_db

# Create RAG database in a specific path
python -m scripts.python.cli create-local-markets-rag /path/to/rag/database
```

**Output:** Creates a local vector database for faster market queries.

#### 10. Query Local Markets RAG

Query your local RAG database for market information.

**Command:**
```bash
python -m scripts.python.cli query-local-markets-rag <vector_db_directory> "<query>"
```

**Parameters:**
- `vector_db_directory` (required): Path to your RAG database directory
- `query` (required): Your search query

**Examples:**

```bash
# Query the local RAG database
python -m scripts.python.cli query-local-markets-rag ./rag_db "What are the best markets for trading?"

# Search for specific topics
python -m scripts.python.cli query-local-markets-rag ./rag_db "crypto markets"
```

**Output:** Returns relevant market information from your local database.

#### 11. Run Autonomous Trader

⚠️ **WARNING**: This command executes real trades. Review Terms of Service before use.

Run an autonomous trading agent that analyzes markets and executes trades automatically.

**Command:**
```bash
python -m scripts.python.cli run-autonomous-trader
```

**Examples:**

```bash
# Run the autonomous trader
python -m scripts.python.cli run-autonomous-trader
```

**Important Notes:**
- This will execute real trades on Polymarket
- Ensure you have sufficient USDC balance
- Review the Terms of Service at https://polymarket.com/tos
- Start with small amounts to test
- Monitor the trades closely

**Output:** The trader will:
1. Fetch all tradeable events
2. Filter events using RAG
3. Map events to markets
4. Filter markets
5. Calculate the best trade
6. Execute the trade (if enabled)

### Direct Script Execution

You can also run the trading script directly without the CLI:

```bash
python -m agents.application.trade
```

This will execute the `one_best_trade()` method directly.

### Docker Deployment

Build and run with Docker for easy deployment:

**Build the image:**
```bash
docker build -t poly-ai-trading-agent .
```

**Run the container:**
```bash
docker run --env-file .env poly-ai-trading-agent
```

**Or use the provided scripts:**

On Linux/macOS:
```bash
./scripts/bash/build-docker.sh
./scripts/bash/run-docker-dev.sh
```

On Windows (PowerShell):
```powershell
.\scripts\bash\build-docker.sh
.\scripts\bash\run-docker-dev.sh
```

### Usage Examples and Workflows

#### Example 1: Research Trending Markets

```bash
# Step 1: Get trending markets
python -m scripts.python.cli get-trending-markets --limit 20

# Step 2: Get news about specific topics
python -m scripts.python.cli get-relevant-news "Bitcoin,crypto,blockchain"

# Step 3: Ask AI for analysis
python -m scripts.python.cli ask-polymarket-llm "What are the best crypto markets to trade right now?"
```

#### Example 2: Create a Local RAG Database

```bash
# Step 1: Create the RAG database
python -m scripts.python.cli create-local-markets-rag ./my_rag_db

# Step 2: Query the database
python -m scripts.python.cli query-local-markets-rag ./my_rag_db "What markets are related to technology?"
```

#### Example 3: Get Market Analysis

```bash
# Step 1: Get all markets
python -m scripts.python.cli get-all-markets --limit 10

# Step 2: Get events
python -m scripts.python.cli get-all-events --limit 5

# Step 3: Ask for superforecaster prediction
python -m scripts.python.cli ask-superforecaster "2024 Election" "Who will win?" "Candidate A"
```

## Development

### Code Quality

This project uses modern Python tooling:

- **Ruff** - Fast Python linter and formatter
- **mypy** - Static type checking
- **pre-commit** - Git hooks for code quality

**Set up pre-commit hooks:**
```bash
pre-commit install
```

**Run linting and type checking:**
```bash
ruff check .
ruff format .
mypy .
```

### Testing

Run tests:
```bash
pytest
```

## Architecture

The Polymarket Agents architecture features modular components that can be maintained and extended by individual community members.

### APIs

Polymarket Agents connectors standardize data sources and order types.

- **`Chroma.py`**: Chroma DB for vectorizing news sources and other API data. Developers are able to add their own vector database implementations.

- **`Gamma.py`**: Defines `GammaMarketClient` class, which interfaces with the Polymarket Gamma API to fetch and parse market and event metadata. Methods to retrieve current and tradable markets, as well as defined information on specific markets and events.

- **`Polymarket.py`**: Defines a Polymarket class that interacts with the Polymarket API to retrieve and manage market and event data, and to execute orders on the Polymarket DEX. It includes methods for API key initialization, market and event data retrieval, and trade execution. The file also provides utility functions for building and signing orders, as well as examples for testing API interactions.

- **`Objects.py`**: Data models using Pydantic; representations for trades, markets, events, and related entities.

### Scripts

Files for managing your local environment, server set-up to run the application remotely, and CLI for end-user commands.

**`cli.py`** is the primary user interface for the repo. Users can run various commands to interact with the Polymarket API, retrieve relevant news articles, query local data, send data/prompts to LLMs, and execute trades in Polymarkets.

Commands follow this format:
```bash
python -m scripts.python.cli <command_name> [options]
```

## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

### Code Quality

Before making contributions, please:

1. Install development dependencies: `pip install -e ".[dev]"`
2. Set up pre-commit hooks: `pre-commit install`
3. Run linting: `ruff check . && ruff format .`
4. Run type checking: `mypy .`

## Prediction Markets Reading

- Prediction Markets: Bottlenecks and the Next Major Unlocks, Mikey 0x: https://mirror.xyz/1kx.eth/jnQhA56Kx9p3RODKiGzqzHGGEODpbskivUUNdd7hwh0
- The promise and challenges of crypto + AI applications, Vitalik Buterin: https://vitalik.eth.limo/general/2024/01/30/cryptoai.html
- Superforecasting: How to Upgrade Your Company's Judgement, Schoemaker and Tetlock: https://hbr.org/2016/05/superforecasting-how-to-upgrade-your-companys-judgment

## Contact

For questions, support, or inquiries:

- **Twitter/X**: [@blacksky_jose](https://x.com/blacksky_jose)
- **Telegram**: [@blacksky_jose](https://t.me/blacksky_jose)
- **GitHub Issues**: [Open an issue](https://github.com/BlackSky-Jose/PolyMarket-AI-agent-trading.git/issues)

Enjoy using the CLI application! If you encounter any issues, feel free to open an issue on the repository or reach out through the contact channels above.

**Important Legal Notice**: Before using this software for trading, please review and comply with:
- Polymarket Terms of Service
- Your local jurisdiction's regulations regarding prediction markets
- Cryptocurrency trading regulations in your area

The developers of this software are not responsible for any losses incurred through the use of this trading agent. Use at your own risk.
