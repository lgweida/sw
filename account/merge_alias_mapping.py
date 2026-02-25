import csv
from io import StringIO

# First file content (sungard.csv)
sungard_content = """SENDERCOMPID;ONBEHALFOFCOMPID;CURRENCY;TARGETSUBID;FIX.5847;ETF;COUNTRYCODE;DESTINATION
*;*;USD;PROG;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;CAD;PROG;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;*;PROG;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;USD;*;PT;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;CAD;*;PT;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;*;*;PT;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;ARDSLY42;USD;*;*;*;*;FlexTradeBuySide42
*;ARDSLY42;CAD;*;*;*;*;FlexTradeBuySide42
*;ARDSLY42;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;URDG42;*;*;*;*;SI;MizuhoTKGOR42BuySide
*;URDG42;USD;*;*;*;*;FlexTradeBuySide42
*;URDG42;CAD;*;*;*;*;FlexTradeBuySide42
*;URDG42;AUD;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;CNH;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;CNY;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;HKD;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;IDR;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;INR;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;JPY;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;KRW;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;MYR;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;NZD;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;PHP;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;SGD;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;THB;*;*;*;*;MizuhoTKGOR42BuySide
*;URDG42;TWD;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;*;*;*;*;SI;MizuhoTKGOR42BuySide
*;HARDING42;USD;*;*;*;*;FlexTradeBuySide42
*;HARDING42;CAD;*;*;*;*;FlexTradeBuySide42
*;HARDING42;AUD;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;CNH;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;CNY;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;HKD;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;IDR;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;INR;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;JPY;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;KRW;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;MYR;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;NZD;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;PHP;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;SGD;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;THB;*;*;*;*;MizuhoTKGOR42BuySide
*;HARDING42;TWD;*;*;*;*;MizuhoTKGOR42BuySide
*;SECR42;USD;*;*;*;*;FlexTradeBuySide42
*;WHALERC42;USD;*;*;*;*;FlexTradeBuySide42
*;GQG42;USD;*;*;*;*;FlexTradeBuySide42
*;SBHIC42;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;JONSTN42;*;*;*;*;SI;MizuhoTKGOR42BuySide
*;JONSTN42;USD;*;*;*;*;FlexTradeBuySide42
*;JONSTN42;CAD;*;*;*;*;FlexTradeBuySide42
*;JONSTN42;AUD;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;CNH;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;CNY;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;HKD;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;IDR;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;INR;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;JPY;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;KRW;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;MYR;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;NZD;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;PHP;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;SGD;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;THB;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;TWD;*;*;*;*;MizuhoTKGOR42BuySide
*;JONSTN42;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;USD;*;*;*;*;FlexTradeBuySide42
*;PARK42;CAD;*;*;*;*;FlexTradeBuySide42
*;PARK42;AUD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;CNH;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;CNY;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;HKD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;IDR;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;INR;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;JPY;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;KRW;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;MYR;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;NZD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;PHP;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;SGD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;THB;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;TWD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;PARK42;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;ARDSLY42;USD;*;*;*;*;FlexTradeBuySide42
*;ARDSLY42;CAD;*;*;*;*;FlexTradeBuySide42
*;ECMPSCAP;USD;*;*;*;*;FlexTradeBuySide42
*;ECMPSCAP;CAD;*;*;*;*;FlexTradeBuySide42
*;ALYESKA;USD;*;*;*;*;FlexTradeBuySide42
*;ALYESKA;CAD;*;*;*;*;FlexTradeBuySide42
*;GLG;USD;*;*;*;*;FlexTradeBuySide42
*;GLG;CAD;*;*;*;*;FlexTradeBuySide42
STN_RICE_P2P;*;*;*;*;*;SI;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;USD;*;*;*;*;FlexTradeBuySide42
STN_RICE_P2P;*;CAD;*;*;*;*;FlexTradeBuySide42
STN_RICE_P2P;*;AUD;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;CNH;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;CNY;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;HKD;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;IDR;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;INR;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;JPY;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;KRW;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;MYR;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;NZD;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;PHP;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;SGD;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;THB;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;TWD;*;*;*;*;MizuhoTKGOR42BuySide
STN_RICE_P2P;*;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
*;*;*;*;*;*;SI;MizuhoTKGOR42BuySide
*;*;USD;*;*;*;*;FlexTradeBuySide42
*;*;CAD;*;*;*;*;FlexTradeBuySide42
*;*;AUD;*;*;*;*;MizuhoTKGOR42BuySide
*;*;CNH;*;*;*;*;MizuhoTKGOR42BuySide
*;*;CNY;*;*;*;*;MizuhoTKGOR42BuySide
*;*;HKD;*;*;*;*;MizuhoTKGOR42BuySide
*;*;IDR;*;*;*;*;MizuhoTKGOR42BuySide
*;*;INR;*;*;*;*;MizuhoTKGOR42BuySide
*;*;JPY;*;*;*;*;MizuhoTKGOR42BuySide
*;*;KRW;*;*;*;*;MizuhoTKGOR42BuySide
*;*;MYR;*;*;*;*;MizuhoTKGOR42BuySide
*;*;NZD;*;*;*;*;MizuhoTKGOR42BuySide
*;*;PHP;*;*;*;*;MizuhoTKGOR42BuySide
*;*;SGD;*;*;*;*;MizuhoTKGOR42BuySide
*;*;THB;*;*;*;*;MizuhoTKGOR42BuySide
*;*;TWD;*;*;*;*;MizuhoTKGOR42BuySide
*;*;*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""

# Second file content (sunguard_mapping.csv)
mapping_content = """URDG42;20010964
HARDING42;20010206
SECR42;20011217
WHALERC42;20010777
GQG42;20011356
SBHIC42;20011570
JONSTN42;20011762
PARK42;20010694
ARDSLY42;20010641
ECMPSCAP;20012531
ALYESKA;20011028
GLG;20010476"""

# Parse the mapping file into a dictionary
mapping_dict = {}
for line in mapping_content.strip().split('\n'):
    key, value = line.split(';')
    mapping_dict[key] = value

# Parse the sungard file and perform inner join
sungard_lines = sungard_content.strip().split('\n')
header = sungard_lines[0]
data_lines = sungard_lines[1:]

# Prepare results
matched_records = []
matched_records.append(header + ";MAPPED_ID")  # Add mapping ID to header

for line in data_lines:
    fields = line.split(';')
    onbehalfof = fields[1]  # ONBEHALFOFCOMPID is the second field
    
    # Check if this ONBEHALFOFCOMPID exists in mapping (ignore '*')
    if onbehalfof != '*' and onbehalfof in mapping_dict:
        matched_records.append(line + ";" + mapping_dict[onbehalfof])

# Print the joined results
print(f"Found {len(matched_records)-1} matching records")
print("\nJoined Results (first 10 rows):")
# for i, record in enumerate(matched_records[:11]):  # Show header + first 10
for i, record in enumerate(matched_records):  # Show header + first 10
    print(record)
    
    if i == 0:
        print("-" * 100)

# Count matches by ONBEHALFOFCOMPID
from collections import Counter
matches_by_id = Counter()
for line in matched_records[1:]:
    fields = line.split(';')
    onbehalfof = fields[1]
    matches_by_id[onbehalfof] += 1

print("\nMatches by ONBEHALFOFCOMPID:")
for comp_id, count in sorted(matches_by_id.items()):
    print(f"{comp_id}: {count} matches (mapped to {mapping_dict[comp_id]})")