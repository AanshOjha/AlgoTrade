* Moving Average Crossover (SMA/EMA)
Signal tells you what mode you're in (buy or not). Position tells you when to act—only when the mode changes. So you trade only when Position is +1 (buy) or –1 (sell).

### Backtesting Engine

```mermaid
graph TD
    A[Start Backtest] --> B{Initialize Portfolio: Set Cash = $10,000, Shares = 0};
    B --> C{Start Loop: For Each Day in Historical Data};
    C --> D{Read Signal for the Day};
    D --> E{Buy? Signal == 1?};
    E -- Yes --> F{Do we already own shares?};
    F -- No --> G[Execute Buy: Update Cash & Shares];
    F -- Yes --> H[Hold: Do Nothing];
    E -- No --> I{Sell? Signal == -1?};
    I -- Yes --> J{Do we own any shares?};
    J -- Yes --> K[Execute Sell: Update Cash & Shares];
    J -- No --> H;
    I -- No --> H;
    G --> L[Update Daily Portfolio Value];
    K --> L;
    H --> L;
    L --> M{Is it the last day?};
    M -- No --> C;
    M -- Yes --> N[End Loop];
    N --> O[Calculate Final Performance Metrics];
    O --> P[End Backtest];
```