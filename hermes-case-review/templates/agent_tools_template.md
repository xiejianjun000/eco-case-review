# 智能体工具配置模板

## 概述

**工具（Tools）** 是智能体与外部世界交互的接口，包括系统工具、内置工具和自定义工具。

---

## 模板结构

```markdown
# 工具配置

## 基本信息

**智能体名称**: [名称]
**工具库版本**: v1.0
**更新时间**: [日期]

## 工具清单

### 系统工具（内置）
| 工具名称 | 功能描述 | 权限 |
|----------|----------|------|
| [工具1] | [描述] | [权限级别] |
| [工具2] | [描述] | [权限级别] |

### 专业工具（自定义）
| 工具名称 | 功能描述 | 调用方式 |
|----------|----------|----------|
| [工具1] | [描述] | [调用方式] |
| [工具2] | [描述] | [调用方式] |

## 工具定义

### 工具1
```json
{
  "name": "[工具名称]",
  "description": "[功能描述]",
  "parameters": {
    "param1": {"type": "string", "required": true},
    "param2": {"type": "number", "required": false}
  },
  "output": {
    "format": "json",
    "schema": {}
  }
}
```

## 工具权限
- system: 系统级工具
- professional: 专业工具
- custom: 自定义工具
```

---

## 六个智能体的工具配置

### 1. 合法性审查员工具

```markdown
# 合法性审查员 - 工具配置

## 工具清单

### 系统工具（内置）
| 工具名称 | 功能描述 | 权限 |
|----------|----------|------|
| file_reader | 读取案卷文件 | system |
| web_search | 搜索法律法规 | system |
| database_query | 查询历史案例 | system |
| llm_call | 调用大模型 | system |

### 专业工具（自定义）
| 工具名称 | 功能描述 | 调用方式 |
|----------|----------|----------|
| law_lookup | 法律法规查询 | law_lookup(query="行政处罚法44条") |
| veto_checker | 否决条件检查 | veto_checker(case_data={}) |
| evidence_extractor | 证据提取 | evidence_extractor(content="") |
| legal_citation | 法律引用校验 | legal_citation(article="") |

## 工具定义

### 1. file_reader
```json
{
  "name": "file_reader",
  "description": "读取案卷文件，支持PDF、TXT、JSON格式",
  "parameters": {
    "file_path": {
      "type": "string",
      "required": true,
      "description": "文件路径"
    },
    "format": {
      "type": "string",
      "required": false,
      "description": "文件格式，auto自动检测"
    }
  },
  "output": {
    "format": "text",
    "example": "案卷文本内容..."
  }
}
```

### 2. law_lookup
```json
{
  "name": "law_lookup",
  "description": "查询相关法律法规条款",
  "parameters": {
    "query": {
      "type": "string",
      "required": true,
      "description": "查询关键词"
    },
    "category": {
      "type": "string",
      "required": false,
      "description": "法律类别"
    }
  },
  "output": {
    "format": "json",
    "example": {
      "law_name": "行政处罚法",
      "article": "第44条",
      "content": "当事人在作出行政处罚决定之前...",
      "source": "全国人大常委会"
    }
  }
}
```

### 3. veto_checker
```json
{
  "name": "veto_checker",
  "description": "检查是否触发一票否决条件",
  "parameters": {
    "case_data": {
      "type": "object",
      "required": true,
      "description": "案卷数据"
    },
    "check_items": {
      "type": "array",
      "required": false,
      "description": "指定检查项，默认为全部25项"
    }
  },
  "output": {
    "format": "json",
    "example": {
      "has_veto": true,
      "veto_items": [
        {"number": 14, "description": "未告知程序性权利"}
      ]
    }
  }
}
```

### 4. evidence_extractor
```json
{
  "name": "evidence_extractor",
  "description": "从案卷内容中提取证据信息",
  "parameters": {
    "content": {
      "type": "string",
      "required": true,
      "description": "案卷文本内容"
    }
  },
  "output": {
    "format": "json",
    "example": {
      "evidence_list": [
        {
          "type": "现场检查笔录",
          "pages": "第3-5页",
          "key_info": "检测到超标排放"
        }
      ]
    }
  }
}
```

### 5. legal_citation
```json
{
  "name": "legal_citation",
  "description": "校验法律条款引用的准确性",
  "parameters": {
    "article": {
      "type": "string",
      "required": true,
      "description": "法律条款引用"
    },
    "context": {
      "type": "string",
      "required": false,
      "description": "使用上下文"
    }
  },
  "output": {
    "format": "json",
    "example": {
      "valid": true,
      "law_name": "行政处罚法",
      "article": "第44条",
      "title": "告知程序",
      "content": "当事人权利告知条款..."
    }
  }
}
```

## 工具调用示例

```python
# Python 调用示例
result = await law_lookup(query="陈述申辩权")
print(result)

result = await veto_checker(case_data=case_data)
print(f"是否否决: {result['has_veto']}")
```

## 工具使用权限

| 工具类型 | 权限级别 | 说明 |
|----------|----------|------|
| file_reader | system | 所有智能体可用 |
| web_search | system | 所有智能体可用 |
| database_query | system | 需要数据库权限 |
| law_lookup | professional | 专业工具 |
| veto_checker | professional | 专业工具 |
| evidence_extractor | professional | 专业工具 |
| legal_citation | professional | 专业工具 |
```
