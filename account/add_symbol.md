Here are the **key steps** to add a dynamic symbol dropdown filter:

## **Step 1: Add Dropdown UI Component**

```python
# In your FIX Log layout (get_fix_log_layout() function)
html.Div([
    html.Label("Symbol Filter", className="block text-sm font-medium text-gray-700 mb-2"),
    dcc.Dropdown(
        id='symbol-filter',
        placeholder="Select symbol(s)...",
        multi=True,  # Allow multiple selections
        className="mb-4"
    ),
], className="mb-4"),
```

Place this in the filters section, after or before other filters like sender/target.

## **Step 2: Update Main Display Callback**

```python
# Add symbol-filter to inputs
@app.callback(
    [Output('data-table-container', 'children'),
     Output('msgtype-filter', 'options'),
     Output('summary-stats', 'children'),
     Output('msgtype-chart', 'figure')],
    [Input('parsed-data-store', 'data'),
     Input('msgtype-filter', 'value'),
     Input('sender-filter', 'value'),
     Input('target-filter', 'value'),
     Input('symbol-filter', 'value'),  # ADD THIS LINE
     Input('global-search', 'value'),
     Input('clear-filters', 'n_clicks')],
    [State('data-source-store', 'data')]
)
def update_display(parsed_data, msgtype_filter, sender_filter, target_filter, 
                   symbol_filter, global_search, clear_clicks, source_data):  # ADD symbol_filter parameter
    
    # ... existing code to convert data to DataFrame ...
    
    # ADD THIS FILTER LOGIC (after other filters, before global search):
    if symbol_filter:
        df = df[df['Symbol'].isin(symbol_filter)]
    
    # ... continue with global search and table creation ...
```

## **Step 3: Add Dynamic Options Callback**

```python
# New callback to populate symbol dropdown
@app.callback(
    Output('symbol-filter', 'options'),
    [Input('parsed-data-store', 'data')]
)
def update_symbol_options(parsed_data):
    """Dynamically populate symbol dropdown from parsed data"""
    if not parsed_data or not parsed_data['data']:
        return []
    
    df = pd.DataFrame(parsed_data['data'])
    
    # Check if Symbol column exists
    if 'Symbol' in df.columns and not df['Symbol'].empty:
        # Get unique symbols, sorted alphabetically
        symbols = sorted(df['Symbol'].dropna().astype(str).unique())
        
        # Create options with counts
        options = []
        for symbol in symbols:
            count = len(df[df['Symbol'] == symbol])
            options.append({
                'label': f"{symbol} ({count})",
                'value': symbol
            })
        return options
    
    return []
```

## **Step 4: Update Clear Filters Callback**

```python
# Add symbol-filter to outputs
@app.callback(
    [Output('msgtype-filter', 'value'),
     Output('sender-filter', 'value'),
     Output('target-filter', 'value'),
     Output('symbol-filter', 'value'),  # ADD THIS
     Output('global-search', 'value')],
    [Input('clear-filters', 'n_clicks')],
    prevent_initial_call=True
)
def clear_filter_inputs(n_clicks):
    if n_clicks:
        return None, '', '', None, ''  # None for symbol dropdown
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
```

## **Step 5: Add Select All Option (Optional)**

```python
# Modify the update_symbol_options callback:
def update_symbol_options(parsed_data):
    if not parsed_data or not parsed_data['data']:
        return []
    
    df = pd.DataFrame(parsed_data['data'])
    
    if 'Symbol' in df.columns and not df['Symbol'].empty:
        symbols = sorted(df['Symbol'].dropna().astype(str).unique())
        
        # Add "Select All" option at the top
        total_count = len(df)
        options = [{
            'label': f"📋 Select All ({total_count})",
            'value': 'ALL'
        }]
        
        for symbol in symbols:
            count = len(df[df['Symbol'] == symbol])
            options.append({
                'label': f"{symbol} ({count})",
                'value': symbol
            })
        return options
    
    return []

# Add callback to handle "Select All"
@app.callback(
    Output('symbol-filter', 'value'),
    [Input('symbol-filter', 'value')],
    [State('symbol-filter', 'options'),
     State('parsed-data-store', 'data')]
)
def handle_select_all(selected_symbols, options, parsed_data):
    """Handle 'Select All' option"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    if not parsed_data or not parsed_data['data']:
        return dash.no_update
    
    # Check if "ALL" was selected
    if selected_symbols and 'ALL' in selected_symbols:
        df = pd.DataFrame(parsed_data['data'])
        if 'Symbol' in df.columns:
            # Get all actual symbols (exclude "ALL")
            all_symbols = sorted(df['Symbol'].dropna().astype(str).unique())
            return all_symbols
    
    return selected_symbols
```

## **Step 6: Show Active Filter Count (Optional)**

```python
# Add this to your update_display callback, in the summary_stats section:
if 'Symbol' in df.columns and symbol_filter:
    symbol_count = len(symbol_filter)
    symbol_text = f"{symbol_count} symbol{'s' if symbol_count > 1 else ''} selected"
    
    # Add to your stats_cards or create a new card
    stats_cards.append(
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-line text-xl text-purple-600"),
                html.Div([
                    html.P("Symbols Filtered", className="text-sm font-medium text-gray-700"),
                    html.P(symbol_text, className="text-2xl font-bold text-gray-800")
                ], className="ml-4")
            ], className="flex items-center")
        ], className="bg-purple-50 rounded-xl p-4")
    )
```

## **Summary of Key Changes:**

1. **Add dropdown component** to layout
2. **Add symbol-filter to callback inputs** and parameter list
3. **Add filter logic** in update_display: `if symbol_filter: df = df[df['Symbol'].isin(symbol_filter)]`
4. **Create dynamic options callback** to populate dropdown from data
5. **Update clear filters** to reset symbol dropdown
6. **(Optional) Add "Select All"** functionality
7. **(Optional) Show filter stats** in summary

## **Minimal Working Version (Just Steps 1-4):**

```python
# 1. Add to layout:
html.Div([
    html.Label("Symbol Filter", className="block text-sm font-medium text-gray-700 mb-2"),
    dcc.Dropdown(id='symbol-filter', placeholder="Select symbol(s)...", multi=True),
], className="mb-4"),

# 2. Add to main callback inputs and parameters
# 3. Add filter logic:
if symbol_filter:
    df = df[df['Symbol'].isin(symbol_filter)]

# 4. Add options callback:
@app.callback(
    Output('symbol-filter', 'options'),
    [Input('parsed-data-store', 'data')]
)
def update_symbol_options(parsed_data):
    if not parsed_data or not parsed_data['data']:
        return []
    
    df = pd.DataFrame(parsed_data['data'])
    if 'Symbol' in df.columns:
        symbols = sorted(df['Symbol'].dropna().unique())
        return [{'label': sym, 'value': sym} for sym in symbols]
    return []

# 5. Update clear filters:
@app.callback(
    [Output('msgtype-filter', 'value'),
     Output('symbol-filter', 'value'),  # Add this
     ...],
    [Input('clear-filters', 'n_clicks')]
)
def clear_filter_inputs(n_clicks):
    if n_clicks:
        return None, None, ...  # None for symbol dropdown
    return dash.no_update, dash.no_update, ...
```

That's it! These are the essential steps to add a dynamic symbol dropdown filter to your FIX Log Viewer.