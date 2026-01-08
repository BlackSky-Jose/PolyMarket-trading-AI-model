import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.pretty import pprint

from agents.polymarket.polymarket import Polymarket
from agents.connectors.chroma import PolymarketRAG
from agents.connectors.news import News
from agents.application.trade import Trader
from agents.application.executor import Executor
from agents.application.creator import Creator
from agents.utils.history import get_history_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = typer.Typer(help="Polymarket AI Trading Agent CLI")
console = Console()

# Initialize clients lazily to avoid import-time errors
_polymarket: Optional[Polymarket] = None
_newsapi_client: Optional[News] = None
_polymarket_rag: Optional[PolymarketRAG] = None


def get_polymarket() -> Polymarket:
    global _polymarket
    if _polymarket is None:
        _polymarket = Polymarket()
    return _polymarket


def get_news() -> News:
    global _newsapi_client
    if _newsapi_client is None:
        _newsapi_client = News()
    return _newsapi_client


def get_rag() -> PolymarketRAG:
    global _polymarket_rag
    if _polymarket_rag is None:
        _polymarket_rag = PolymarketRAG()
    return _polymarket_rag
@app.command()
def get_all_markets(limit: int = 5, sort_by: str = "spread") -> None:
    """
    Query Polymarket's markets
    """
    history = get_history_logger()
    console.print(f"[cyan]Fetching {limit} markets, sorted by {sort_by}[/cyan]")
    try:
        pm = get_polymarket()
        markets = pm.get_all_markets()
        markets = pm.filter_markets_for_trading(markets)
        if sort_by == "spread":
            markets = sorted(markets, key=lambda x: x.spread, reverse=True)
        markets = markets[:limit]
        console.print("[green]Markets:[/green]")
        pprint(markets)
        # Log to MongoDB
        history.log_market_query(
            query_type="get_all_markets",
            limit=limit,
            sort_by=sort_by,
            results_count=len(markets),
            markets=[m.dict() if hasattr(m, "dict") else str(m) for m in markets],
            success=True,
        )
        history.log_cli_command(
            command="get_all_markets",
            parameters={"limit": limit, "sort_by": sort_by},
            result={"markets_count": len(markets)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_market_query(
            query_type="get_all_markets",
            limit=limit,
            sort_by=sort_by,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="get_all_markets",
            parameters={"limit": limit, "sort_by": sort_by},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def get_trending_markets(limit: int = 10) -> None:
    """
    Get trending markets sorted by 24-hour volume
    """
    history = get_history_logger()
    console.print(f"[cyan]Fetching {limit} trending markets (sorted by 24h volume)[/cyan]")
    try:
        pm = get_polymarket()
        markets = pm.get_trending_markets(limit=limit)
        console.print(f"[green]Found {len(markets)} trending markets:[/green]")
        pprint(markets)
        # Log to MongoDB
        history.log_market_query(
            query_type="get_trending_markets",
            limit=limit,
            results_count=len(markets),
            markets=[m.dict() if hasattr(m, "dict") else str(m) for m in markets],
            success=True,
        )
        history.log_cli_command(
            command="get_trending_markets",
            parameters={"limit": limit},
            result={"markets_count": len(markets)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_market_query(
            query_type="get_trending_markets",
            limit=limit,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="get_trending_markets",
            parameters={"limit": limit},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def get_relevant_news(keywords: str) -> None:
    """
    Use NewsAPI to query the internet
    """
    history = get_history_logger()
    console.print(f"[cyan]Fetching news for keywords: {keywords}[/cyan]")
    try:
        news = get_news()
        articles = news.get_articles_for_cli_keywords(keywords)
        console.print(f"[green]Found {len(articles)} articles:[/green]")
        pprint(articles)
        # Log to MongoDB
        history.log_news_query(
            keywords=keywords,
            articles_count=len(articles),
            articles=[a.dict() if hasattr(a, "dict") else str(a) for a in articles],
            success=True,
        )
        history.log_cli_command(
            command="get_relevant_news",
            parameters={"keywords": keywords},
            result={"articles_count": len(articles)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_news_query(
            keywords=keywords,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="get_relevant_news",
            parameters={"keywords": keywords},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def get_all_events(limit: int = 5, sort_by: str = "number_of_markets") -> None:
    """
    Query Polymarket's events
    """
    history = get_history_logger()
    console.print(f"[cyan]Fetching {limit} events, sorted by {sort_by}[/cyan]")
    try:
        pm = get_polymarket()
        events = pm.get_all_events()
        events = pm.filter_events_for_trading(events)
        if sort_by == "number_of_markets":
            events = sorted(events, key=lambda x: len(x.markets.split(",")), reverse=True)
        events = events[:limit]
        console.print(f"[green]Found {len(events)} events:[/green]")
        pprint(events)
        # Log to MongoDB
        history.log_market_query(
            query_type="get_all_events",
            limit=limit,
            sort_by=sort_by,
            results_count=len(events),
            success=True,
        )
        history.log_cli_command(
            command="get_all_events",
            parameters={"limit": limit, "sort_by": sort_by},
            result={"events_count": len(events)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_market_query(
            query_type="get_all_events",
            limit=limit,
            sort_by=sort_by,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="get_all_events",
            parameters={"limit": limit, "sort_by": sort_by},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def create_local_markets_rag(local_directory: str) -> None:
    """
    Create a local markets database for RAG
    """
    history = get_history_logger()
    console.print(f"[cyan]Creating local RAG database in {local_directory}[/cyan]")
    try:
        rag = get_rag()
        rag.create_local_markets_rag(local_directory=local_directory)
        console.print("[green]RAG database created successfully![/green]")
        # Log to MongoDB
        history.log_rag_operation(
            operation_type="create_local_markets_rag",
            local_directory=local_directory,
            success=True,
        )
        history.log_cli_command(
            command="create_local_markets_rag",
            parameters={"local_directory": local_directory},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_rag_operation(
            operation_type="create_local_markets_rag",
            local_directory=local_directory,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="create_local_markets_rag",
            parameters={"local_directory": local_directory},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def query_local_markets_rag(vector_db_directory: str, query: str) -> None:
    """
    RAG over a local database of Polymarket's events
    """
    history = get_history_logger()
    console.print(f"[cyan]Querying RAG database: {query}[/cyan]")
    try:
        rag = get_rag()
        response = rag.query_local_markets_rag(
            local_directory=vector_db_directory, query=query
        )
        console.print("[green]RAG Results:[/green]")
        pprint(response)
        # Log to MongoDB
        history.log_rag_operation(
            operation_type="query_local_markets_rag",
            query=query,
            local_directory=vector_db_directory,
            results_count=len(response) if isinstance(response, list) else 1,
            success=True,
        )
        history.log_cli_command(
            command="query_local_markets_rag",
            parameters={"vector_db_directory": vector_db_directory, "query": query},
            result={"response_length": len(str(response))},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_rag_operation(
            operation_type="query_local_markets_rag",
            query=query,
            local_directory=vector_db_directory,
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="query_local_markets_rag",
            parameters={"vector_db_directory": vector_db_directory, "query": query},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def ask_superforecaster(event_title: str, market_question: str, outcome: str) -> None:
    """
    Ask a superforecaster about a trade
    """
    history = get_history_logger()
    console.print(f"[cyan]Event: {event_title}[/cyan]")
    console.print(f"[cyan]Question: {market_question}[/cyan]")
    console.print(f"[cyan]Outcome: {outcome}[/cyan]")
    try:
        executor = Executor()
        response = executor.get_superforecast(
            event_title=event_title, market_question=market_question, outcome=outcome
        )
        console.print("[green]Superforecaster Response:[/green]")
        console.print(response)
        # Log to MongoDB
        history.log_llm_query(
            query_type="ask_superforecaster",
            user_input=f"Event: {event_title}, Question: {market_question}, Outcome: {outcome}",
            response=response,
            model=executor.llm.model_name if hasattr(executor.llm, "model_name") else None,
            success=True,
        )
        history.log_cli_command(
            command="ask_superforecaster",
            parameters={"event_title": event_title, "market_question": market_question, "outcome": outcome},
            result={"response_length": len(response)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_llm_query(
            query_type="ask_superforecaster",
            user_input=f"Event: {event_title}, Question: {market_question}, Outcome: {outcome}",
            success=False,
            error=error_msg,
        )
        history.log_cli_command(
            command="ask_superforecaster",
            parameters={"event_title": event_title, "market_question": market_question, "outcome": outcome},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def create_market() -> None:
    """
    Format a request to create a market on Polymarket
    """
    history = get_history_logger()
    console.print("[cyan]Generating market idea...[/cyan]")
    try:
        c = Creator()
        market_description = c.one_best_market()
        console.print("[green]Market Description:[/green]")
        console.print(market_description)
        # Log to MongoDB (Creator class will also log internally)
        history.log_cli_command(
            command="create_market",
            parameters={},
            result={"market_description": market_description},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_cli_command(
            command="create_market",
            parameters={},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def ask_llm(user_input: str) -> None:
    """
    Ask a question to the LLM and get a response.
    """
    history = get_history_logger()
    console.print(f"[cyan]Querying LLM: {user_input}[/cyan]")
    try:
        executor = Executor()
        response = executor.get_llm_response(user_input)
        console.print("[green]LLM Response:[/green]")
        console.print(response)
        # Log to MongoDB (Executor will also log internally)
        history.log_cli_command(
            command="ask_llm",
            parameters={"user_input": user_input},
            result={"response_length": len(response)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_cli_command(
            command="ask_llm",
            parameters={"user_input": user_input},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def ask_polymarket_llm(user_input: str) -> None:
    """
    What types of markets do you want trade?
    """
    history = get_history_logger()
    console.print(f"[cyan]Querying Polymarket LLM: {user_input}[/cyan]")
    try:
        executor = Executor()
        response = executor.get_polymarket_llm(user_input=user_input)
        console.print("[green]LLM + current markets&events response:[/green]")
        console.print(response)
        # Log to MongoDB (Executor will also log internally)
        history.log_cli_command(
            command="ask_polymarket_llm",
            parameters={"user_input": user_input},
            result={"response_length": len(response)},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_cli_command(
            command="ask_polymarket_llm",
            parameters={"user_input": user_input},
            success=False,
            error=error_msg,
        )
        raise


@app.command()
def run_autonomous_trader() -> None:
    """
    Let an autonomous system trade for you.
    """
    history = get_history_logger()
    console.print("[yellow]⚠️  Starting autonomous trader...[/yellow]")
    console.print("[yellow]⚠️  Please review Terms of Service: https://polymarket.com/tos[/yellow]")
    try:
        trader = Trader()
        trader.one_best_trade()
        console.print("[green]Autonomous trading completed![/green]")
        # Log to MongoDB (Trader class will also log internally)
        history.log_cli_command(
            command="run_autonomous_trader",
            parameters={},
            result={"status": "completed"},
            success=True,
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")
        history.log_cli_command(
            command="run_autonomous_trader",
            parameters={},
            success=False,
            error=error_msg,
        )
        raise


if __name__ == "__main__":
    app()
