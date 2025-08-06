import pandas as pd
import numpy as np

## Step 1: Create Initial DataFrame
data = {
    'Date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', 
             '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01',
             '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01',
             '2025-01-01', '2025-02-01', '2025-03-01'],
    'adobe.com - Visits': [332326100, 320743500, 344297500, 335306400,
                          337284900, 312578500, 325797900, 338307600,
                          339340800, 354133100, 334800500, 315504600,
                          338102500, 327602100, 341440000],
    'openai.com - Bounce Rate': [0.580, 0.590, 0.610, 0.600, 0.620, 0.630,
                                0.610, 0.600, 0.620, 0.630, 0.640, 0.650,
                                0.581, 0.585, 0.590]
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

## Step 2: Calculate T3M Metrics
def calculate_t3m_metrics(df):
    # Sort by date to ensure proper rolling calculations
    df = df.sort_values('Date').copy()
    
    # Calculate T3M Bounce Rate (3-month rolling average)
    bounce_rate_col = 'openai.com - Bounce Rate'
    t3m_col = 'openai.com - Bounce Rate (T3M)'
    
    df[t3m_col] = df[bounce_rate_col].rolling(3, min_periods=1).mean()
    
    # Calculate M/M % change (compared to previous month's T3M)
    mm_col = 'openai.com - Bounce Rate (T3M) M/M %'
    df[mm_col] = df[t3m_col].pct_change(periods=1) * 100
    # Calculate M/M % change (compared to previous month's T3M)

    qq_col = 'openai.com - Bounce Rate (T3M) Q/Q %'
    df[qq_col] = df[t3m_col].pct_change(periods=3) * 100
    
    # Calculate Y/Y % change (compared to same quarter last year)
    yy_col = 'openai.com - Bounce Rate (T3M) Y/Y %'
    df[yy_col] = df[t3m_col].pct_change(periods=12) * 100
    
    return df

# Initial calculation
df = calculate_t3m_metrics(df)

print("Initial DataFrame with T3M Metrics:")
print(df[['Date', 'openai.com - Bounce Rate', 'openai.com - Bounce Rate (T3M)',
          'openai.com - Bounce Rate (T3M) Q/Q %', 'openai.com - Bounce Rate (T3M) Y/Y %']].tail(5))

## Step 3: Add New Data and Recalculate
new_data = {
    'Date': ['2025-04-01', '2025-05-01'],
    'adobe.com - Visits': [350000000, 345000000],
    'openai.com - Bounce Rate': [0.595, 0.605]
}

new_df = pd.DataFrame(new_data)
new_df['Date'] = pd.to_datetime(new_df['Date'])

# Append new data
df = pd.concat([df, new_df], ignore_index=True)
print (df)

# Recalculate metrics
df = calculate_t3m_metrics(df)

print("\nDataFrame After Adding New Data:")
print(df[['Date', 'openai.com - Bounce Rate', 'openai.com - Bounce Rate (T3M)', 'openai.com - Bounce Rate (T3M) M/M %',
          'openai.com - Bounce Rate (T3M) Q/Q %', 'openai.com - Bounce Rate (T3M) Y/Y %']].tail(20))
