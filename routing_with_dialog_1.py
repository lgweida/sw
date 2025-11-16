import dash
from dash import html, dash_table, dcc, Input, Output, State
import pandas as pd
import csv
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# Sample customer data - replace with your actual data
customer_data = [
    {'id': 1, 'name': 'Customer A', 'sendercompid': 'BPGICRD', 'region': 'North America'},
    {'id': 2, 'name': 'Customer B', 'sendercompid': 'ARICMCRD', 'region': 'Europe'},
    {'id': 3, 'name': 'Customer C', 'sendercompid': 'GEODECRD', 'region': 'Asia'},
    {'id': 4, 'name': 'Customer D', 'sendercompid': 'ACAMLCRD', 'region': 'North America'},
    {'id': 5, 'name': 'Customer E', 'sendercompid': 'TVMGCRD', 'region': 'Europe'},
    {'id': 6, 'name': 'Customer F', 'sendercompid': 'BPGICRD', 'region': 'Asia'},
]

def create_routing_rules_from_csv_1():
    """
    Create routing rules visualization data from the CSV content
    """
    csv_content = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
BPGICRD;USD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;CAD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;*;*;SI;MizuhoTKGOR42BuySide
BPGICRD;USD;*;*;*;FlexTradeBuySide42
BPGICRD;CAD;*;*;*;FlexTradeBuySide42
BPGICRD;AUD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNH;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;HKD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;IDR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;INR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;JPY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;KRW;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;MYR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;NZD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;PHP;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;SGD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;THB;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;TWD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ARICMCRD;*;*;*;SI;MizuhoTKGOR42BuySide
ARICMCRD;USD;*;*;*;FlexTradeBuySide42
ARICMCRD;CAD;*;*;*;FlexTradeBuySide42
ARICMCRD;AUD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNH;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;HKD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;IDR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;INR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;JPY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;KRW;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;MYR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;NZD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;PHP;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;SGD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;THB;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;TWD;*;*;*;MizuhoTKGOR42BuySide
GEODECRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ACAMLCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
TVMGCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""
    
    # Parse CSV content
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(';')
    data = [line.split(';') for line in lines[1:]]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Analyze routing patterns and create visualization rules
    routing_rules = []
    
    # Color palette for different destinations
    destination_colors = {
        'O_FLEXTRADE_GLOBAL_PT_FIX42': '#3b82f6',
        'MizuhoTKGOR42BuySide': '#10b981', 
        'FlexTradeBuySide42': '#f59e0b'
    }
    
    # Group by destination and create order types based on conditions
    for destination in df['DESTINATION'].unique():
        dest_rules = df[df['DESTINATION'] == destination]
        
        # Create order type descriptions based on conditions
        for idx, rule in dest_rules.iterrows():
            order_type_parts = []
            
            # Build order type description from conditions
            if rule['CURRENCY'] != '*':
                order_type_parts.append(f"{rule['CURRENCY']}")
            
            if rule['TARGETSUBID'] != '*':
                order_type_parts.append(f"SubID:{rule['TARGETSUBID']}")
            
            if rule['COUNTRYCODE'] != '*':
                order_type_parts.append(f"Country:{rule['COUNTRYCODE']}")
            
            if rule['ETF'] != '*':
                order_type_parts.append(f"ETF:{rule['ETF']}")
            
            # If no specific conditions, it's a catch-all
            if not order_type_parts:
                order_type = f"All Orders → {rule['SENDERCOMPID']}"
            else:
                order_type = f"{' + '.join(order_type_parts)} → {rule['SENDERCOMPID']}"
            
            # Get color for destination, assign default if not found
            color = destination_colors.get(destination, '#6b7280')
            
            routing_rules.append({
                'orderType': order_type,
                'destination': destination,
                'color': color,
                'sendercompid': rule['SENDERCOMPID'],
                'currency': rule['CURRENCY'],
                'targetsubid': rule['TARGETSUBID'],
                'countrycode': rule['COUNTRYCODE'],
                'etf': rule['ETF']
            })
    
    return routing_rules


def create_routing_rules_from_csv():
    """
    Create routing rules visualization data from the CSV content maintaining natural order
    """
    csv_content = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
