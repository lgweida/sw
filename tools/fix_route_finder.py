import csv
import os
import argparse
from collections import defaultdict

class FixRouteFinder:
    def __init__(self, rules_dir):
        """初始化路由查找器，加载指定目录下的所有路由规则"""
        self.rules_dir = rules_dir
        self.routing_rules = defaultdict(list)  # 按网络名称组织规则
        self.field_mapping = {
            # 可以添加FIX标签到字段名的映射，如果需要的话
            # 例如: '35' : 'MSG_TYPE',
        }
        self.load_all_rules()
        
    def load_all_rules(self):
        """加载目录中所有的路由规则CSV文件"""
        try:
            # 获取目录中所有以alias_开头且以.csv结尾的文件
            for filename in os.listdir(self.rules_dir):
                if filename.startswith('alias_') and filename.endswith('.csv'):
                    network_name = filename[len('alias_'):-len('.csv')]
                    file_path = os.path.join(self.rules_dir, filename)
                    self._load_rules_from_file(network_name, file_path)
                    
            print(f"成功加载 {len(self.routing_rules)} 个网络的路由规则")
            
        except Exception as e:
            print(f"加载路由规则时出错: {str(e)}")
            raise
    
    def _load_rules_from_file(self, network, file_path):
        """从单个CSV文件加载路由规则"""
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # 检测CSV文件使用的分隔符
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                rules_count = 0
                
                for row in reader:
                    # 提取目标地址
                    destination = row.get('DESTINATION')
                    if not destination:
                        continue
                        
                    # 构建规则条件（排除DESTINATION本身）
                    conditions = {k: v.strip() for k, v in row.items() if k != 'DESTINATION' and v.strip()}
                    
                    # 添加到规则集合
                    self.routing_rules[network].append({
                        'conditions': conditions,
                        'destination': destination
                    })
                    rules_count += 1
                
                print(f"从 {file_path} 加载了 {rules_count} 条规则 (网络: {network})")
                
        except Exception as e:
            print(f"加载文件 {file_path} 时出错: {str(e)}")
    
    def _parse_fix_message(self, fix_string):
        """解析FIX格式的消息字符串为字典"""
        # 简单的FIX消息解析，假设字段以|分隔，格式为标签=值
        # 实际应用中可能需要更复杂的解析逻辑
        fix_fields = {}
        for field in fix_string.split('|'):
            if '=' in field:
                tag, value = field.split('=', 1)
                # 使用字段映射转换标签为名称，如果有的话
                field_name = self.field_mapping.get(tag, tag)
                fix_fields[field_name] = value.strip()
        return fix_fields
    
    def _calculate_match_score(self, fix_message, rule_conditions):
        """计算FIX消息与规则条件的匹配分数"""
        score = 0
        total_conditions = len(rule_conditions)
        
        if total_conditions == 0:
            return 0  # 没有条件的规则不参与匹配
        
        for field, required_value in rule_conditions.items():
            # 获取FIX消息中的对应字段值
            message_value = fix_message.get(field)
            
            if message_value is None:
                # 消息中没有该字段，不匹配
                continue
                
            if required_value == '*':
                # 通配符匹配，给予基础分数
                score += 1
            elif required_value == message_value:
                # 精确匹配，给予更高分数
                score += 3
            elif '*' in required_value:
                # 部分通配符匹配（如ABC*）
                pattern = required_value.replace('*', '')
                if message_value.startswith(pattern) or message_value.endswith(pattern):
                    score += 2
        
        # 计算匹配百分比
        return (score / (total_conditions * 3)) * 100 if total_conditions > 0 else 0
    
    def find_best_route(self, fix_input):
        """
        为给定的FIX消息找到最佳路由
        fix_input可以是字符串或已解析的字典
        """
        # 如果输入是字符串，则解析为字典
        if isinstance(fix_input, str):
            fix_message = self._parse_fix_message(fix_input)
        else:
            fix_message = fix_input
            
        best_route = None
        highest_score = 0
        
        # 检查所有网络的所有规则
        for network, rules in self.routing_rules.items():
            for rule in rules:
                score = self._calculate_match_score(fix_message, rule['conditions'])
                
                # 更新最佳路由
                if score > highest_score and score > 0:
                    highest_score = score
                    best_route = {
                        'network': network,
                        'destination': rule['destination'],
                        'match_score': round(score, 2),
                        'conditions_matched': rule['conditions']
                    }
        
        return best_route

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='FIX消息路由路径查找器')
    parser.add_argument('rules_directory', help='包含路由规则CSV文件的目录路径')
    args = parser.parse_args()
    
    # 验证目录是否存在
    if not os.path.isdir(args.rules_directory):
        print(f"错误: 目录 {args.rules_directory} 不存在")
        return
    
    # 初始化路由查找器
    try:
        route_finder = FixRouteFinder(args.rules_directory)
    except Exception as e:
        print(f"初始化路由查找器失败: {str(e)}")
        return
    
    # 示例1: 使用字典形式的FIX消息
    example_fix_dict = {
        'ULFOMSESSIONNAME': 'Session123',
        'HANDLINST': 'FlextradeAlgoFix42',
        'FIX.5847': 'broker',
        'TARGETSUBID': 'FROG',
        'CURRENCY': 'USD',
        'ONBEHALFOFCOMPID': 'MHFEUAG',
        'SENDERCOMPID': 'BFGICRD',
        'ETF': 'yes',
        'COUNTRYCODE': 'US'
    }
    
    print("\n=== 测试示例1 (字典形式的FIX消息) ===")
    best_route = route_finder.find_best_route(example_fix_dict)
    if best_route:
        print(f"最佳路由网络: {best_route['network']}")
        print(f"目标地址: {best_route['destination']}")
        print(f"匹配分数: {best_route['match_score']}%")
        print("匹配的条件:")
        for k, v in best_route['conditions_matched'].items():
            print(f"  {k}: {v}")
    else:
        print("未找到匹配的路由规则")
    
    # 示例2: 使用FIX字符串形式的消息
    example_fix_string = (
        "ULFOMSESSIONNAME=Session456|HANDLINST=FlextradeAlgoFix42|FIX.5847=broker|"
        "TARGETSUBID=FROG|CURRENCY=USD|ONBEHALFOFCOMPID=SomeComp|SENDERCOMPID=BFGICRD|"
        "ETF=yes|COUNTRYCODE=US"
    )
    
    print("\n=== 测试示例2 (FIX字符串形式的消息) ===")
    best_route = route_finder.find_best_route(example_fix_string)
    if best_route:
        print(f"最佳路由网络: {best_route['network']}")
        print(f"目标地址: {best_route['destination']}")
        print(f"匹配分数: {best_route['match_score']}%")
        print("匹配的条件:")
        for k, v in best_route['conditions_matched'].items():
            print(f"  {k}: {v}")
    else:
        print("未找到匹配的路由规则")

if __name__ == "__main__":
    main()
