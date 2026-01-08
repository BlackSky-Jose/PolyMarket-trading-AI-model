import logging
import shutil
from pathlib import Path

from agents.application.executor import Executor as Agent
from agents.polymarket.gamma import GammaMarketClient as Gamma
from agents.polymarket.polymarket import Polymarket
from agents.utils.history import get_history_logger

logger = logging.getLogger(__name__)


class Trader:
    def __init__(self):
        self.polymarket = Polymarket()
        self.gamma = Gamma()
        self.agent = Agent()

    def pre_trade_logic(self) -> None:
        self.clear_local_dbs()

    def clear_local_dbs(self) -> None:
        """Clear local database directories."""
        for db_dir in ["local_db_events", "local_db_markets"]:
            db_path = Path(db_dir)
            if db_path.exists():
                try:
                    shutil.rmtree(db_path)
                    logger.info(f"Cleared {db_dir}")
                except OSError as e:
                    logger.warning(f"Failed to clear {db_dir}: {e}")

    def one_best_trade(self) -> None:
        """

        one_best_trade is a strategy that evaluates all events, markets, and orderbooks

        leverages all available information sources accessible to the autonomous agent

        then executes that trade without any human intervention

        """
        history = get_history_logger()
        try:
            self.pre_trade_logic()

            events = self.polymarket.get_all_tradeable_events()
            events_count = len(events)
            logger.info(f"1. FOUND {events_count} EVENTS")

            filtered_events = self.agent.filter_events_with_rag(events)
            filtered_events_count = len(filtered_events) if isinstance(filtered_events, list) else 0
            logger.info(f"2. FILTERED {filtered_events_count} EVENTS")

            markets = self.agent.map_filtered_events_to_markets(filtered_events)
            markets_count = len(markets)
            logger.info(f"3. FOUND {markets_count} MARKETS")

            filtered_markets = self.agent.filter_markets(markets)
            filtered_markets_count = len(filtered_markets) if isinstance(filtered_markets, list) else 0
            logger.info(f"4. FILTERED {filtered_markets_count} MARKETS")

            if not filtered_markets:
                logger.warning("No markets found after filtering")
                history.log_trade_operation(
                    operation_type="one_best_trade",
                    events_count=events_count,
                    markets_count=markets_count,
                    filtered_events_count=filtered_events_count,
                    filtered_markets_count=filtered_markets_count,
                    success=False,
                    error="No markets found after filtering",
                )
                return

            market = filtered_markets[0]
            best_trade = self.agent.source_best_trade(market)
            logger.info(f"5. CALCULATED TRADE {best_trade}")

            amount = self.agent.format_trade_prompt_for_execution(best_trade)
            # Please refer to TOS before uncommenting: polymarket.com/tos
            # trade = self.polymarket.execute_market_order(market, amount)
            # logger.info(f"6. TRADED {trade}")

            # Log successful trade operation
            market_id = None
            market_data = None
            if hasattr(market[0], "dict"):
                market_dict = market[0].dict()
                market_id = market_dict.get("metadata", {}).get("id") if isinstance(market_dict.get("metadata"), dict) else None
                market_data = market_dict

            history.log_trade_operation(
                operation_type="one_best_trade",
                market_id=str(market_id) if market_id else None,
                market_data=market_data,
                events_count=events_count,
                markets_count=markets_count,
                filtered_events_count=filtered_events_count,
                filtered_markets_count=filtered_markets_count,
                best_trade=best_trade,
                amount=amount,
                success=True,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in one_best_trade: {error_msg}", exc_info=True)
            history.log_trade_operation(
                operation_type="one_best_trade",
                success=False,
                error=error_msg,
            )
            logger.info("Retrying...")
            self.one_best_trade()

    def maintain_positions(self):
        pass

    def incentive_farm(self):
        pass


if __name__ == "__main__":
    t = Trader()
    t.one_best_trade()