BPGICRD;USD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;CAD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;*;*;SI;MizuhoTKGOR42BuySide
BPGICRD;USD;*;*;*;FlexTradeBuySide42
BPGICRD;CAD;*;*;*;FlexTradeBuySide42
BPGICRD;AUD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNH;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;HKD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;IDR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;INR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;JPY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;KRW;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;MYR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;NZD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;PHP;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;SGD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;THB;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;TWD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ARICMCRD;*;*;*;SI;MizuhoTKGOR42BuySide
ARICMCRD;USD;*;*;*;FlexTradeBuySide42
ARICMCRD;CAD;*;*;*;FlexTradeBuySide42
ARICMCRD;AUD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNH;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;HKD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;IDR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;INR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;JPY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;KRW;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;MYR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;NZD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;PHP;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;SGD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;THB;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;TWD;*;*;*;MizuhoTKGOR42BuySide
GEODECRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ACAMLCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
TVMGCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""
    
    # Parse CSV content
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(';')
    data = [line.split(';') for line in lines[1:]]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Color palette for different destinations
    destination_colors = {
        'O_FLEXTRADE_GLOBAL_PT_FIX42': '#3b82f6',  # Blue
        'MizuhoTKGOR42BuySide': '#10b981',         # Green
        'FlexTradeBuySide42': '#f59e0b'            # Orange
    }
    
    routing_rules = []
    
    # Process rules in the exact order they appear in the CSV
    for _, rule in df.iterrows():
        order_type_parts = []
        
        # Build order type description from conditions
        if rule['CURRENCY'] != '*':
            order_type_parts.append(rule['CURRENCY'])
        
        if rule['TARGETSUBID'] != '*':
            order_type_parts.append(f"SubID:{rule['TARGETSUBID']}")
        
        if rule['COUNTRYCODE'] != '*':
            country_name = "Singapore" if rule['COUNTRYCODE'] == 'SI' else rule['COUNTRYCODE']
            order_type_parts.append(f"Country:{country_name}")
        
        if rule['ETF'] != '*':
            order_type_parts.append(f"ETF:{rule['ETF']}")
        
        # Create the order type string
        if order_type_parts:
            order_type = f"{' + '.join(order_type_parts)} → {rule['SENDERCOMPID']}"
        else:
            order_type = f"All Orders → {rule['SENDERCOMPID']}"
        
        # Get color for destination
        color = destination_colors.get(rule['DESTINATION'], '#6b7280')
        
        routing_rules.append({
            'orderType': order_type,
            'destination': rule['DESTINATION'],
            'color': color,
            'sendercompid': rule['SENDERCOMPID'],
            'currency': rule['CURRENCY'],
            'targetsubid': rule['TARGETSUBID'],
            'countrycode': rule['COUNTRYCODE'],
            'etf': rule['ETF']
        })
    
    return routing_rules

def get_routing_rules_for_customer(sendercompid: str) -> List[Dict[str, Any]]:
    """
    Get routing rules for a specific customer
    """
    all_rules = create_routing_rules_from_csv()
    customer_rules = [rule for rule in all_rules if rule['sendercompid'] == sendercompid]
    return customer_rules

def get_destinations_for_customer(sendercompid: str) -> List[str]:
    """
    Get unique destinations for a customer
    """
    customer_rules = get_routing_rules_for_customer(sendercompid)
    return list(set([rule['destination'] for rule in customer_rules]))

# Desk descriptions based on actual destinations from CSV
desk_descriptions = {
    'O_FLEXTRADE_GLOBAL_PT_FIX42': 'Primary global order routing destination for standard executions',
    'MizuhoTKGOR42BuySide': 'Mizuho Bank routing for specific currencies and country codes',
    'FlexTradeBuySide42': 'FlexTrade system for USD and CAD currency orders'
}

