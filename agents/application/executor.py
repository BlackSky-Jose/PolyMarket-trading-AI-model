import os
import json
import ast
import re
import logging
import math
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agents.polymarket.gamma import GammaMarketClient as Gamma
from agents.connectors.chroma import PolymarketRAG as Chroma
from agents.utils.objects import SimpleEvent, SimpleMarket
from agents.application.prompts import Prompter
from agents.polymarket.polymarket import Polymarket
from agents.utils.history import get_history_logger

# BlockRun x402 integration - pay-per-request LLM
from agents.connectors.blockrun import BlockRunLLM

logger = logging.getLogger(__name__)

def retain_keys(data, keys_to_retain):
    if isinstance(data, dict):
        return {
            key: retain_keys(value, keys_to_retain)
            for key, value in data.items()
            if key in keys_to_retain
        }
    elif isinstance(data, list):
        return [retain_keys(item, keys_to_retain) for item in data]
    else:
        return data

class Executor:
    def __init__(self, default_model: str = 'gpt-4o-mini', use_blockrun: bool = None) -> None:
        load_dotenv()
        max_token_model: Dict[str, int] = {
            'gpt-3.5-turbo-16k': 15000,
            'gpt-4-1106-preview': 95000,
            'gpt-4o-mini': 128000,
            'gpt-4o': 128000,
        }
        self.token_limit = max_token_model.get(default_model, 128000)
        self.prompter = Prompter()

        # Determine which LLM backend to use
        # Priority: use_blockrun param > BLOCKRUN_WALLET_KEY env > OPENAI_API_KEY env
        blockrun_key = os.getenv("BLOCKRUN_WALLET_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if use_blockrun is None:
            use_blockrun = bool(blockrun_key)

        if use_blockrun and blockrun_key:
            # Use BlockRun x402 pay-per-request
            logger.info("Using BlockRun LLM (x402 pay-per-request)")
            self.llm = BlockRunLLM(
                model=f"openai/{default_model}",
                temperature=0,
            )
            self.using_blockrun = True
        else:
            # Fallback to direct OpenAI
            if not openai_key:
                logger.warning("Neither BLOCKRUN_WALLET_KEY nor OPENAI_API_KEY found")
            self.llm = ChatOpenAI(
                model=default_model,
                temperature=0,
            )
            self.using_blockrun = False

        self.gamma = Gamma()
        self.chroma = Chroma()
        self.polymarket = Polymarket()

    def get_llm_response(self, user_input: str) -> str:
        history = get_history_logger()
        try:
            system_message = SystemMessage(content=str(self.prompter.market_analyst()))
            human_message = HumanMessage(content=user_input)
            messages = [system_message, human_message]
            result = self.llm.invoke(messages)
            response = result.content
            # Log to MongoDB
            history.log_llm_query(
                query_type="ask_llm",
                user_input=user_input,
                response=response,
                model=self.llm.model_name if hasattr(self.llm, "model_name") else None,
                success=True,
            )
            return response
        except Exception as e:
            error_msg = str(e)
            history.log_llm_query(
                query_type="ask_llm",
                user_input=user_input,
                success=False,
                error=error_msg,
            )
            raise

    def get_superforecast(
        self, event_title: str, market_question: str, outcome: str
    ) -> str:
        history = get_history_logger()
        try:
            messages = self.prompter.superforecaster(
                description=event_title, question=market_question, outcome=outcome
            )
            result = self.llm.invoke(messages)
            response = result.content
            # Log to MongoDB
            history.log_llm_query(
                query_type="ask_superforecaster",
                user_input=f"Event: {event_title}, Question: {market_question}, Outcome: {outcome}",
                response=response,
                model=self.llm.model_name if hasattr(self.llm, "model_name") else None,
                success=True,
            )
            return response
        except Exception as e:
            error_msg = str(e)
            history.log_llm_query(
                query_type="ask_superforecaster",
                user_input=f"Event: {event_title}, Question: {market_question}, Outcome: {outcome}",
                success=False,
                error=error_msg,
            )
            raise


    def estimate_tokens(self, text: str) -> int:
        # This is a rough estimate. For more accurate results, consider using a tokenizer.
        return len(text) // 4  # Assuming average of 4 characters per token

    def process_data_chunk(self, data1: List[Dict[Any, Any]], data2: List[Dict[Any, Any]], user_input: str) -> str:
        system_message = SystemMessage(
            content=str(self.prompter.prompts_polymarket(data1=data1, data2=data2))
        )
        human_message = HumanMessage(content=user_input)
        messages = [system_message, human_message]
        result = self.llm.invoke(messages)
        return result.content


    def divide_list(self, original_list, i):
        # Calculate the size of each sublist
        sublist_size = math.ceil(len(original_list) / i)
        
        # Use list comprehension to create sublists
        return [original_list[j:j+sublist_size] for j in range(0, len(original_list), sublist_size)]
    
    def get_polymarket_llm(self, user_input: str) -> str:
        history = get_history_logger()
        try:
            data1 = self.gamma.get_current_events()
            data2 = self.gamma.get_current_markets()
            
            combined_data = str(self.prompter.prompts_polymarket(data1=data1, data2=data2))
            
            # Estimate total tokens
            total_tokens = self.estimate_tokens(combined_data)
            
            # Set a token limit (adjust as needed, leaving room for system and user messages)
            token_limit = self.token_limit
            if total_tokens <= token_limit:
                # If within limit, process normally
                response = self.process_data_chunk(data1, data2, user_input)
            else:
                # If exceeding limit, process in chunks
                logger.info(f'Total tokens {total_tokens} exceeding LLM capacity, splitting into chunks')
                group_size = (total_tokens // token_limit) + 1
                useful_keys = [
                    'id', 'questionID', 'description', 'liquidity', 'clobTokenIds',
                    'outcomes', 'outcomePrices', 'volume', 'startDate', 'endDate',
                    'question', 'events'
                ]
                data1 = retain_keys(data1, useful_keys)
                cut_1 = self.divide_list(data1, group_size)
                cut_2 = self.divide_list(data2, group_size)
                cut_data_12 = zip(cut_1, cut_2)

                results = []

                for cut_data in cut_data_12:
                    sub_data1 = cut_data[0]
                    sub_data2 = cut_data[1]
                    result = self.process_data_chunk(sub_data1, sub_data2, user_input)
                    results.append(result)
                
                response = " ".join(results)
            
            # Log to MongoDB
            history.log_llm_query(
                query_type="ask_polymarket_llm",
                user_input=user_input,
                response=response,
                model=self.llm.model_name if hasattr(self.llm, "model_name") else None,
                tokens_used=total_tokens,
                success=True,
            )
            return response
        except Exception as e:
            error_msg = str(e)
            history.log_llm_query(
                query_type="ask_polymarket_llm",
                user_input=user_input,
                success=False,
                error=error_msg,
            )
            raise
    def filter_events(self, events: "list[SimpleEvent]") -> str:
        prompt = self.prompter.filter_events(events)
        result = self.llm.invoke(prompt)
        return result.content

    def filter_events_with_rag(self, events: "list[SimpleEvent]") -> str:
        prompt = self.prompter.filter_events()
        logger.debug(f"Filtering events with RAG, prompt: {prompt[:100]}...")
        return self.chroma.events(events, prompt)

    def map_filtered_events_to_markets(
        self, filtered_events: "list[SimpleEvent]"
    ) -> "list[SimpleMarket]":
        markets = []
        for e in filtered_events:
            data = json.loads(e[0].json())
            market_ids = data["metadata"]["markets"].split(",")
            for market_id in market_ids:
                market_data = self.gamma.get_market(market_id)
                formatted_market_data = self.polymarket.map_api_to_market(market_data)
                markets.append(formatted_market_data)
        return markets

    def filter_markets(self, markets) -> "list[tuple]":
        prompt = self.prompter.filter_markets()
        logger.debug(f"Filtering markets, prompt: {prompt[:100]}...")
        return self.chroma.markets(markets, prompt)

    def source_best_trade(self, market_object) -> str:
        market_document = market_object[0].dict()
        market = market_document["metadata"]
        outcome_prices = ast.literal_eval(market["outcome_prices"])
        outcomes = ast.literal_eval(market["outcomes"])
        question = market["question"]
        description = market_document["page_content"]

        prompt = self.prompter.superforecaster(question, description, outcomes)
        logger.debug("Getting superforecast prediction")
        result = self.llm.invoke(prompt)
        content = result.content
        logger.debug(f"Superforecast result: {content[:200]}...")

        prompt = self.prompter.one_best_trade(content, outcomes, outcome_prices)
        logger.debug("Determining best trade")
        result = self.llm.invoke(prompt)
        content = result.content
        logger.debug(f"Best trade result: {content[:200]}...")
        return content

    def format_trade_prompt_for_execution(self, best_trade: str) -> float:
        data = best_trade.split(",")
        # price = re.findall("\d+\.\d+", data[0])[0]
        size = re.findall("\d+\.\d+", data[1])[0]
        usdc_balance = self.polymarket.get_usdc_balance()
        return float(size) * usdc_balance

    def source_best_market_to_create(self, filtered_markets) -> str:
        prompt = self.prompter.create_new_market(filtered_markets)
        logger.debug("Creating new market idea")
        result = self.llm.invoke(prompt)
        content = result.content
        return content
