"""
古代木廊桥火灾风险智能评估系统 V1.0
工具函数模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from config import (
    HAZARD_WEIGHTS, 
    ENVIRONMENT_WEIGHTS, 
    RISK_LEVELS,
    RISK_COLORS
)


def load_bridges() -> pd.DataFrame:
    """加载桥梁数据"""
    try:
        df = pd.read_csv("data/bridges.csv")
        return df
    except FileNotFoundError:
        # 返回示例数据
        return get_sample_bridges()


def get_sample_bridges() -> pd.DataFrame:
    """获取示例桥梁数据"""
    data = {
        "桥梁名称": ["如龙桥", "临江桥", "兰溪桥", "淤上桥", "大济桥", 
                    "张村桥", "南阳桥", "北涧桥", "三条桥", "永宁桥"],
        "所在省": ["浙江省"] * 10,
        "所在市": ["丽水市", "丽水市", "丽水市", "丽水市", "丽水市", 
                  "丽水市", "温州市", "温州市", "温州市", "温州市"],
        "所在县": ["庆元县", "庆元县", "庆元县", "庆元县", "庆元县", 
                  "庆元县", "泰顺县", "泰顺县", "泰顺县", "泰顺县"],
        "具体地点": ["淤上乡坑下村", "松源镇坑西村", "贤良镇", "淤上乡", 
                   "濛洲街道大济村", "张村乡", "泗溪镇", "泗溪镇", "洲岭乡", "三魁镇"],
        "纬度": [27.4542, 27.4612, 27.4456, 27.4489, 27.4678, 
                27.4234, 27.5612, 27.5567, 27.5123, 27.6234],
        "经度": [119.0825, 119.0756, 119.0634, 119.0789, 119.0812, 
                119.0545, 120.0534, 120.0489, 119.9823, 120.1234],
        "桥梁类型": ["木拱桥", "木拱桥", "木拱桥", "木拱桥", "木拱桥", 
                   "木平桥", "木拱桥", "木拱桥", "木拱桥", "木拱桥"],
        "建造年代": ["明代", "清代", "明代", "清代", "明代", 
                   "清代", "清代", "清代", "宋代", "清代"],
        "保护级别": ["全国重点", "省级", "全国重点", "县级", "省级", 
                   "县级", "全国重点", "全国重点", "省级", "县级"],
        "是否开放使用": ["是", "是", "是", "是", "是", "是", "是", "是", "是", "是"],
        "备注": ["全国重点文物保护单位", "保存完好", "著名廊桥", "乡村廊桥", 
                "历史悠久", "简洁型廊桥", "泰顺廊桥代表", "双桥结构", "历史最悠久", "保存较好"]
    }
    return pd.DataFrame(data)


def calculate_hazard_score(factors: Dict[str, float]) -> Tuple[float, str]:
    """
    计算致灾因子危险性指数
    factors: 各因子评分 (0-100)
    返回: (总分, 等级)
    """
    score = 0
    for factor, value in factors.items():
        weight = HAZARD_WEIGHTS.get(factor, 0.1)
        score += value * weight
    
    level = get_risk_level(score)
    return round(score, 2), level


def calculate_sensitivity_score(factors: Dict[str, float]) -> Tuple[float, str]:
    """
    计算孕灾环境敏感性指数
    factors: 各环境因子评分 (0-100)
    返回: (总分, 等级)
    """
    score = 0
    for factor, value in factors.items():
        weight = ENVIRONMENT_WEIGHTS.get(factor, 0.25)
        score += value * weight
    
    level = get_risk_level(score)
    return round(score, 2), level


def calculate_comprehensive_risk(hazard_score: float, sensitivity_score: float) -> Tuple[float, str, str]:
    """
    计算综合火灾风险
    返回: (总分, 等级, 建议)
    """
    # 综合风险 = 危险性 * 0.5 + 敏感性 * 0.5
    risk_score = hazard_score * 0.5 + sensitivity_score * 0.5
    level = get_risk_level(risk_score)
    
    # 生成建议
    suggestions = get_risk_suggestions(hazard_score, sensitivity_score, level)
    
    return round(risk_score, 2), level, suggestions


def get_risk_level(score: float) -> str:
    """根据分数获取风险等级"""
    if score < 25:
        return "低"
    elif score < 50:
        return "中"
    elif score < 75:
        return "较高"
    else:
        return "高"


def get_risk_suggestions(hazard_score: float, sensitivity_score: float, level: str) -> str:
    """获取风险管控建议"""
    suggestions = []
    
    if hazard_score > 50:
        suggestions.append("加强火灾源头管控，重点关注用火安全和电气设施")
    if sensitivity_score > 50:
        suggestions.append("改善周边环境，增加消防设施配置")
    
    if level == "高":
        suggestions.append("建议安装火灾预警系统，加强日常巡查频率")
        suggestions.append("制定专项应急预案，配备充足灭火器材")
    elif level == "较高":
        suggestions.append("建议定期检查消防设施，加强防火宣传")
    else:
        suggestions.append("保持现有防火措施，定期维护检查")
    
    return "\n".join(suggestions) if suggestions else "继续做好日常防火工作"


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """数值标准化到0-100"""
    if max_val == min_val:
        return 50
    normalized = (value - min_val) / (max_val - min_val) * 100
    return max(0, min(100, normalized))


def get_risk_color(level: str) -> str:
    """获取风险等级对应的颜色"""
    return RISK_COLORS.get(level, "#6c757d")


def generate_sample_assessment(bridge_name: str) -> Dict:
    """为示例桥梁生成评估数据"""
    np.random.seed(hash(bridge_name) % 10000)
    
    # 致灾因子数据
    hazard_factors = {
        "祭祀用火": np.random.randint(20, 80),
        "爆竹燃放": np.random.randint(20, 70),
        "电气设施": np.random.randint(30, 90),
        "易燃物堆积": np.random.randint(20, 75),
        "旅游开发": np.random.randint(30, 80),
        "居民生活干扰": np.random.randint(20, 60),
        "雷击高发区": np.random.randint(10, 50),
        "交通节点影响": np.random.randint(20, 70)
    }
    
    hazard_score, hazard_level = calculate_hazard_score(hazard_factors)
    
    # 孕灾环境数据
    environment_factors = {
        "气温": np.random.randint(20, 40),
        "绝对湿度": np.random.randint(30, 80),
        "风速": np.random.randint(10, 80),
        "降水": np.random.randint(20, 90)
    }
    
    # 标准化环境数据
    env_normalized = {
        "气温": (environment_factors["气温"] - 20) / 20 * 100,
        "绝对湿度": (100 - environment_factors["绝对湿度"]),
        "风速": environment_factors["风速"],
        "降水": (100 - environment_factors["降水"])
    }
    
    sensitivity_score, sensitivity_level = calculate_sensitivity_score(env_normalized)
    
    # 综合风险
    risk_score, risk_level, suggestions = calculate_comprehensive_risk(
        hazard_score, sensitivity_score
    )
    
    return {
        "bridge_name": bridge_name,
        "hazard_factors": hazard_factors,
        "hazard_score": hazard_score,
        "hazard_level": hazard_level,
        "environment_factors": environment_factors,
        "sensitivity_score": sensitivity_score,
        "sensitivity_level": sensitivity_level,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "suggestions": suggestions
    }


def get_all_bridges_with_assessment() -> List[Dict]:
    """获取所有桥梁及其评估结果"""
    bridges = get_sample_bridges()
    results = []
    
    for _, row in bridges.iterrows():
        assessment = generate_sample_assessment(row["桥梁名称"])
        assessment["bridge_info"] = {
            "name": row["桥梁名称"],
            "province": row["所在省"],
            "city": row["所在市"],
            "county": row["所在县"],
            "location": row["具体地点"],
            "lat": row["纬度"],
            "lon": row["经度"],
            "type": row["桥梁类型"],
            "year": row["建造年代"],
            "level": row["保护级别"]
        }
        results.append(assessment)
    
    return results