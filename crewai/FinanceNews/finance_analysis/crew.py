import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool,DirectoryReadTool, FileReadTool
from typing import Optional, Type, Any


scrape_website_tool = ScrapeWebsiteTool()
search_tool = SerperDevTool(
    search_url="https://google.serper.dev/search",
    country="us",
    locale="en",
    n_results=50
)

data_output_dir = "data/stock_data"

class StockDataDownloader:
    def download_stock_data(self, symbols: list) -> str:
        """Downloads stock data and saves to file"""
        data_dir = data_output_dir
        os.makedirs(data_dir, exist_ok=True)

        try:
            # Initialize multiple tickers at once
            tickers = yf.Tickers(' '.join(symbols))

            # Download batch historical data with proper parsing
            history_data = yf.download(
                ' '.join(symbols),
                period="2y",
                group_by='ticker'
            )

            # Save combined history with proper structure
            history_file = f"{data_dir}/all_tickers_history.csv"
            history_data.to_csv(
                history_file,
                # Preserve data types and formatting
                float_format='%.2f',  # Format floats to 2 decimal places
                date_format='%Y-%m-%d'  # Consistent date format
            )

            # When saving individual ticker histories, add metadata
            for symbol in symbols:
                symbol_dir = f"{data_dir}/{symbol}"
                os.makedirs(symbol_dir, exist_ok=True)

                # Extract and save individual ticker history
                if len(symbols) > 1:
                    ticker_history = history_data[symbol]
                else:
                    ticker_history = history_data

                history_file = f"{symbol_dir}/history.csv"
                ticker_history.to_csv(history_file)

                # Add structured metadata about the columns
                history_metadata = {
                    'columns': {
                        'Open': {
                            'description': 'Opening price of the trading day',
                            'type': 'float',
                            'unit': 'USD'
                        },
                        'High': {
                            'description': 'Highest price during the trading day',
                            'type': 'float',
                            'unit': 'USD'
                        },
                        'Low': {
                            'description': 'Lowest price during the trading day',
                            'type': 'float',
                            'unit': 'USD'
                        },
                        'Close': {
                            'description': 'Closing price of the trading day',
                            'type': 'float',
                            'unit': 'USD'
                        },
                        'Adj Close': {
                            'description': 'Adjusted closing price (accounting for splits/dividends)',
                            'type': 'float',
                            'unit': 'USD'
                        },
                        'Volume': {
                            'description': 'Number of shares traded',
                            'type': 'integer',
                            'unit': 'shares'
                        }
                    },
                    'period': {
                        'start_date': str(ticker_history.index.min()),
                        'end_date': str(ticker_history.index.max()),
                        'trading_days': len(ticker_history)
                    }
                }

                metadata_file = f"{symbol_dir}/history_metadata.json"
                pd.DataFrame([history_metadata]).to_json(metadata_file)
                print(f"Created history files for {symbol}")

                # Process each ticker's specific data
                ticker = tickers.tickers[symbol]
                symbol_dir = f"{data_dir}/{symbol}"
                os.makedirs(symbol_dir, exist_ok=True)

                try:
                    # Save individual ticker info
                    info_file = f"{symbol_dir}/info.json"
                    pd.DataFrame([ticker.info]).to_json(info_file)
                    print(f"Downloaded info for {symbol}")

                    # Save actions (dividends, splits, capital gains)
                    if not ticker.actions.empty:
                        actions_file = f"{symbol_dir}/actions.csv"
                        ticker.actions.to_csv(actions_file)
                    if not ticker.dividends.empty:
                        dividends_file = f"{symbol_dir}/dividends.csv"
                        ticker.dividends.to_csv(dividends_file)
                    if not ticker.splits.empty:
                        splits_file = f"{symbol_dir}/splits.csv"
                        ticker.splits.to_csv(splits_file)
                    print(f"Downloaded actions data for {symbol}")

                    # Save share count
                    shares = ticker.get_shares_full(start="2022-01-01", end=None)
                    if not shares.empty:
                        shares_file = f"{symbol_dir}/shares.csv"
                        shares.to_csv(shares_file)
                    print(f"Downloaded shares data for {symbol}")

                    # Save financials
                    if hasattr(ticker, 'calendar') and ticker.calendar:
                        calendar_file = f"{symbol_dir}/calendar.json"
                        pd.DataFrame([ticker.calendar]).to_json(calendar_file)

                    if not ticker.income_stmt.empty:
                        income_file = f"{symbol_dir}/income.csv"
                        ticker.income_stmt.to_csv(income_file)
                    if not ticker.quarterly_income_stmt.empty:
                        quarterly_income_file = f"{symbol_dir}/quarterly_income.csv"
                        ticker.quarterly_income_stmt.to_csv(quarterly_income_file)

                    if not ticker.balance_sheet.empty:
                        balance_file = f"{symbol_dir}/balance.csv"
                        ticker.balance_sheet.to_csv(balance_file)
                    if not ticker.quarterly_balance_sheet.empty:
                        quarterly_balance_file = f"{symbol_dir}/quarterly_balance.csv"
                        ticker.quarterly_balance_sheet.to_csv(quarterly_balance_file)

                    if not ticker.cashflow.empty:
                        cashflow_file = f"{symbol_dir}/cashflow.csv"
                        ticker.cashflow.to_csv(cashflow_file)
                    if not ticker.quarterly_cashflow.empty:
                        quarterly_cashflow_file = f"{symbol_dir}/quarterly_cashflow.csv"
                        ticker.quarterly_cashflow.to_csv(quarterly_cashflow_file)
                    print(f"Downloaded financial statements for {symbol}")

                    # Save holders data
                    if not ticker.major_holders.empty:
                        holders_file = f"{symbol_dir}/major_holders.csv"
                        ticker.major_holders.to_csv(holders_file)
                    if not ticker.institutional_holders.empty:
                        institutional_holders_file = f"{symbol_dir}/institutional_holders.csv"
                        ticker.institutional_holders.to_csv(institutional_holders_file)
                    if hasattr(ticker, 'mutualfund_holders') and not ticker.mutualfund_holders.empty:
                        mutualfund_holders_file = f"{symbol_dir}/mutualfund_holders.csv"
                        ticker.mutualfund_holders.to_csv(mutualfund_holders_file)
                    print(f"Downloaded holders data for {symbol}")

                    # Save analysis data
                    if hasattr(ticker, 'recommendations') and not ticker.recommendations.empty:
                        recommendations_file = f"{symbol_dir}/recommendations.csv"
                        ticker.recommendations.to_csv(recommendations_file)

                    if hasattr(ticker, 'recommendations_summary'):
                        recommendations_summary_file = f"{symbol_dir}/recommendations_summary.json"
                        pd.DataFrame([ticker.recommendations_summary]).to_json(recommendations_summary_file)

                    if hasattr(ticker, 'analyst_price_targets') and not ticker.analyst_price_targets.empty:
                        analyst_price_targets_file = f"{symbol_dir}/analyst_price_targets.csv"
                        ticker.analyst_price_targets.to_csv(analyst_price_targets_file)


                    if hasattr(ticker, 'earnings_dates') and not ticker.earnings_dates.empty:
                        earnings_dates_file = f"{symbol_dir}/earnings_dates.csv"
                        ticker.earnings_dates.to_csv(earnings_dates_file)
                    print(f"Downloaded analysis data for {symbol}")

                except Exception as e:
                    print(f"Error downloading specific data for {symbol}: {str(e)}")

        except Exception as e:
            print(f"Error downloading data: {str(e)}")
            raise

        return data_dir

