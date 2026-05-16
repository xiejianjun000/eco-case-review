"""
多样化测试案例数据集
包含不同类型的生态环境行政处罚案例
"""

# 测试案例数据
TEST_CASES = [
    # 水污染案例
    {
        "id": "case_001",
        "name": "某食品公司篡改自动监测数据案",
        "type": "一般行政处罚",
        "case_type": "water_pollution",
        "violation": "违反《水污染防治法》第三十九条，篡改自动监测数据",
        "document_score": 85,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {
            "company": "某食品有限公司",
            "pollutant": "化学需氧量、氨氮",
            "amount": "超标幅度2-3倍",
            "duration": "2023年12月至2024年5月",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 76.5,
            "suggested_fine": "240000"
        }
    },
    
    # 大气污染案例
    {
        "id": "case_002",
        "name": "某碳素公司大气污染物超标排放案",
        "type": "一般行政处罚",
        "case_type": "air_pollution",
        "violation": "违反《大气污染防治法》第十八条，超标排放大气污染物",
        "document_score": 92,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {
            "company": "某碳素有限公司",
            "pollutant": "烟尘",
            "amount": "超标0.128倍",
            "duration": "2024年3月",
            "location": "河北省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 91.0,
            "suggested_fine": "100000"
        }
    },
    
    # 危险废物案例
    {
        "id": "case_003",
        "name": "跨省转移废铅蓄电池案",
        "type": "移送涉嫌环境污染犯罪",
        "case_type": "hazardous_waste",
        "violation": "违反《固体废物污染环境防治法》相关规定",
        "document_score": 78,
        "document_standard": 100,
        "basic_deduction": 5,
        "data": {
            "company": "某物资回收公司",
            "waste_type": "废铅蓄电池",
            "amount": "约100吨",
            "duration": "2021年至2023年",
            "location": "海南省"
        },
        "expected_result": {
            "legality_pass": False,
            "estimated_score": 45.0,
            "suggested_fine": "2000000"
        }
    },
    
    # 第三方机构造假案例
    {
        "id": "case_004",
        "name": "某检测公司出具虚假监测报告案",
        "type": "一般行政处罚",
        "case_type": "third_party_fraud",
        "violation": "违反《环境监测数据弄虚作假行为判定及处理办法》",
        "document_score": 95,
        "document_standard": 100,
        "basic_deduction": 0,
        "data": {
            "company": "某环境检测有限公司",
            "fraud_type": "采样时间异常，数据伪造",
            "report_count": "多份报告",
            "duration": "2023年8月至2024年4月",
            "location": "广东省"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 95.0,
            "suggested_fine": "100000"
        }
    },
    
    # 建设项目违法案例
    {
        "id": "case_005",
        "name": "未批先建违法生产案",
        "type": "一般行政处罚",
        "case_type": "construction_project",
        "violation": "违反《环境影响评价法》相关规定",
        "document_score": 88,
        "document_standard": 100,
        "basic_deduction": 2,
        "data": {
            "company": "某建材有限公司",
            "project": "新建生产线项目",
            "status": "未环评先建投产",
            "duration": "2024年",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 86.0,
            "suggested_fine": "500000"
        }
    },
    
    # 噪声污染案例
    {
        "id": "case_006",
        "name": "某公司夜间施工噪声污染案",
        "type": "一般行政处罚",
        "case_type": "noise_pollution",
        "violation": "违反《噪声污染防治法》相关规定",
        "document_score": 72,
        "document_standard": 100,
        "basic_deduction": 4,
        "data": {
            "company": "某建筑工程公司",
            "noise_level": "夜间施工超标",
            "duration": "2024年5月",
            "location": "某直辖市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 68.0,
            "suggested_fine": "30000"
        }
    },
    
    # 土壤污染案例
    {
        "id": "case_007",
        "name": "某化工公司土壤污染责任案",
        "type": "一般行政处罚",
        "case_type": "soil_pollution",
        "violation": "违反《土壤污染防治法》相关规定",
        "document_score": 90,
        "document_standard": 100,
        "basic_deduction": 2,
        "data": {
            "company": "某化工有限公司",
            "contaminant": "重金属、有机物",
            "area": "约5000平方米",
            "duration": "2024年",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 88.0,
            "suggested_fine": "1500000"
        }
    },
    
    # 固废污染案例
    {
        "id": "case_008",
        "name": "某养殖场畜禽粪污污染案",
        "type": "一般行政处罚",
        "case_type": "solid_waste",
        "violation": "违反《固体废物污染环境防治法》相关规定",
        "document_score": 65,
        "document_standard": 100,
        "basic_deduction": 6,
        "data": {
            "company": "某生态养殖有限公司",
            "waste_type": "畜禽粪便",
            "amount": "约200吨",
            "duration": "2024年",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": False,
            "estimated_score": 58.0,
            "suggested_fine": "80000"
        }
    },
    
    # 自动监测数据造假案例2
    {
        "id": "case_009",
        "name": "某肉联公司伪造监测数据案",
        "type": "移送涉嫌环境污染犯罪",
        "case_type": "monitoring_fraud",
        "violation": "违反《水污染防治法》第三十九条，伪造监测数据",
        "document_score": 87,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {
            "company": "某肉联实业有限公司",
            "pollutant": "总氮、氨氮",
            "fraud_method": "人工标记设备故障",
            "duration": "2023年12月至2024年2月",
            "location": "海南省三亚市"
        },
        "expected_result": {
            "legality_pass": False,
            "estimated_score": 63.0,
            "suggested_fine": "500000"
        }
    },
    
    # 应急培训缺失案例
    {
        "id": "case_010",
        "name": "某公司未按规定进行环境应急培训案",
        "type": "一般行政处罚",
        "case_type": "emergency_management",
        "violation": "违反《突发环境事件应急管理办法》第十九条",
        "document_score": 93,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {
            "company": "某化工有限公司",
            "issue": "未定期进行环境应急知识培训",
            "duration": "2024年",
            "location": "天津市静海区"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 92.0,
            "suggested_fine": "11000"
        }
    },
    
    # 旁路排放案例
    {
        "id": "case_011",
        "name": "某耐火材料公司旁路偷排废气案",
        "type": "移送公安",
        "case_type": "bypass_emission",
        "violation": "违反《大气污染防治法》第二十条第二款，通过旁路偷排",
        "document_score": 75,
        "document_standard": 100,
        "basic_deduction": 4,
        "data": {
            "company": "某耐火材料有限公司",
            "pollutant": "窑炉废气",
            "detection_method": "无人机巡查",
            "duration": "2023年",
            "location": "山西省阳泉市"
        },
        "expected_result": {
            "legality_pass": False,
            "estimated_score": 56.0,
            "suggested_fine": "320000"
        }
    },
    
    # 机动车检测机构造假案例
    {
        "id": "case_012",
        "name": "某检测公司出具虚假机动车排放检验报告案",
        "type": "一般行政处罚",
        "case_type": "vehicle_testing_fraud",
        "violation": "违反《大气污染防治法》相关规定",
        "document_score": 82,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {
            "company": "某机动车检测有限公司",
            "fraud_type": "未按技术规范检验",
            "report_count": "多份报告",
            "duration": "2024年",
            "location": "河南省献县"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 79.0,
            "suggested_fine": "60000"
        }
    },
    
    # 轻微不予处罚案例
    {
        "id": "case_013",
        "name": "某公司轻微超标且及时整改案",
        "type": "不予行政处罚",
        "case_type": "minor_violation",
        "violation": "轻微超标，首次发现，及时整改",
        "document_score": 91,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {
            "company": "某碳素有限公司",
            "pollutant": "烟尘",
            "amount": "超标0.128倍",
            "remediation": "立即停止维护作业，降低负荷",
            "duration": "2024年3月",
            "location": "河北省"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 90.0,
            "suggested_fine": "0"
        }
    },
    
    # 生态破坏案例
    {
        "id": "case_014",
        "name": "某采石场破坏生态环境案",
        "type": "一般行政处罚",
        "case_type": "ecological_damage",
        "violation": "违反《环境保护法》相关规定",
        "document_score": 80,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {
            "company": "某矿业开发公司",
            "damage_type": "山体破坏、水土流失",
            "area": "约50亩",
            "duration": "2024年",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 77.0,
            "suggested_fine": "800000"
        }
    },
    
    # 辐射安全案例
    {
        "id": "case_015",
        "name": "某医院放射性同位素管理不规范案",
        "type": "一般行政处罚",
        "case_type": "radiation_safety",
        "violation": "违反《放射性污染防治法》相关规定",
        "document_score": 70,
        "document_standard": 100,
        "basic_deduction": 5,
        "data": {
            "company": "某医院",
            "issue": "放射源管理不规范",
            "isotope_type": "Cs-137",
            "duration": "2024年",
            "location": "某省某市"
        },
        "expected_result": {
            "legality_pass": True,
            "estimated_score": 65.0,
            "suggested_fine": "50000"
        }
    }
]

# 案例类型映射
CASE_TYPE_MAPPING = {
    "water_pollution": "水污染防治类",
    "air_pollution": "大气污染防治类",
    "hazardous_waste": "危险废物类",
    "third_party_fraud": "第三方机构造假类",
    "construction_project": "建设项目类",
    "noise_pollution": "噪声污染类",
    "soil_pollution": "土壤污染类",
    "solid_waste": "固体废物类",
    "monitoring_fraud": "监测数据造假类",
    "emergency_management": "应急管理类",
    "bypass_emission": "旁路排放类",
    "vehicle_testing_fraud": "机动车检测类",
    "minor_violation": "轻微违法类",
    "ecological_damage": "生态破坏类",
    "radiation_safety": "辐射安全类"
}

# 案件类型选项
CASE_TYPES = [
    "一般行政处罚",
    "不予行政处罚",
    "按日连续处罚",
    "查封扣押",
    "移送拘留",
    "移送涉嫌环境污染犯罪"
]

# 评分标准配置
SCORING_STANDARDS = {
    "legality_weight": 0.5,
    "normative_weight": 0.5,
    "pass_score": 60,
    "excellent_score": 90,
    "good_score": 80
}