def create_flow_arrow_chart(rules):
    """
    Create an arrow flow diagram with shorter arrows that don't overlap with text.
    """
    if not rules:
        # Return empty figure if no rules provided
        fig = go.Figure()
        fig.update_layout(
            title="No routing rules to display",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return fig
    
    # Create data for the flow arrows
    sources = []
    targets = []
    
    for i, rule in enumerate(rules):
        # Source point (left side) - moved further right to avoid text overlap
        sources.append({
            'x': 0.1,  # Moved right to avoid text overlap
            'y': i,
            'label': rule['orderType'],
            'color': rule['color']
        })
        # Target point (right side) - moved further left to avoid text overlap
        targets.append({
            'x': 0.9,  # Moved left to avoid text overlap
            'y': i,
            'label': rule['destination'],
            'color': rule['color']
        })
    
    # Create the figure
    fig = go.Figure()
    
    # Add source nodes (left side - Order Types)
    fig.add_trace(go.Scatter(
        x=[s['x'] for s in sources],
        y=[s['y'] for s in sources],
        mode='markers+text',
        marker=dict(
            size=20,
            color=[s['color'] for s in sources],
            line=dict(width=2, color='white')
        ),
        text=[s['label'] for s in sources],
        textposition="middle right",
        textfont=dict(size=11, color='black'),
        name='Order Types',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))
    
    # Add target nodes (right side - Destinations)
    fig.add_trace(go.Scatter(
        x=[t['x'] for t in targets],
        y=[t['y'] for t in targets],
        mode='markers+text',
        marker=dict(
            size=20,
            color=[t['color'] for t in targets],
            line=dict(width=2, color='white')
        ),
        text=[t['label'] for t in targets],
        textposition="middle left",
        textfont=dict(size=11, color='black'),
        name='Destinations',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))
    
    # Add flow arrows with shorter length
    for i, (source, target) in enumerate(zip(sources, targets)):
        # Shorter arrows - start closer to source and end closer to target
        arrow_start_x = source['x'] + 0.15  # Start 0.15 from source
        arrow_end_x = target['x'] - 0.15    # End 0.15 before target
        
        fig.add_annotation(
            x=arrow_end_x,    # End point of arrow (closer to target)
            y=target['y'],
            ax=arrow_start_x, # Start point of arrow (closer to source)
            ay=source['y'],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2.5,
            arrowcolor=source['color'],
            opacity=0.8
        )
    
    # Update layout for better appearance
    fig.update_layout(
        title={
            'text': 'Order Routing Flow - Directional Arrow Diagram',
            'font': {'size': 20, 'color': '#1f2937', 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, 1]  # Tighter range for better spacing
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, len(rules) - 0.5]  # Better y-range for spacing
        ),
        plot_bgcolor='#f9fafb',
        paper_bgcolor='#f9fafb',
        margin=dict(l=80, r=80, t=80, b=50),  # Increased margins for text
        height=max(500, len(rules) * 60),  # Dynamic height based on number of rules
        width=900
    )
    
    return fig