stock_data_downloader = StockDataDownloader()

@CrewBase
class FinancialAnalysisCrew:
    """Financial Analysis crew for analyzing tech companies"""

    def __init__(self):
        self.data_dir = None

    def download_all_stock_data(self, symbols: list) -> str:
        """Download stock data for all companies before analysis"""
        self.data_dir = stock_data_downloader.download_stock_data(symbols)
        return self.data_dir

    @agent
    def captain_future_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['captain_future_agent'],
            tools=[DirectoryReadTool(directory=data_output_dir), FileReadTool()],
            verbose=True
        )

    @agent
    def news_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['news_research_agent'],
            tools=[search_tool, scrape_website_tool],
            verbose=True
        )

    @agent
    def tech_innovation_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['tech_innovation_analyst'],
            tools=[search_tool, scrape_website_tool],
            verbose=True
        )

    @agent
    def social_sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['social_sentiment_analyst'],
            tools=[search_tool, scrape_website_tool],
            verbose=True
        )

    @agent
    def market_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_data_analyst'],
            tools=[
                DirectoryReadTool(directory=data_output_dir),
                FileReadTool()
            ],
            verbose=True
        )

    @agent
    def event_impact_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['event_impact_analyst'],
            tools=[
                search_tool,
                scrape_website_tool,
                DirectoryReadTool(directory=data_output_dir),
                FileReadTool()
            ],
            verbose=True
        )

    @agent
    def comparison_report_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['comparison_report_agent'],
            tools=[
                DirectoryReadTool(directory='./outputs'),
                FileReadTool()
            ],
            verbose=True
        )

    @task
    def news_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['news_research_task']
        )

    @task
    def market_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_data_task']
        )

    @task
    def event_impact_task(self) -> Task:
        return Task(
            config=self.tasks_config['event_impact_task']
        )

    @task
    def comparison_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['comparison_report_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Financial Analysis crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True
        )