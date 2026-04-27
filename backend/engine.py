import pandas as pd
import os

class PortfolioEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.portfolio_path = os.path.join(data_dir, 'portfolio.csv')
        self.market_path = os.path.join(data_dir, 'market_data.csv')
        self.news_path = os.path.join(data_dir, 'news.csv')

    def load_data(self):
        portfolio = pd.read_csv(self.portfolio_path)
        market = pd.read_csv(self.market_path)
        news = pd.read_csv(self.news_path)
        return portfolio, market, news

    def get_portfolio_summary(self):
        portfolio, market, news = self.load_data()
        df = pd.merge(portfolio, market, on='ticker')
        df['current_value'] = df['shares'] * df['current_price']
        df['invested_value'] = df['shares'] * df['buy_price']
        df['total_gain'] = df['current_value'] - df['invested_value']
        df['return_pct'] = (df['total_gain'] / df['invested_value']) * 100
        df['day_gain'] = (df['current_price'] - df['prev_close']) * df['shares']
        df['day_return_pct'] = ((df['current_price'] - df['prev_close']) / df['prev_close']) * 100
        total_invested = df['invested_value'].sum()
        total_current = df['current_value'].sum()
        total_gain = total_current - total_invested
        total_return_pct = (total_gain / total_invested) * 100
        day_gain = df['day_gain'].sum()
        day_return_pct = (day_gain / total_current) * 100
        return {
            "total_invested": round(total_invested, 2),
            "total_current": round(total_current, 2),
            "total_gain": round(total_gain, 2),
            "total_return_pct": round(total_return_pct, 2),
            "day_gain": round(day_gain, 2),
            "day_return_pct": round(day_return_pct, 2),
            "holdings": df.to_dict(orient='records')
        }

    def get_sector_exposure(self):
        portfolio, market, _ = self.load_data()
        df = pd.merge(portfolio, market, on='ticker')
        df['current_value'] = df['shares'] * df['current_price']
        sector_dist = df.groupby('sector')['current_value'].sum().reset_index()
        total_val = sector_dist['current_value'].sum()
        sector_dist['percentage'] = (sector_dist['current_value'] / total_val) * 100
        return sector_dist.to_dict(orient='records')

    def get_weekly_performance(self):
        history = pd.read_csv(os.path.join(self.data_dir, 'history.csv'))
        portfolio, market, _ = self.load_data()
        weekly_stats = []
        for ticker in portfolio['ticker'].unique():
            recent = history[history['ticker'] == ticker].sort_values('date', ascending=False)
            if not recent.empty:
                latest_price = market[market['ticker'] == ticker]['current_price'].iloc[0]
                oldest_price = recent.iloc[-1]['close_price']
                change = latest_price - oldest_price
                change_pct = (change / oldest_price) * 100
                weekly_stats.append({
                    "ticker": ticker,
                    "weekly_change": round(change, 2),
                    "weekly_change_pct": round(change_pct, 2)
                })
        return weekly_stats

    def get_relevant_news(self, tickers=None):
        _, _, news = self.load_data()
        if tickers:
            news = news[news['ticker'].isin(tickers) | (news['ticker'] == 'GLOBAL')]
        return news.to_dict(orient='records')