def create_parallel_categories_chart(rules):
    """
    Create a parallel categories diagram for order routing flow.
    """
    if not rules:
        # Return empty figure if no rules provided
        fig = go.Figure()
        fig.update_layout(
            title="No routing rules to display",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return fig
    
    # Prepare data for parallel categories
    order_types = []
    destinations = []
    colors = []
    
    for rule in rules:
        order_types.append(rule['orderType'])
        destinations.append(rule['destination'])
        colors.append(rule['color'])
    
    # Create parallel categories diagram
    fig = go.Figure(data=
        go.Parcats(
            dimensions=[
                {'label': 'Order Type', 'values': order_types},
                {'label': 'Destination', 'values': destinations}
            ],
            line={'color': colors, 'colorscale': 'Viridis'},
            hoveron='color',
            hoverinfo='count+probability',
            arrangement='freeform'
        )
    )
    
    fig.update_layout(
        title={
            'text': 'Order Routing Flow - Parallel Categories View',
            'font': {'size': 20, 'color': '#1f2937', 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='#f9fafb',
        paper_bgcolor='#f9fafb',
        margin=dict(l=50, r=50, t=80, b=50),
        height=500
    )
    
    return fig

def create_enhanced_sankey_with_arrows(rules):
    """
    Create an enhanced Sankey diagram with better visual flow indicators.
    """
    if not rules:
        # Return empty figure if no rules provided
        fig = go.Figure()
        fig.update_layout(
            title="No routing rules to display",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return fig
    
    # Create source and target indices for Sankey links
    sources = list(range(len(rules)))
    targets = [i + len(rules) for i in range(len(rules))]
    
    # Use equal values for all flows
    values = [1] * len(rules)
    
    colors = [rule['color'] for rule in rules]
    
    # Create node labels (order types on left, destinations on right)
    node_labels = [rule['orderType'] for rule in rules] + [rule['destination'] for rule in rules]
    
    # Create node colors - use solid colors for both sources and targets
    node_colors = colors + colors
    
    # Create link colors - use rgba for transparency
    link_colors = []
    for color in colors:
        # Convert hex to rgba with transparency
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            link_colors.append(f'rgba({r}, {g}, {b}, 0.6)')
        else:
            link_colors.append(color)
    
    # Build the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="white", width=2),
            label=node_labels,
            color=node_colors,
            hovertemplate='<b>%{label}</b><extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><extra></extra>'
        )
    )])
    
    fig.update_layout(
        title={
            'text': 'Order Routing Flow - Enhanced Sankey Diagram',
            'font': {'size': 20, 'color': '#1f2937', 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=12, color='#374151', family='Inter'),
        plot_bgcolor='#f9fafb',
        paper_bgcolor='#f9fafb',
        margin=dict(l=50, r=50, t=80, b=50),
        height=500
    )
    
    return fig

# Routing rules functions for the original table view
def get_routing_rules(sendercompid: str, csv_file_path: str = 'routing.csv') -> List[Dict[str, Any]]:
    """
    Get routing rules for a given sendercompid from the routing CSV file.
    """
    routing_rules = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                if row['SENDERCOMPID'] == sendercompid:
                    routing_rules.append({
                        'SENDERCOMPID': row['SENDERCOMPID'],
                        'CURRENCY': row['CURRENCY'],
                        'TARGETSUBID': row['TARGETSUBID'],
                        'ETF': row['ETF'],
                        'COUNTRYCODE': row['COUNTRYCODE'],
                        'DESTINATION': row['DESTINATION']
                    })
    
    except FileNotFoundError:
        print(f"Error: Routing file '{csv_file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading routing file: {e}")
        return []
    
    return routing_rules

def get_smart_routing_display(sendercompid: str) -> List[Dict[str, Any]]:
    """
    Smart routing display that handles single-rule and multi-rule scenarios with currency grouping.
    """
    all_rules = get_routing_rules(sendercompid)
    
    if not all_rules:
        return []
    
    # Check if there's only one rule (typically a catch-all)
    if len(all_rules) == 1:
        single_rule = all_rules[0]
        # Return as "all -> destination"
        return [{
            'conditions': ['all'],
            'DESTINATION': single_rule['DESTINATION'],
            'is_default': True,
            'priority': 1
        }]
    
    # For multiple rules, group specific rules and find default
    specific_rules = []
    default_rule = None
    
    # First, group specific rules by destination and conditions (maintaining currency grouping)
    grouped_specific_rules = {}
    
    for i, rule in enumerate(all_rules, 1):
        # Check if this is a catch-all rule (all wildcards)
        is_catch_all = (
            rule['CURRENCY'] == '*' and 
            rule['TARGETSUBID'] == '*' and 
            rule['ETF'] == '*' and 
            rule['COUNTRYCODE'] == '*'
        )
        
        if is_catch_all:
            default_rule = {
                'conditions': ['rest'],
                'DESTINATION': rule['DESTINATION'],
                'is_default': True,
                'priority': i
            }
        else:
            # Group specific rules by destination and non-currency conditions
            key = (rule['DESTINATION'], rule['TARGETSUBID'], rule['ETF'], rule['COUNTRYCODE'])
            
            if key not in grouped_specific_rules:
                grouped_specific_rules[key] = {
                    'DESTINATION': rule['DESTINATION'],
                    'TARGETSUBID': rule['TARGETSUBID'],
                    'ETF': rule['ETF'],
                    'COUNTRYCODE': rule['COUNTRYCODE'],
                    'CURRENCIES': [],
                    'MIN_PRIORITY': i,
                    'RULE_COUNT': 0
                }
            
            if rule['CURRENCY'] != '*':
                if rule['CURRENCY'] not in grouped_specific_rules[key]['CURRENCIES']:
                    grouped_specific_rules[key]['CURRENCIES'].append(rule['CURRENCY'])
            
            grouped_specific_rules[key]['RULE_COUNT'] += 1
    
    # Convert grouped rules to display format
    for key, grouped_rule in grouped_specific_rules.items():
        conditions = []
        
        # Add currencies as grouped condition
        if grouped_rule['CURRENCIES']:
            sorted_currencies = sorted(grouped_rule['CURRENCIES'])
            if len(sorted_currencies) > 2:
                display_text = f"[{', '.join(sorted_currencies[:2])} +{len(sorted_currencies)-2} more]"
            else:
                display_text = f"[{', '.join(sorted_currencies)}]"
            conditions.append(display_text)
        
        # Add other conditions
        if grouped_rule['TARGETSUBID'] != '*':
            conditions.append(f"SubID:{grouped_rule['TARGETSUBID']}")
        if grouped_rule['COUNTRYCODE'] != '*':
            conditions.append(f"Country:{grouped_rule['COUNTRYCODE']}")
        if grouped_rule['ETF'] != '*':
            conditions.append(f"ETF:{grouped_rule['ETF']}")
        
        specific_rules.append({
            'conditions': conditions,
            'DESTINATION': grouped_rule['DESTINATION'],
            'is_default': False,
            'priority': grouped_rule['MIN_PRIORITY'],
            'rule_count': grouped_rule['RULE_COUNT']
        })
    
    # Sort specific rules by priority
    specific_rules.sort(key=lambda x: x['priority'])
    
    # If no explicit catch-all found, use the last rule as default
    if not default_rule and all_rules:
        default_rule = {
            'conditions': ['rest'],
            'DESTINATION': all_rules[-1]['DESTINATION'],
            'is_default': True,
            'priority': len(all_rules)
        }
    
    # Combine specific rules and default rule
    display_rules = specific_rules
    if default_rule:
        display_rules.append(default_rule)
    
    return display_rules

def create_routing_csv():
    """
    Create the routing CSV file from the provided data
    """
    csv_content = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
BPGICRD;USD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;CAD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;*;*;SI;MizuhoTKGOR42BuySide
BPGICRD;USD;*;*;*;FlexTradeBuySide42
BPGICRD;CAD;*;*;*;FlexTradeBuySide42
BPGICRD;AUD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNH;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;HKD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;IDR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;INR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;JPY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;KRW;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;MYR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;NZD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;PHP;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;SGD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;THB;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;TWD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ARICMCRD;*;*;*;SI;MizuhoTKGOR42BuySide
ARICMCRD;USD;*;*;*;FlexTradeBuySide42
ARICMCRD;CAD;*;*;*;FlexTradeBuySide42
ARICMCRD;AUD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNH;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;HKD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;IDR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;INR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;JPY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;KRW;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;MYR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;NZD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;PHP;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;SGD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;THB;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;TWD;*;*;*;MizuhoTKGOR42BuySide
GEODECRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ACAMLCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
TVMGCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""
    
    with open('routing.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)

# Create the routing CSV file
create_routing_csv()

# Convert customer data to DataFrame
df_customers = pd.DataFrame(customer_data)

# Initialize Dash app
app = dash.Dash(__name__)

# Add Tailwind CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .modal-backdrop {
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            .rule-row {
                transition: all 0.2s ease-in-out;
                border-left: 3px solid #3b82f6;
            }
            .rule-row:hover {
                background-color: #f8fafc;
                transform: translateX(2px);
            }
            .default-row {
                border-left: 3px solid #10b981;
                background-color: #f0fdf4;
            }
            .default-row:hover {
                background-color: #dcfce7;
            }
            .priority-badge {
                background-color: #fef3c7;
                color: #92400e;
                border: 1px solid #f59e0b;
            }
            .default-badge {
                background-color: #10b981;
                color: white;
                border: 1px solid #059669;
            }
            .currency-group-badge {
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #0ea5e9;
            }
            .target-badge {
                background-color: #f3e8ff;
                color: #7c3aed;
                border: 1px solid #a855f7;
            }
            .country-badge {
                background-color: #ffedd5;
                color: #ea580c;
                border: 1px solid #fb923c;
            }
            .destination-badge {
                background-color: #dcfce7;
                color: #166534;
                border: 1px solid #22c55e;
            }
            .all-badge {
                background-color: #6b7280;
                color: white;
                border: 1px solid #4b5563;
            }
        </style>
    </head>
    <body class="bg-gray-50">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout
app.layout = html.Div([
    # Main content
    html.Div([
        html.Div([
            html.H1("Customer Routing Rules", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Click on any customer to view their routing rules", className="text-gray-600")
        ], className="text-center mb-8"),
        
        html.Div([
            html.H2("Customers", className="text-xl font-semibold text-gray-700 mb-4"),
            html.Div([
                dash_table.DataTable(
                    id='customer-table',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Customer Name", "id": "name"},
                        {"name": "SenderCompID", "id": "sendercompid"},
                        {"name": "Region", "id": "region"}
                    ],
                    data=customer_data,
                    row_selectable='single',
                    selected_rows=[],
                    style_cell={
                        'textAlign': 'left', 
                        'padding': '12px',
                        'fontFamily': 'Inter, sans-serif',
                        'minWidth': '80px', 'width': '150px', 'maxWidth': '250px'
                    },
                    style_header={
                        'backgroundColor': '#f8fafc',
                        'fontWeight': '600',
                        'borderBottom': '2px solid #e2e8f0',
                        'textAlign': 'left'
                    },
                    style_data={
                        'border': '1px solid #e2e8f0'
                    },
                    style_data_conditional=[
                        {
                            'if': {'state': 'selected'},
                            'backgroundColor': '#dbeafe',
                            'border': '2px solid #3b82f6'
                        },
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8fafc'
                        }
                    ]
                )
            ], className="bg-white rounded-lg shadow-sm border border-gray-200 p-4")
        ], className="mb-8")
    ], className="container mx-auto px-4 py-8 max-w-6xl"),
    
    # Modal Dialog - Updated with visualization from rule_2.py
    html.Div([
        html.Div([
            # Modal header
            html.Div([
                html.Div([
                    html.H3("Routing Rules Visualization", className="text-xl font-semibold text-gray-800"),
                    html.Button(
                        html.I(className="fas fa-times text-lg"),
                        id="close-modal",
                        className="text-gray-400 hover:text-gray-600 transition-colors duration-200 p-1 rounded-full hover:bg-gray-100"
                    )
                ], className="flex justify-between items-center")
            ], className="px-6 py-4 border-b border-gray-200 bg-gray-50 rounded-t-lg"),
            
            # Modal body - Updated with visualization components
            html.Div([
                html.Div(id="modal-customer-info", className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),
                
                # View Type Selector
                html.Div([
                    html.H2('Select Visualization Type', 
                           className='text-xl font-semibold text-gray-900 mb-4'),
                    html.Div([
                        dcc.Dropdown(
                            id='view-type-selector',
                            options=[
                                {'label': '🔄 Arrow Flow Diagram', 'value': 'arrow'},
                                {'label': '📊 Parallel Categories', 'value': 'parallel'},
                                {'label': '🌊 Enhanced Sankey', 'value': 'sankey'}
                            ],
                            value='arrow',
                            className='w-full md:w-64',
                            clearable=False
                        )
                    ], className='flex justify-center')
                ], className='bg-white rounded-2xl shadow-sm p-6 mb-8 border border-gray-100'),
                
                # Flow Visualization Section
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='flow-chart',
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ], className='bg-white rounded-2xl shadow-sm p-6 border border-gray-100')
                ], className='mb-8'),
                
                # Routing Rules Table
                html.Div([
                    html.H2('Routing Rules Summary', 
                           className='text-xl font-semibold text-gray-900 mb-4'),
                    html.Div(id="routing-rules-table", className='overflow-hidden')
                ], className='bg-white rounded-2xl shadow-sm p-6 mb-8 border border-gray-100'),
                
                # Desk Descriptions
                html.Div([
                    html.H2('Desk Descriptions', 
                           className='text-xl font-semibold text-gray-900 mb-4'),
                    html.Div(id="desk-descriptions", className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6')
                ], className='bg-white rounded-2xl shadow-sm p-6 border border-gray-100')
                
            ], className="px-6 py-4")
        ], className="bg-white rounded-lg shadow-xl w-full max-w-7xl mx-auto transform transition-all max-h-[90vh] overflow-y-auto")
    ], id="routing-modal", className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden"),
    
    # Store component
    dcc.Store(id='selected-customer-store'),
    
    # Hidden div to track modal state
    html.Div(id='modal-state', style={'display': 'none'})
])

