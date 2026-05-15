"""
裁量基准计算模块 - 计算罚款金额合理性
"""
from typing import Dict, List, Any, Optional
from loguru import logger
import json
from pathlib import Path


class DiscretionCalculator:
    """裁量基准计算器 - 计算罚款金额合理性"""
    
    def __init__(self):
        self.discretion_tables = self._load_discretion_tables()
    
    def _load_discretion_tables(self) -> Dict[str, Any]:
        """加载裁量基准表"""
        # 默认裁量基准数据
        default_tables = {
            '大气污染': {
                'base_fine': {'min': 10, 'max': 100},  # 万元
                'factors': {
                    '超标倍数': [
                        {'range': '≤1', 'percentage': 0.1},
                        {'range': '1-2', 'percentage': 0.25},
                        {'range': '2-3', 'percentage': 0.4},
                        {'range': '3-5', 'percentage': 0.6},
                        {'range': '5-10', 'percentage': 0.8},
                        {'range': '>10', 'percentage': 1.0}
                    ],
                    '改正情况': [
                        {'value': '立即改正', 'percentage': -0.1},
                        {'value': '限期改正', 'percentage': 0},
                        {'value': '拒不改正', 'percentage': 0.2}
                    ],
                    '主观过错': [
                        {'value': '故意', 'percentage': 0.2},
                        {'value': '过失', 'percentage': 0},
                        {'value': '无过错', 'percentage': -0.15}
                    ],
                    '影响范围': [
                        {'value': '轻微', 'percentage': -0.1},
                        {'value': '一般', 'percentage': 0},
                        {'value': '较大', 'percentage': 0.15},
                        {'value': '重大', 'percentage': 0.3}
                    ],
                    '配合程度': [
                        {'value': '积极配合', 'percentage': -0.1},
                        {'value': '一般', 'percentage': 0},
                        {'value': '拒不配合', 'percentage': 0.15}
                    ]
                }
            },
            '水污染': {
                'base_fine': {'min': 20, 'max': 200},
                'factors': {
                    '超标倍数': [
                        {'range': '≤1', 'percentage': 0.1},
                        {'range': '1-2', 'percentage': 0.25},
                        {'range': '2-5', 'percentage': 0.45},
                        {'range': '5-10', 'percentage': 0.7},
                        {'range': '>10', 'percentage': 1.0}
                    ],
                    '改正情况': [
                        {'value': '立即改正', 'percentage': -0.1},
                        {'value': '限期改正', 'percentage': 0},
                        {'value': '拒不改正', 'percentage': 0.2}
                    ],
                    '主观过错': [
                        {'value': '故意', 'percentage': 0.2},
                        {'value': '过失', 'percentage': 0},
                        {'value': '无过错', 'percentage': -0.15}
                    ],
                    '影响范围': [
                        {'value': '轻微', 'percentage': -0.1},
                        {'value': '一般', 'percentage': 0},
                        {'value': '较大', 'percentage': 0.15},
                        {'value': '重大', 'percentage': 0.3}
                    ],
                    '配合程度': [
                        {'value': '积极配合', 'percentage': -0.1},
                        {'value': '一般', 'percentage': 0},
                        {'value': '拒不配合', 'percentage': 0.15}
                    ]
                }
            },
            '固废污染': {
                'base_fine': {'min': 10, 'max': 100},
                'factors': {
                    '数量规模': [
                        {'range': '<1吨', 'percentage': 0.15},
                        {'range': '1-5吨', 'percentage': 0.35},
                        {'range': '5-10吨', 'percentage': 0.55},
                        {'range': '10-50吨', 'percentage': 0.75},
                        {'range': '>50吨', 'percentage': 1.0}
                    ],
                    '改正情况': [
                        {'value': '立即改正', 'percentage': -0.1},
                        {'value': '限期改正', 'percentage': 0},
                        {'value': '拒不改正', 'percentage': 0.2}
                    ],
                    '危害后果': [
                        {'value': '无', 'percentage': -0.1},
                        {'value': '轻微', 'percentage': 0},
                        {'value': '一般', 'percentage': 0.15},
                        {'value': '严重', 'percentage': 0.3}
                    ]
                }
            },
            '噪声污染': {
                'base_fine': {'min': 2, 'max': 20},
                'factors': {
                    '超标分贝': [
                        {'range': '≤3', 'percentage': 0.2},
                        {'range': '3-5', 'percentage': 0.4},
                        {'range': '5-10', 'percentage': 0.65},
                        {'range': '>10', 'percentage': 1.0}
                    ],
                    '持续时间': [
                        {'range': '<1小时', 'percentage': 0.3},
                        {'range': '1-4小时', 'percentage': 0.5},
                        {'range': '4-12小时', 'percentage': 0.75},
                        {'range': '>12小时', 'percentage': 1.0}
                    ]
                }
            }
        }
        
        # 尝试从文件加载
        tables_file = Path(__file__).parent.parent / 'config' / 'standards' / 'discretion_base.json'
        if tables_file.exists():
            try:
                with open(tables_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_tables.update(loaded)
            except Exception as e:
                logger.warning(f"加载裁量基准表失败，使用默认值: {e}")
        
        return default_tables
    
    def calculate(self, violation_type: str, case_data: Dict) -> Dict[str, Any]:
        """
        计算裁量金额
        
        Args:
            violation_type: 违法行为类型
            case_data: 案件数据
            
        Returns:
            裁量计算结果
        """
        result = {
            'success': False,
            'violation_type': violation_type,
            'applicable': False,
            'legal_range': '',
            'factors': [],
            'total_percentage': 0,
            'calculated_fine': 0,
            'recorded_fine': 0,
            'fine_difference': 0,
            'reasonableness': '未知',
            'notes': []
        }
        
        try:
            # 获取裁量基准表
            if violation_type not in self.discretion_tables:
                result['notes'].append(f"未找到'{violation_type}'的裁量基准表")
                return result
            
            table = self.discretion_tables[violation_type]
            result['applicable'] = True
            result['legal_range'] = f"{table['base_fine']['min']}-{table['base_fine']['max']}万元"
            
            # 获取记录的罚款金额
            result['recorded_fine'] = case_data.get('penalty_amount', 0)
            
            # 计算各因素的裁量百分值
            total_percentage = 0.3  # 基础百分值（起罚点）
            factors = []
            
            for factor_name, factor_options in table['factors'].items():
                case_value = case_data.get(factor_name, '')
                matched_option = None
                
                for option in factor_options:
                    if 'range' in option:
                        # 范围匹配
                        if self._match_range(case_value, option['range']):
                            matched_option = option
                            break
                    elif 'value' in option:
                        # 值匹配
                        if case_value == option['value']:
                            matched_option = option
                            break
                
                if matched_option:
                    percentage = matched_option['percentage']
                    total_percentage += percentage
                    factors.append({
                        'factor_name': factor_name,
                        'case_value': case_value,
                        'matched_range': matched_option.get('range') or matched_option.get('value'),
                        'percentage': percentage
                    })
                else:
                    factors.append({
                        'factor_name': factor_name,
                        'case_value': case_value,
                        'matched_range': '未匹配',
                        'percentage': 0,
                        'note': '未找到匹配项，使用默认值'
                    })
            
            # 限制百分值范围
            total_percentage = max(0.1, min(total_percentage, 1.0))
            
            # 计算罚款金额
            base_min = table['base_fine']['min']
            base_max = table['base_fine']['max']
            calculated_fine = base_min + (base_max - base_min) * total_percentage
            
            # 保存结果
            result['factors'] = factors
            result['total_percentage'] = round(total_percentage, 2)
            result['calculated_fine'] = round(calculated_fine, 2)
            
            # 计算差异
            if result['recorded_fine'] > 0:
                result['fine_difference'] = round(result['recorded_fine'] - calculated_fine, 2)
                
                # 判断合理性
                difference_ratio = abs(result['fine_difference']) / calculated_fine if calculated_fine > 0 else 1
                if difference_ratio <= 0.1:
                    result['reasonableness'] = '合理'
                elif difference_ratio <= 0.25:
                    result['reasonableness'] = '基本合理'
                elif difference_ratio <= 0.5:
                    result['reasonableness'] = '存在偏差'
                else:
                    result['reasonableness'] = '明显不合理'
            
            result['success'] = True
            
        except Exception as e:
            logger.error(f"裁量计算失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _match_range(self, value: str, range_str: str) -> bool:
        """匹配范围"""
        try:
            # 移除单位，提取数字
            num_value = self._extract_number(value)
            
            if num_value is None:
                return False
            
            # 解析范围
            range_str = range_str.strip()
            
            # 处理 ">X" 或 "<X" 格式
            if range_str.startswith('>'):
                threshold = float(range_str[1:])
                return num_value > threshold
            elif range_str.startswith('<'):
                threshold = float(range_str[1:])
                return num_value < threshold
            elif range_str.startswith('≤'):
                threshold = float(range_str[1:])
                return num_value <= threshold
            elif range_str.startswith('≥'):
                threshold = float(range_str[1:])
                return num_value >= threshold
            
            # 处理 "X-Y" 格式
            if '-' in range_str:
                parts = range_str.split('-')
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return min_val <= num_value <= max_val
            
            # 处理 "≤X" 格式
            if '≤' in range_str:
                threshold = float(range_str.replace('≤', '').strip())
                return num_value <= threshold
            
            return False
            
        except Exception:
            return False
    
    def _extract_number(self, value: str) -> Optional[float]:
        """从字符串中提取数字"""
        import re
        
        if not value:
            return None
        
        # 提取数字（支持中文数字）
        match = re.search(r'([\d.]+)', value)
        if match:
            return float(match.group(1))
        
        return None


# 全局实例
discretion_calculator = DiscretionCalculator()
