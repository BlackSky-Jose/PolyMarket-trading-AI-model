import logging

from agents.application.executor import Executor as Agent
from agents.polymarket.gamma import GammaMarketClient as Gamma
from agents.polymarket.polymarket import Polymarket
from agents.utils.history import get_history_logger

logger = logging.getLogger(__name__)


class Creator:
    def __init__(self):
        self.polymarket = Polymarket()
        self.gamma = Gamma()
        self.agent = Agent()
    def one_best_market(self):
        """
        one_best_trade is a strategy that evaluates all events, markets, and orderbooks

        leverages all available information sources accessible to the autonomous agent

        then executes that trade without any human intervention

        """
        history = get_history_logger()
        try:
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

            best_market = self.agent.source_best_market_to_create(filtered_markets)
            logger.info(f"5. IDEA FOR NEW MARKET {best_market}")
            
            # Log to MongoDB
            history.log_market_creation(
                market_description=best_market,
                events_count=events_count,
                markets_count=markets_count,
                filtered_events_count=filtered_events_count,
                filtered_markets_count=filtered_markets_count,
                success=True,
            )
            return best_market

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in one_best_market: {error_msg}", exc_info=True)
            history.log_market_creation(
                success=False,
                error=error_msg,
            )
            logger.info("Retrying...")
            self.one_best_market()

    def maintain_positions(self):
        pass

    def incentive_farm(self):
        pass
if __name__ == "__main__":
    c = Creator()
    c.one_best_market()