@app.callback(
    [Output('routing-modal', 'className'),
     Output('selected-customer-store', 'data'),
     Output('customer-table', 'selected_rows')],
    [Input('customer-table', 'selected_rows'),
     Input('close-modal', 'n_clicks'),
     Input('modal-state', 'children')],
    [State('customer-table', 'data'),
     State('routing-modal', 'className'),
     State('selected-customer-store', 'data')]
)
def toggle_modal(selected_rows, close_clicks, modal_state, customer_data, current_class, stored_customer):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-modal':
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    if trigger_id == 'customer-table' and selected_rows:
        selected_row_index = selected_rows[0]
        selected_customer = customer_data[selected_row_index]
        
        customer_store_data = {
            'id': selected_customer['id'],
            'name': selected_customer['name'],
            'sendercompid': selected_customer['sendercompid'],
            'region': selected_customer['region']
        }
        
        # Always open modal when a row is clicked, even if it's the same row
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop", customer_store_data, selected_rows
    
    return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []

@app.callback(
    Output('modal-customer-info', 'children'),
    [Input('selected-customer-store', 'data')]
)
def update_customer_info(selected_customer):
    if not selected_customer:
        return ""
    
    return html.Div([
        html.H4(f"{selected_customer['name']}", className="text-lg font-semibold text-gray-800 mb-2"),
        html.Div([
            html.Span([
                html.Strong("SenderCompID: ", className="text-gray-700"),
                html.Span(selected_customer['sendercompid'], className="font-mono bg-blue-100 px-2 py-1 rounded")
            ], className="mr-4"),
            html.Span([
                html.Strong("Region: ", className="text-gray-700"),
                html.Span(selected_customer['region'], className="bg-green-100 px-2 py-1 rounded")
            ])
        ], className="text-sm")
    ])

