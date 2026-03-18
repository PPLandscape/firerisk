"""
古代木廊桥火灾风险智能评估系统 V1.0
评估工具函数
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import random

HAZARD_WEIGHTS = {
    "祭祀用火": 0.15, "爆竹燃放": 0.12, "电气设施": 0.18,
    "易燃物堆积": 0.15, "旅游开发": 0.10, "居民生活干扰": 0.10,
    "雷击高发区": 0.10, "交通节点影响": 0.10
}

ENVIRONMENT_WEIGHTS = {
    "气温": 0.25, "绝对湿度": 0.25, "风速": 0.25, "降水": 0.25
}

RISK_COLORS = {"低": "#28a745", "中": "#ffc107", "较高": "#fd7e14", "高": "#dc3545"}

def get_bridges():
    """获取桥梁数据"""
    try:
        return pd.read_csv("data/bridges.csv")
    except:
        return None

def calc_hazard(factors: Dict[str, float]) -> Tuple[float, str]:
    """计算危险性指数"""
    score = sum(factors.get(k, 0) * v for k, v in HAZARD_WEIGHTS.items())
    level = "低" if score < 25 else "中" if score < 50 else "较高" if score < 75 else "高"
    return round(score, 2), level

def calc_sensitivity(factors: Dict[str, float]) -> Tuple[float, str]:
    """计算敏感性指数"""
    score = sum(factors.get(k, 0) * v for k, v in ENVIRONMENT_WEIGHTS.items())
    level = "低" if score < 25 else "中" if score < 50 else "较高" if score < 75 else "高"
    return round(score, 2), level

def calc_risk(hazard: float, sensitivity: float) -> Tuple[float, str, str]:
    """计算综合风险"""
    risk = hazard * 0.5 + sensitivity * 0.5
    level = "低" if risk < 25 else "中" if risk < 50 else "较商" if risk < 75 else "高"
    suggestions = []
    if hazard > 50: suggestions.append("加强火灾源头管控")
    if sensitivity > 50: suggestions.append("改善周边环境")
    if level == "高": suggestions.extend(["安装火灾预警系统", "加强巡查频率"])
    return round(risk, 2), level, "\n".join(suggestions) if suggestions else "保持日常防火"

def gen_sample(bridge_name: str, lat: float, lon: float) -> Dict:
    """生成示例评估数据"""
    random.seed(hash(bridge_name) % 10000)
    hazard = {k: random.randint(20, 80) for k in HAZARD_WEIGHTS}
    h_score, h_level = calc_hazard(hazard)
    
    env = {k: random.randint(20, 80) for k in ENVIRONMENT_WEIGHTS}
    s_score, s_level = calc_sensitivity(env)
    
    r_score, r_level, sugg = calc_risk(h_score, s_score)
    
    return {
        "bridge_name": bridge_name, "lat": lat, "lon": lon,
        "hazard_factors": hazard, "hazard_score": h_score, "hazard_level": h_level,
        "sensitivity_factors": env, "sensitivity_score": s_score, "sensitivity_level": s_level,
        "risk_score": r_score, "risk_level": r_level, "suggestions": sugg
    }