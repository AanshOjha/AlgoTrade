**Development Approach**
- The first thing I did was sketch out how the whole project should work. I wanted a simple flow: fetch historical stock data → apply a trading strategy → run the backtest → save results in a database → generate charts and performance metrics. To keep things clean, I broke it down into separate parts like data feed, strategy logic, backtesting engine, and API endpoints. This made it much easier to fix issues and add features. I began with the backend, built the API in FastAPI, and tested every endpoint in Postman before even touching the frontend.

**Technologies Used**
- The backend is in Python, with FastAPI handling the API. For stock data and analysis, I used pandas and yfinance. Results and trade records are saved in SQLite since it’s lightweight and perfect for a project this size. Right now, the system supports two strategies—Moving Average Crossover and Bollinger Bands. The idea is to connect this backend to a Vue.js frontend later so it’s easier for users to interact with.

**Challenges & Learnings**
- I didn’t know much about trading when I started, so I had to learn the basics of technical analysis fast. For example, I found that Moving Average Crossovers usually work well in trending markets, while Bollinger Bands are better for ranging ones. On the development side, working with FastAPI was a big learning curve, especially using background tasks to run backtests without blocking everything else. Overall, the project taught me both trading concepts and modern backend development in a very practical way.