@app.callback(
    [Output('flow-chart', 'figure'),
     Output('routing-rules-table', 'children'),
     Output('desk-descriptions', 'children')],
    [Input('view-type-selector', 'value'),
     Input('selected-customer-store', 'data')]
)
def update_dashboard(view_type, selected_customer):
    """Update the dashboard based on view type selection and customer"""
    if not selected_customer:
        # Return empty components if no customer selected
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Select a customer to view routing rules",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return empty_fig, "No customer selected", "No customer selected"
    
    sendercompid = selected_customer['sendercompid']
    customer_rules = get_routing_rules_for_customer(sendercompid)
    customer_destinations = get_destinations_for_customer(sendercompid)
    
    if not customer_rules:
        # Return empty components if no rules found
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title=f"No routing rules found for {sendercompid}",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return empty_fig, "No routing rules found", "No routing rules found"
    
    # Create appropriate chart based on view type
    if view_type == 'arrow':
        fig = create_flow_arrow_chart(customer_rules)
    elif view_type == 'parallel':
        fig = create_parallel_categories_chart(customer_rules)
    else:  # sankey
        fig = create_enhanced_sankey_with_arrows(customer_rules)
    
    # Create routing rules table
    routing_table = html.Table([
        html.Thead([
            html.Tr([
                html.Th('Order Type', className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'),
                html.Th('Destination', className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'),
                html.Th('Color', className='px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider')
            ], className='bg-gray-50')
        ]),
        html.Tbody([
            html.Tr([
                html.Td(rule['orderType'], className='px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900'),
                html.Td(rule['destination'], className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'),
                html.Td([
                    html.Div(className='w-4 h-4 rounded-full border-2 border-gray-200 mx-auto', 
                            style={'backgroundColor': rule['color']})
                ], className='px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center')
            ], className='hover:bg-gray-50 transition duration-150')
            for rule in customer_rules
        ], className='bg-white divide-y divide-gray-200')
    ], className='min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden')
    
    # Create desk descriptions for this customer's destinations
    desk_descriptions_elements = []
    for destination in customer_destinations:
        if destination in desk_descriptions:
            desk_descriptions_elements.append(
                html.Div([
                    html.Div([
                        html.H3(destination, className='text-lg font-semibold text-gray-900 mb-2'),
                        html.P(desk_descriptions[destination], className='text-gray-600 text-sm leading-relaxed')
                    ], className='p-4')
                ], className='bg-gray-50 rounded-xl border-l-4 hover:shadow-md transition duration-200', 
                   style={'borderLeftColor': customer_rules[0]['color'] if customer_rules else '#6b7280'})
            )
    
    return fig, routing_table, desk_descriptions_elements

if __name__ == '__main__':
    app.run(debug=True, port=8050)