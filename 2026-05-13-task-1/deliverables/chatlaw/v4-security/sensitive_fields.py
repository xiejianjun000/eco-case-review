"""
V4 行政处罚案卷评查系统 - 敏感信息脱敏模块
"""

SENSITIVE_FIELDS = [
    "当事人名称",
    "法定代表人",
    "身份证号",
    "电话号码",
    "银行账号",
    "处罚金额",
    "地址",
    "邮箱"
]

def sanitize_output(report: dict) -> dict:
    """
    脱敏处理输出报告
    
    Args:
        report: 原始报告字典
        
    Returns:
        脱敏后的报告字典
    """
    sanitized = report.copy()
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = mask(sanitized[field])
    return sanitized

def mask(value: str) -> str:
    """
    脱敏掩码处理
    
    Args:
        value: 原始值
        
    Returns:
        脱敏后的值
    """
    if not value:
        return value
    
    length = len(value)
    
    # 长度<=4，全部掩码
    if length <= 4:
        return "*" * length
    
    # 长度>4，保留首尾
    return value[:2] + "*" * (length - 4) + value[-2:]

def mask_amount(amount: float) -> str:
    """
    金额掩码（保留整数位）
    
    Args:
        amount: 原始金额
        
    Returns:
        脱敏后的金额字符串
    """
    if amount <= 0:
        return "0"
    
    # 大金额只显示数量级
    if amount >= 10000:
        return f"{int(amount / 10000)}万"
    
    return f"{int(amount)}"

def sanitize_case_report(case_report: dict, role: str = "user") -> dict:
    """
    根据角色脱敏报告
    
    Args:
        case_report: 案件报告
        role: 用户角色
        
    Returns:
        脱敏后的报告
    """
    # 管理员不脱敏
    if role == "admin":
        return case_report
    
    # 评查员/审计员部分脱敏
    if role in ["reviewer", "auditor"]:
        result = case_report.copy()
        for field in ["身份证号", "银行账号"]:
            if field in result:
                result[field] = mask(result[field])
        return result
    
    # 普通用户全部脱敏
    return sanitize_output(case_report)
