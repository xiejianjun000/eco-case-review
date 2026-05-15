SENSITIVE_FIELDS = [
    "当事人名称",
    "法定代表人",
    "身份证号",
    "电话号码",
    "银行账号",
    "处罚金额"
]

def sanitize_output(report: dict) -> dict:
    for field in SENSITIVE_FIELDS:
        if field in report:
            report[field] = mask(report[field])
    return report

def mask(value: str) -> str:
    if not value or len(value) <= 4:
        return "*" * len(value) if value else ""
    return value[:2] + "*" * (len(value) - 4) + value[-2:]
