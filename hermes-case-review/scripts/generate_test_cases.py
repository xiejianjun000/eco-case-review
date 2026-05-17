#!/usr/bin/env python3
"""
HERMES 1000份生态环境案例生成器
基于真实案例数据生成用于压力测试的案例数据
"""
import json
import random
import os
from datetime import datetime, timedelta

class CaseGenerator:
    """案例生成器"""

    # 地区数据
    PROVINCES = [
        "北京市", "天津市", "河北省", "山西省", "内蒙古",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区"
    ]

    CITIES = {
        "北京市": ["北京市"],
        "天津市": ["天津市"],
        "河北省": ["石家庄市", "唐山市", "秦皇岛市", "邯郸市", "邢台市", "保定市", "张家口市", "承德市", "沧州市", "廊坊市", "衡水市"],
        "山西省": ["太原市", "大同市", "阳泉市", "长治市", "晋城市", "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市"],
        "内蒙古": ["呼和浩特市", "包头市", "乌海市", "赤峰市", "通辽市", "鄂尔多斯市", "呼伦贝尔市", "巴彦淖尔市", "乌兰察布市"],
        "辽宁省": ["沈阳市", "大连市", "鞍山市", "抚顺市", "本溪市", "丹东市", "锦州市", "营口市", "阜新市", "辽阳市", "盘锦市", "铁岭市", "朝阳市", "葫芦岛市"],
        "吉林省": ["长春市", "吉林市", "四平市", "辽源市", "通化市", "白山式", "松原市", "白城市", "延边朝鲜族自治州"],
        "黑龙江省": ["哈尔滨市", "齐齐哈尔市", "鸡西市", "鹤岗市", "双鸭山市", "大庆市", "伊春市", "佳木斯市", "七台河市", "牡丹江市", "黑河市", "绥化市"],
        "上海市": ["上海市"],
        "江苏省": ["南京市", "无锡市", "徐州市", "常州市", "苏州市", "南通市", "连云港市", "淮安市", "盐城市", "扬州市", "镇江市", "泰州市", "宿迁市"],
        "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "衢州市", "舟山市", "台州市", "丽水市"],
        "安徽省": ["合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市", "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市", "阜阳市", "宿州市", "六安市", "亳州市", "池州市", "宣城市"],
        "福建省": ["福州市", "厦门市", "莆田市", "三明市", "泉州市", "漳州市", "南平市", "龙岩市", "宁德市"],
        "江西省": ["南昌市", "景德镇市", "萍乡市", "九江市", "新余市", "鹰潭市", "赣州市", "吉安市", "宜春市", "抚州市", "上饶市"],
        "山东省": ["济南市", "青岛市", "淄博市", "枣庄市", "东营市", "烟台市", "潍坊市", "济宁市", "泰安市", "威海市", "日照市", "临沂市", "德州市", "聊城市", "滨州市", "菏泽市"],
        "河南省": ["郑州市", "开封市", "洛阳市", "平顶山市", "安阳市", "鹤壁市", "新乡市", "焦作市", "濮阳市", "许昌市", "漯河市", "三门峡市", "南阳市", "商丘市", "信阳市", "周口市", "驻马店市"],
        "湖北省": ["武汉市", "黄石市", "十堰市", "宜昌市", "襄阳市", "鄂州市", "荆门市", "孝感市", "荆州市", "黄冈市", "咸宁市", "随州市", "恩施土家族苗族自治州"],
        "湖南省": ["长沙市", "株洲市", "湘潭市", "衡阳市", "邵阳市", "岳阳市", "常德市", "张家界市", "益阳市", "郴州市", "永州市", "怀化市", "娄底市", "湘西土家族苗族自治州"],
        "广东省": ["广州市", "深圳市", "珠海市", "汕头市", "佛山市", "韶关市", "湛江市", "肇庆市", "江门市", "茂名市", "惠州市", "梅州市", "汕尾市", "河源市", "阳江市", "清远市", "东莞市", "中山市", "潮州市", "揭阳市", "云浮市"],
        "广西壮族自治区": ["南宁市", "柳州市", "桂林市", "梧州市", "北海市", "防城港市", "钦州市", "贵港市", "玉林市", "百色市", "贺州市", "河池市", "来宾市", "崇左市"],
        "海南省": ["海口市", "三亚市", "三沙市", "儋州市"],
        "重庆市": ["重庆市"],
        "四川省": ["成都市", "自贡市", "攀枝花市", "泸州市", "德阳市", "绵阳市", "广元市", "遂宁市", "内江市", "乐山市", "南充市", "眉山市", "宜宾市", "广安市", "达州市", "雅安市", "巴中市", "资阳市", "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"],
        "贵州省": ["贵阳市", "六盘水市", "遵义市", "安顺市", "毕节市", "铜仁市", "黔西南布依族苗族自治州", "黔东南苗族侗族自治州", "黔南布依族苗族自治州"],
        "云南省": ["昆明市", "曲靖市", "玉溪市", "保山市", "昭通市", "丽江市", "普洱市", "临沧市", "楚雄彝族自治州", "红河哈尼族彝族自治州", "文山壮族苗族自治州", "西双版纳傣族自治州", "大理白族自治州", "德宏傣族景颇族自治州", "怒江傈僳族自治州", "迪庆藏族自治州"],
        "陕西省": ["西安市", "铜川市", "宝鸡市", "咸阳市", "渭南市", "延安市", "汉中市", "榆林市", "安康市", "商洛市"],
        "甘肃省": ["兰州市", "嘉峪关市", "金昌市", "白银市", "天水市", "武威市", "张掖市", "平凉市", "酒泉市", "庆阳市", "定西市", "陇南市", "临夏回族自治州", "甘南藏族自治州"],
        "青海省": ["西宁市", "海东市", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"],
        "宁夏回族自治区": ["银川市", "石嘴山市", "吴忠市", "固原市", "中卫市"],
        "新疆维吾尔自治区": ["乌鲁木齐市", "克拉玛依市", "吐鲁番市", "哈密市", "阿克苏地区", "喀什地区", "和田地区", "伊犁哈萨克自治州", "塔城地区", "阿勒泰地区"]
    }

    # 企业名称模板
    COMPANY_TYPES = [
        "化工有限公司", "建材有限公司", "印染有限公司", "电镀有限公司", "造纸有限公司",
        "食品有限公司", "制药有限公司", "电子有限公司", "机械有限公司", "金属有限公司",
        "矿业有限公司", "冶炼有限公司", "铸造有限公司", "塑料有限公司", "橡胶有限公司",
        "皮革有限公司", "木业有限公司", "水泥有限公司", "石材有限公司", "玻璃有限公司",
        "陶瓷有限公司", "饲料有限公司", "养殖有限公司", "医院", "学校", "酒店",
        "污水处理厂", "垃圾处理厂", "检测技术有限公司", "环保科技有限公司",
        "机动车检测有限公司", "汽车维修服务有限公司", "加油站", "运输有限公司"
    ]

    COMPANY_NAMES = [
        "鑫顺", "华泰", "金山", "银河", "宏达", "盛源", "正达", "华盛", "中天", "恒通",
        "诚信", "创新", "飞跃", "超越", "卓越", "祥瑞", "祥和", "德盛", "瑞丰", "福源",
        "永昌", "永盛", "永信", "永达", "永成", "永泰", "永华", "永利", "永安", "永昌",
        "三元", "三友", "三利", "三和", "三维", "三元", "四方", "四通", "四海", "四季",
        "新兴", "新华", "新宇", "新锐", "新科", "新艺", "新星", "新阳", "新材", "新能",
        "东升", "东方", "东海", "东南", "东北", "西北", "西南", "东阳", "东岳", "东华",
        "南洋", "南方", "南山", "南湖", "南粤", "南岭", "南岳", "南津", "南宁", "南昌",
        "北辰", "北控", "北创", "北科", "北铃", "北大", "北纬", "北电", "北车", "北重"
    ]

    # 违法行为类型
    VIOLATION_TYPES = {
        "大气污染类": {
            "patterns": [
                "超标排放大气污染物",
                "通过逃避监管的方式排放大气污染物",
                "未按规定使用污染防治设施",
                "未取得排污许可证排放大气污染物",
                "未按规定安装自动监测设备",
                "自动监测设备数据弄虚作假",
                "露天堆放易产生扬尘的物料未采取有效防尘措施",
                "未采取密闭措施控制扬尘排放"
            ],
            "laws": ["《大气污染防治法》第九十九条", "《大气污染防治法》第一百零八条"]
        },
        "水污染类": {
            "patterns": [
                "超标排放水污染物",
                "通过逃避监管的方式排放水污染物",
                "未取得排污许可证排放水污染物",
                "私设暗管排放水污染物",
                "水污染物处理设施不正常运行",
                "向水体倾倒废弃物",
                "超标排放畜禽养殖废弃物"
            ],
            "laws": ["《水污染防治法》第八十三条", "《水污染防治法》第八十四条"]
        },
        "固体废物类": {
            "patterns": [
                "擅自倾倒工业固体废物",
                "未采取相应防范措施造成工业固体废物扬散",
                "将危险废物提供或者委托给无经营许可证的单位从事经营活动",
                "未按规定贮存危险废物",
                "危险废物与一般废物混放",
                "转移固体废物出省、自治区、直辖市行政区域贮存、处置未经批准",
                "未建立工业固体废物管理台账"
            ],
            "laws": ["《固体废物污染环境防治法》第一百零二条", "《固体废物污染环境防治法》第一百零三条"]
        },
        "土壤污染类": {
            "patterns": [
                "土壤污染地块未进行风险管控和修复",
                "重金属污染物排放超过污染物排放标准",
                "非法处置被污染土壤",
                "向沙化土地排放污染物"
            ],
            "laws": ["《土壤污染防治法》第八十六条", "《土壤污染防治法》第八十七条"]
        },
        "噪声污染类": {
            "patterns": [
                "超标排放工业噪声",
                "夜间施工未取得夜间施工证明",
                "未按规定采取噪声污染防治措施"
            ],
            "laws": ["《噪声污染防治法》第七十五条", "《噪声污染防治法》第七十六条"]
        },
        "辐射污染类": {
            "patterns": [
                "辐射工作单位未按照规定办理辐射安全许可证",
                "擅自转让放射性同位素",
                "未按规定对辐射工作人员进行个人剂量监测"
            ],
            "laws": ["《放射性污染防治法》", "《放射性同位素与射线装置安全和防护条例》"]
        },
        "环评类": {
            "patterns": [
                "建设项目未依法报批环境影响评价文件擅自开工建设",
                "建设项目需要配套建设的环境保护设施未经验收合格即投入生产",
                "未重新报批环境影响评价文件",
                "建设项目环境影响评价文件经批准后发生重大变动未重新报批"
            ],
            "laws": ["《环境影响评价法》第三十一条", "《建设项目环境保护管理条例》第二十二条"]
        },
        "排污许可类": {
            "patterns": [
                "未取得排污许可证排放污染物",
                "排污许可证有效期届满未申请延续",
                "未按照排污许可证规定提交排污许可证执行报告",
                "未按照排污许可证规定制定自行监测方案",
                "未按照排污许可证规定开展自行监测并保存原始监测记录"
            ],
            "laws": ["《排污许可管理条例》第三十三条", "《排污许可管理条例》第三十四条"]
        },
        "监测数据类": {
            "patterns": [
                "篡改监测数据",
                "伪造监测数据",
                "出具虚假监测报告",
                "未保证监测设备正常运行"
            ],
            "laws": ["《环境监测管理办法》", "《环境保护法》第六十三条"]
        },
        "第三方机构类": {
            "patterns": [
                "环境监测机构出具虚假监测报告",
                "第三方环保服务机构弄虚作假",
                "验收监测机构出具虚假验收报告"
            ],
            "laws": ["《环境监测管理办法》", "《环境保护法》"]
        }
    }

    # 行业分类
    INDUSTRIES = [
        "制造业-化学原料和化学制品制造业",
        "制造业-纺织业",
        "制造业-皮革、毛皮、羽毛及其制品和制鞋业",
        "制造业-造纸和纸制品业",
        "制造业-印刷和记录媒介复制业",
        "制造业-石油加工、炼焦和核燃料加工业",
        "制造业-非金属矿物制品业",
        "制造业-黑色金属冶炼和压延加工业",
        "制造业-有色金属冶炼和压延加工业",
        "制造业-金属制品业",
        "制造业-通用设备制造业",
        "制造业-专用设备制造业",
        "制造业-汽车制造业",
        "制造业-电气机械和器材制造业",
        "电力、热力、燃气及水生产和供应业",
        "采矿业-煤炭开采和洗选业",
        "采矿业-黑色金属矿采选业",
        "采矿业-有色金属矿采选业",
        "采矿业-非金属矿采选业",
        "建筑业",
        "交通运输、仓储和邮政业",
        "住宿和餐饮业",
        "水利、环境和公共设施管理业",
        "居民服务、修理和其他服务业"
    ]

    def __init__(self, count=1000):
        self.count = count
        self.case_id = 0

    def generate_company_name(self):
        """生成企业名称"""
        prefix = random.choice(self.COMPANY_NAMES)
        suffix = random.choice(self.COMPANY_TYPES)
        province_short = random.choice(["省", "市", "县"])
        return f"{prefix}{suffix}"

    def generate_case_number(self, province_short, year, month):
        """生成案号"""
        regions = ["环罚", "环罚字", "环境罚", "生态罚"]
        region = random.choice(regions)
        num = random.randint(1, 999)
        return f"{province_short}{region}〔{year}〕{num:03d}号"

    def generate_case_content(self, violation_type_data, company_name, province, city, year, month):
        """生成完整案例内容"""
        self.case_id += 1

        violation_pattern = random.choice(violation_type_data["patterns"])
        law = random.choice(violation_type_data["laws"])

        penalty_amount = random.randint(2, 100) * 10000
        if violation_pattern == "通过逃避监管的方式排放大气污染物":
            penalty_amount = random.randint(20, 100) * 10000
        elif violation_pattern == "出具虚假监测报告":
            penalty_amount = random.randint(3, 30) * 10000

        penalty_base = penalty_amount
        discretion_level = random.choice(["从轻", "一般", "从重"])

        case_content = f"""
生态环境行政处罚案卷
========================================

【基本信息】
案卷编号：{self.generate_case_number(province[:2], year, month)}
案卷名称：{company_name}{violation_pattern}案
案件类型：行政处罚
被处罚单位：{company_name}
统一社会信用代码：91350{random.randint(100000000, 999999999)}
法定代表人：{random.choice(['张', '王', '李', '刘', '陈', '杨', '黄', '赵', '周', '吴'])}{random.choice(['明', '华', '伟', '强', '军', '勇', '杰', '涛', '超', '鹏'])}
地址：{city}{random.choice(['工业园区', '高新技术产业开发区', '经济技术开发区', '镇'])}{random.choice(['路', '街', '大道'])}{random.randint(1, 999)}号
所属行业：{random.choice(self.INDUSTRIES)}

【执法机关】
机关名称：{city}生态环境局
执法人员：{random.choice(['张三', '李四', '王五', '赵六', '钱七'])}、{random.choice(['孙八', '周九', '吴十', '郑一', '王二'])}
执法证号：{random.randint(100000, 999999)}

【违法事实】
违法时间：{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日
违法地点：{company_name}厂区内
违法事实：
{company_name}于{yeah}年{random.randint(1, 12)}月，因{violation_pattern}，违反了相关环境保护法律规定。

【现场检查笔录】
检查日期：{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日
检查人员：{random.choice(['张三', '李四', '王五'])}、{random.choice(['赵六', '钱七', '孙八'])}
检查内容：
执法人员对该公司进行现场检查，发现该公司正常生产，{violation_pattern}。

【调查询问笔录】
询问日期：{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日
被询问人：{random.choice(['张总', '李厂长', '王经理'])}（公司环保负责人）
询问内容：
承认违法事实，表示因管理疏忽导致，愿意配合整改。

【证据材料】
1. 现场检查笔录1份
2. 调查询问笔录1份
3. 现场照片5张
4. 监测报告1份（如涉及）

【法律依据】
{law}
{random.choice(['《中华人民共和国环境保护法》', '《中华人民共和国行政处罚法》', ''])}

【处罚决定】
罚款金额：人民币{penalty_amount}万元整（¥{penalty_amount * 10000}元）
裁量等级：{discretion_level}
裁量理由：{random.choice(['企业积极配合调查', '初次违法', '已及时整改', '造成一定环境影响', '违法情节较重'])}

【程序性文件】
立案审批：√ 已审批
法制审核：√ 已审核
集体讨论：√ 已讨论
告知权利：√ 已告知
听证权利：√ 已告知（如适用）
决定审批：√ 已审批
送达回证：√ 已送达

【文书签署】
作出日期：{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日
执法人员签名：
负责人签名：
机关印章：
"""
        return case_content

    def generate_structured_data(self, violation_type_data, company_name, province, city, year, month):
        """生成结构化案例数据"""
        self.case_id += 1
        violation_pattern = random.choice(violation_type_data["patterns"])
        law = random.choice(violation_type_data["laws"])
        penalty_amount = random.randint(2, 100) * 10000

        return {
            "case_id": f"case_{self.case_id:05d}",
            "case_number": self.generate_case_number(province[:2], year, month),
            "case_name": f"{company_name}{violation_pattern}案",
            "case_type": "行政处罚",
            "respondent": company_name,
            "organizing_unit": f"{city}生态环境局",
            "province": province,
            "city": city,
            "industry": random.choice(self.INDUSTRIES),
            "violation_date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "decision_date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "violation_type": list(self.VIOLATION_TYPES.keys())[list(self.VIOLATION_TYPES.values()).index(violation_type_data)],
            "violation": violation_pattern,
            "penalty_basis": law,
            "penalty_decision": f"罚款人民币{penalty_amount}万元",
            "penalty_amount": penalty_amount,
            "discretion_level": random.choice(["从轻", "一般", "从重"]),
            "legal_basis": violation_type_data["laws"],
            "documents": {
                "现场检查笔录": {"date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "status": "有"},
                "调查询问笔录": {"date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "status": "有"},
                "监测报告": {"status": random.choice(["有", "无"])},
                "行政处罚决定书": {"date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "status": "有"}
            },
            "procedural_check": {
                "立案审批": True,
                "法制审核": True,
                "集体讨论": True,
                "告知权利": True,
                "决定审批": True
            },
            "procedural_issues": random.choice([True, False]),
            "evidence_complete": random.choice([True, False]),
            "has_legality_issues": random.choice([True, False])
        }

    def generate_batch(self, count=None):
        """批量生成案例"""
        if count is None:
            count = self.count

        cases = []
        violation_types = list(self.VIOLATION_TYPES.keys())

        for i in range(count):
            province = random.choice(self.PROVINCES)
            city = random.choice(self.CITIES.get(province, [province]))
            company_name = self.generate_company_name()
            year = random.randint(2020, 2025)
            month = random.randint(1, 12)
            violation_type = random.choice(violation_types)
            violation_type_data = self.VIOLATION_TYPES[violation_type]

            case = self.generate_structured_data(violation_type_data, company_name, province, city, year, month)
            cases.append(case)

            if (i + 1) % 100 == 0:
                print(f"已生成 {i + 1} / {count} 份案例...")

        return cases


def main():
    """主函数"""
    print("=" * 60)
    print("HERMES 1000份生态环境案例生成器")
    print("=" * 60)

    generator = CaseGenerator(count=1000)

    print("\n正在生成1000份生态环境行政处罚案例...")
    cases = generator.generate_batch(1000)

    output_dir = "test_data/stress_test"
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, "eco_cases_1000.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"\n案例数据已保存到: {json_path}")

    txt_path = os.path.join(output_dir, "eco_cases_content.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        for i, case in enumerate(cases):
            content = f"""
案例 {i + 1}
{'=' * 60}
案卷编号：{case['case_number']}
案卷名称：{case['case_name']}
被处罚单位：{case['respondent']}
执法机关：{case['organizing_unit']}
违法事实：{case['violation']}
处罚决定：{case['penalty_decision']}
罚款金额：{case['penalty_amount']}元
法律依据：{case['penalty_basis']}
裁量等级：{case['discretion_level']}

程序检查：立案审批={case['procedural_check']['立案审批']}, 法制审核={case['procedural_check']['法制审核']}, 集体讨论={case['procedural_check']['集体讨论']}
告知权利={case['procedural_check']['告知权利']}, 决定审批={case['procedural_check']['决定审批']}

证据材料：现场检查笔录={case['documents']['现场检查笔录']['status']}, 调查询问笔录={case['documents']['调查询问笔录']['status']}, 监测报告={case['documents']['监测报告']['status']}

{'=' * 60}
"""
            f.write(content)

    print(f"案例内容已保存到: {txt_path}")

    stats = {
        "总数": len(cases),
        "按省份统计": {},
        "按违法类型统计": {},
        "按裁量等级统计": {"从轻": 0, "一般": 0, "从重": 0}
    }

    for case in cases:
        province = case['province']
        violation_type = case['violation_type']
        discretion = case['discretion_level']

        stats["按省份统计"][province] = stats["按省份统计"].get(province, 0) + 1
        stats["按违法类型统计"][violation_type] = stats["按违法类型统计"].get(violation_type, 0) + 1
        stats["按裁量等级统计"][discretion] += 1

    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总案例数：{stats['总数']}")
    print(f"\n按违法类型统计：")
    for vt, count in sorted(stats["按违法类型统计"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {vt}: {count}份")
    print(f"\n按裁量等级统计：")
    for dl, count in stats["按裁量等级统计"].items():
        print(f"  {dl}: {count}份")

    print("\n1000份测试案例生成完成！")
    return 0


if __name__ == "__main__":
    exit(main())
