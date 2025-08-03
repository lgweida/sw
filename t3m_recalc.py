import pandas as pd
import numpy as np

def calculate_t3m_metrics(df):
    """
    Recalculate T3M (Trailing 3-Month) metrics for visits and bounce rate
    Including Q/Q % and Y/Y % calculations
    """
    # Make a copy to avoid modifying original
    df_calc = df.copy()
    
    # Ensure Date column is datetime
    df_calc['Date'] = pd.to_datetime(df_calc['Date'])
    df_calc = df_calc.sort_values('Date').reset_index(drop=True)
    
    # Extract base column names (assuming pattern: "site.com - Metric")
    # You'll need to adjust these column names to match your actual data
    visits_col = 'adobe.com - Visits'  # Adjust as needed
    bounce_rate_col = 'openai.com - Bounce Rate'  # Adjust as needed
    
    # Calculate T3M for Visits
    visits_t3m_col = f'{visits_col.split(" - ")[0]} - Visits (T3M)'
    df_calc[visits_t3m_col] = df_calc[visits_col].rolling(window=3, min_periods=3).mean()
    
    # Calculate T3M for Bounce Rate
    bounce_t3m_col = f'{bounce_rate_col.split(" - ")[0]} - Bounce Rate (T3M)'
    df_calc[bounce_t3m_col] = df_calc[bounce_rate_col].rolling(window=3, min_periods=3).mean()
    
    # Calculate Q/Q % (Quarter over Quarter) - comparing current T3M to T3M from 3 months ago
    qq_col = f'{bounce_t3m_col} Q/Q %'
    df_calc[qq_col] = df_calc[bounce_t3m_col].pct_change(periods=3)
    
    # Calculate Y/Y % (Year over Year) - comparing current T3M to T3M from 12 months ago
    yy_col = f'{bounce_t3m_col} Y/Y %'
    df_calc[yy_col] = df_calc[bounce_t3m_col].pct_change(periods=12)
    
    return df_calc

def add_new_data_and_recalculate(df, new_date, new_visits, new_bounce_rate):
    """
    Add new row of data and recalculate all T3M metrics
    """
    # Create new row
    new_row = {
        'Date': new_date,
        'adobe.com - Visits': new_visits,
        'openai.com - Bounce Rate': new_bounce_rate
    }
    
    # Add other columns with NaN (they'll be calculated)
    for col in df.columns:
        if col not in new_row:
            new_row[col] = np.nan
    
    # Append new row
    df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Recalculate all T3M metrics
    df_recalculated = calculate_t3m_metrics(df_updated)
    
    return df_recalculated

# Example usage function
def example_usage():
    """
    Example of how to use the functions with your data
    """
    # Assuming your dataframe is called 'df'
    # df = your_dataframe_here
    
    # Method 1: Recalculate existing data
    # df_recalculated = calculate_t3m_metrics(df)
    
    # Method 2: Add new data and recalculate
    # df_updated = add_new_data_and_recalculate(
    #     df, 
    #     new_date='2025-04-01',
    #     new_visits=350000000.0,
    #     new_bounce_rate=0.595
    # )
    
    # Method 3: If you want to update specific T3M calculations manually
    # df['openai.com - Bounce Rate (T3M)'] = df['openai.com - Bounce Rate'].rolling(window=3, min_periods=3).mean()
    # df['openai.com - Bounce Rate (T3M) Q/Q %'] = df['openai.com - Bounce Rate (T3M)'].pct_change(periods=3)
    # df['openai.com - Bounce Rate (T3M) Y/Y %'] = df['openai.com - Bounce Rate (T3M)'].pct_change(periods=12)
    
    pass

# Helper function to verify calculations
def verify_t3m_calculation(df, metric_col, t3m_col, row_index):
    """
    Verify T3M calculation for a specific row
    """
    if row_index < 2:  # Need at least 3 rows for T3M
        return None
    
    start_idx = max(0, row_index - 2)
    end_idx = row_index + 1
    
    manual_t3m = df[metric_col].iloc[start_idx:end_idx].mean()
    calculated_t3m = df[t3m_col].iloc[row_index]
    
    print(f"Row {row_index}:")
    print(f"Manual T3M calculation: {manual_t3m:.6f}")
    print(f"DataFrame T3M value: {calculated_t3m:.6f}")
    print(f"Match: {abs(manual_t3m - calculated_t3m) < 0.000001}")
    
    return manual_t3m