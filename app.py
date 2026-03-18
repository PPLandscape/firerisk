"""
古代木廊桥火灾风险智能评估系统 V1.0
主应用程序
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from utils import get_bridges, calc_hazard, calc_sensitivity, calc_risk, gen_sample, RISK_COLORS
import json

st.set_page_config(page_title="古代木廊桥火灾风险评估系统", page_icon="🌉", layout="wide")

# 导航
pages = {
    "首页": "home",
    "桥梁档案": "bridges", 
    "危险性评估": "hazard",
    "敏感性评估": "sensitivity",
    "综合评估": "risk",
    "地图分析": "map",
    "结果分析": "analysis",
    "报告导出": "report",
    "系统说明": "help"
}

st.sidebar.title("🌉 导航菜单")
selection = st.sidebar.radio("请选择功能模块", list(pages.keys()))

# 加载数据
df = get_bridges()

# 首页
if selection == "首页":
    st.title("🏛️ 古代木廊桥火灾风险智能评估系统")
    st.markdown("### V1.0")
    st.markdown("---")
    st.markdown("""
    本系统面向古代木廊桥火灾风险研究与保护管理，集成以下核心功能：
    
    - 📁 **桥梁档案管理** - 收录桥梁基本信息和地理坐标
    - 🔥 **致灾因子危险性评估** - 评估火灾源头风险
    - 🌤️ **孕灾环境敏感性评估** - 评估环境因素风险  
    - 📊 **综合火灾风险评估** - 综合计算整体风险等级
    - 🗺️ **风险地图可视化** - 天地图展示风险点位
    - 📈 **结果分析** - 图表展示评估结果
    - 📄 **报告导出** - 生成评估报告
    """)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📁 桥梁档案\n\n管理桥梁基础信息")
    with col2:
        st.warning("🔥 危险性评估\n\n评估致灾因子风险")
    with col3:
        st.error("🌤️ 敏感性评估\n\n评估环境敏感风险")
    
    st.markdown("### 最近评估项目")
    if df is not None:
        st.dataframe(df[["桥梁名称", "所在省", "所在市", "保护级别"]].head(5), use_container_width=True)

# 桥梁档案
elif selection == "桥梁档案":
    st.title("📁 桥梁档案管理")
    
    tab1, tab2 = st.tabs(["桥梁列表", "新建桥梁"])
    
    with tab1:
        st.subheader("桥梁档案列表")
        if df is not None:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无桥梁数据")
    
    with tab2:
        st.subheader("新建桥梁档案")
        with st.form("new_bridge"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("桥梁名称")
                province = st.selectbox("所在省", ["浙江省", "福建省", "江西省", "广东省"])
                city = st.selectbox("所在市", ["丽水市", "温州市", "福州市", "南平市", "赣州市", "梅州市"])
                county = st.text_input("所在县")
                location = st.text_input("具体地点")
            with col2:
                lat = st.number_input("纬度", min_value=24.0, max_value=30.0, value=27.5)
                lon = st.number_input("经度", min_value=115.0, max_value=122.0, value=119.0)
                btype = st.selectbox("桥梁类型", ["木拱桥", "木平桥", "石拱桥", "其它"])
                year = st.selectbox("建造年代", ["宋代", "元代", "明代", "清代", "民国"])
                level = st.selectbox("保护级别", ["全国重点", "省级", "市级", "县级"])
            
            open_use = st.radio("是否开放使用", ["是", "否"])
            remark = st.text_area("备注")
            
            if st.form_submit_button("保存桥梁信息"):
                st.success(f"桥梁「{name}」信息已保存！")

# 危险性评估
elif selection == "危险性评估":
    st.title("🔥 致灾因子危险性评估")
    
    bridge_name = st.selectbox("选择桥梁", df["桥梁名称"].tolist() if df is not None else ["如龙桥"])
    
    st.subheader("致灾因子评分 (0-100)")
    
    col1, col2 = st.columns(2)
    with col1:
        f1 = st.slider("祭祀用火", 0, 100, 50)
        f2 = st.slider("爆竹燃放", 0, 100, 40)
        f3 = st.slider("电气设施", 0, 100, 60)
        f4 = st.slider("易燃物堆积", 0, 100, 45)
    with col2:
        f5 = st.slider("旅游开发", 0, 100, 50)
        f6 = st.slider("居民生活干扰", 0, 100, 35)
        f7 = st.slider("雷击高发区", 0, 100, 25)
        f8 = st.slider("交通节点影响", 0, 100, 40)
    
    factors = {
        "祭祀用火": f1, "爆竹燃放": f2, "电气设施": f3, "易燃物堆积": f4,
        "旅游开发": f5, "居民生活干扰": f6, "雷击高发区": f7, "交通节点影响": f8
    }
    
    if st.button("计算危险性指数"):
        score, level = calc_hazard(factors)
        
        st.markdown("---")
        st.subheader("评估结果")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("危险性总分", f"{score}")
        col2.metric("危险性等级", level)
        
        colors = {"低": "green", "中": "yellow", "较高": "orange", "高": "red"}
        col3.markdown(f"**等级颜色**: :{colors[level]}[{level}]")
        
        # 图表
        fig = px.bar(x=list(factors.keys()), y=list(factors.values()), 
                    title="致灾因子贡献图",
                    labels={"x": "因子", "y": "评分"},
                    color=list(factors.values()),
                    color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"结果解读：该桥梁致灾因子危险性评估得分为 {score}，等级为「{level}」。")

# 敏感性评估
elif selection == "敏感性评估":
    st.title("🌤️ 孕灾环境敏感性评估")
    
    bridge_name = st.selectbox("选择桥梁", df["桥梁名称"].tolist() if df is not None else ["如龙桥"], key="sens_bridge")
    
    st.subheader("环境因子评分 (0-100)")
    
    col1, col2 = st.columns(2)
    with col1:
        e1 = st.slider("气温", 0, 100, 45, key="e1")
        e2 = st.slider("绝对湿度", 0, 100, 50, key="e2")
    with col2:
        e3 = st.slider("风速", 0, 100, 40, key="e3")
        e4 = st.slider("降水", 0, 100, 55, key="e4")
    
    factors = {"气温": e1, "绝对湿度": e2, "风速": e3, "降水": e4}
    
    if st.button("计算敏感性指数", key="calc_sens"):
        score, level = calc_sensitivity(factors)
        
        st.markdown("---")
        st.subheader("评估结果")
        
        col1, col2 = st.columns(3)
        col1.metric("敏感性总分", f"{score}")
        col2.metric("敏感性等级", level)
        
        colors = {"低": "green", "中": "yellow", "较高": "orange", "高": "red"}
        col2.markdown(f"**等级颜色**: :{colors[level]}[{level}]")
        
        # 雷达图
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(factors.values()),
            theta=list(factors.keys()),
            fill='toself',
            name='环境因子'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                         showlegend=False, title="环境因子雷达图")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"结果解读：该桥梁孕灾环境敏感性评估得分为 {score}，等级为「{level}」。")

# 综合评估
elif selection == "综合评估":
    st.title("📊 综合火灾风险评估")
    
    bridge_name = st.selectbox("选择桥梁", df["桥梁名称"].tolist() if df is not None else ["如龙桥"], key="risk_bridge")
    
    # 获取该桥梁的示例数据
    if df is not None:
        row = df[df["桥梁名称"] == bridge_name].iloc[0]
        sample = gen_sample(bridge_name, row["纬度"], row["经度"])
    else:
        sample = gen_sample("如龙桥", 27.4542, 119.0825)
    
    st.subheader("评估结果")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("致灾因子危险性", f"{sample['hazard_score']}", sample['hazard_level'])
    col2.metric("孕灾环境敏感性", f"{sample['sensitivity_score']}", sample['sensitivity_level'])
    col3.metric("综合火灾风险", f"{sample['risk_score']}", sample['risk_level'])
    
    colors = {"低": "green", "中": "yellow", "较高": "orange", "高": "red"}
    st.markdown(f"综合风险等级: :{colors[sample['risk_level']]}[{sample['risk_level']}]")
    
    st.subheader("风险归因分析")
    st.write(sample.get("suggestions", "暂无建议"))
    
    st.subheader("管控建议")
    st.info("1. 建议安装火灾预警系统\n2. 加强日常巡查频率\n3. 配备充足灭火器材")

# 地图分析
elif selection == "地图分析":
    st.title("🗺️ 风险地图可视化")
    
    # 模式选择
    mode = st.radio("选择显示模式", ["孕灾环境敏感性", "致灾因子危险性", "综合火灾风险"], horizontal=True)
    
    # 生成所有桥梁的评估数据
    bridges_data = []
    if df is not None:
        for _, row in df.iterrows():
            sample = gen_sample(row["桥梁名称"], row["纬度"], row["经度"])
            sample["info"] = {
                "name": row["桥梁名称"],
                "location": f"{row['所在省']}{row['所在市']}{row['所在县']}",
                "lat": row["纬度"],
                "lon": row["经度"]
            }
            bridges_data.append(sample)
    
    # 根据模式获取颜色
    def get_color(sample, mode):
        if mode == "孕灾环境敏感性":
            level = sample["sensitivity_level"]
        elif mode == "致灾因子危险性":
            level = sample["hazard_level"]
        else:
            level = sample["risk_level"]
        return RISK_COLORS.get(level, "#6c757d")
    
    # 生成地图HTML
    center_lat = df["纬度"].mean() if df is not None else 27.5
    center_lon = df["经度"].mean() if df is not None else 119.0
    
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ height: 600px; width: 100%; }}
            .legend {{ background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2); }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{center_lat}, {center_lon}], 8);
            L.tileLayer('https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={{x}}&y={{y}}&z={{z}}', {{
                subdomains: '1234',
                attribution: '© 天地图'
            }}).addTo(map);
            
            var bridges = {json.dumps(bridges_data)};
            var colors = {json.dumps(RISK_COLORS)};
            
            bridges.forEach(function(b) {{
                var color = colors[b.risk_level] || '#6c757d';
                var marker = L.circleMarker([b.lat, b.lon], {{
                    radius: 10,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }}).addTo(map);
                
                var info = b.info;
                marker.bindPopup(
                    '<b>' + info.name + '</b><br>' +
                    '所在地: ' + info.location + '<br>' +
                    '敏感性等级: ' + b.sensitivity_level + '<br>' +
                    '危险性等级: ' + b.hazard_level + '<br>' +
                    '综合风险: ' + b.risk_level + ' (' + b.risk_score + ')'
                );
            }});
            
            // 图例
            var legend = L.control({{position: 'bottomright'}});
            legend.onAdd = function(map) {{
                var div = L.DomUtil.create('div', 'legend');
                div.innerHTML = '<b>风险等级</b><br>' +
                    '<i style="background:#28a745;width:12px;height:12px;display:inline-block;"></i> 低<br>' +
                    '<i style="background:#ffc107;width:12px;height:12px;display:inline-block;"></i> 中<br>' +
                    '<i style="background:#fd7e14;width:12px;height:12px;display:inline-block;"></i> 较高<br>' +
                    '<i style="background:#dc3545;width:12px;height:12px;display:inline-block;"></i> 高';
                return div;
            }};
            legend.addTo(map);
        </script>
    </body>
    </html>
    """
    
    components.html(map_html, height=650)
    
    st.markdown("### 图例说明")
    st.markdown("""
    - 🟢 绿色: 低风险
    - 🟡 黄色: 中风险  
    - 🟠 橙色: 较高风险
    - 🔴 红色: 高风险
    """)
    
    st.info(f"当前模式: {mode}。点击地图上的点位可查看详细信息。")

# 结果分析
elif selection == "结果分析":
    st.title("📈 结果分析")
    
    bridges_data = []
    if df is not None:
        for _, row in df.iterrows():
            sample = gen_sample(row["桥梁名称"], row["纬度"], row["经度"])
            bridges_data.append(sample)
    
    # 综合风险排序
    st.subheader("综合风险排序")
    risk_df = pd.DataFrame([{
        "桥梁名称": b["bridge_name"],
        "综合风险": b["risk_score"],
        "风险等级": b["risk_level"],
        "危险性": b["hazard_score"],
        "敏感性": b["sensitivity_score"]
    } for b in bridges_data])
    risk_df = risk_df.sort_values("综合风险", ascending=False)
    st.dataframe(risk_df, use_container_width=True)
    
    # 风险等级统计
    st.subheader("风险等级统计")
    level_counts = risk_df["风险等级"].value_counts()
    fig = px.pie(values=level_counts.values, names=level_counts.index, 
                title="风险等级分布", color=level_counts.index,
                color_discrete_map=RISK_COLORS)
    st.plotly_chart(fig, use_container_width=True)
    
    # 柱状图
    st.subheader("各桥梁风险对比")
    fig2 = px.bar(risk_df, x="桥梁名称", y="综合风险", color="风险等级",
                 color_discrete_map=RISK_COLORS, title="桥梁综合风险对比")
    st.plotly_chart(fig2, use_container_width=True)

# 报告导出
elif selection == "报告导出":
    st.title("📄 评估报告导出")
    
    bridge_name = st.selectbox("选择桥梁", df["桥梁名称"].tolist() if df is not None else ["如龙桥"], key="report_bridge")
    
    if df is not None:
        row = df[df["桥梁名称"] == bridge_name].iloc[0]
        sample = gen_sample(bridge_name, row["纬度"], row["经度"])
    else:
        sample = gen_sample("如龙桥", 27.4542, 119.0825)
    
    st.subheader(f"「{bridge_name}」火灾风险评估报告")
    
    st.markdown("---")
    st.markdown("### 一、桥梁基本信息")
    
    col1, col2 = st.columns(2)
    col1.markdown(f"**桥梁名称**: {bridge_name}")
    col1.markdown(f"**所在省**: {row['所在省']}")
    col1.markdown(f"**所在市**: {row['所在市']}")
    col1.markdown(f"**所在县**: {row['所在县']}")
    col2.markdown(f"**桥梁类型**: {row['桥梁类型']}")
    col2.markdown(f"**建造年代**: {row['建造年代']}")
    col2.markdown(f"**保护级别**: {row['保护级别']}")
    col2.markdown(f"**地理坐标**: ({row['纬度']}, {row['经度']})")
    
    st.markdown("---")
    st.markdown("### 二、致灾因子危险性评估")
    st.metric("危险性总分", f"{sample['hazard_score']}", sample['hazard_level'])
    st.write("各因子评分:")
    st.json(sample["hazard_factors"])
    
    st.markdown("---")
    st.markdown("### 三、孕灾环境敏感性评估")
    st.metric("敏感性总分", f"{sample['sensitivity_score']}", sample['sensitivity_level'])
    st.write("环境因子评分:")
    st.json(sample["sensitivity_factors"])
    
    st.markdown("---")
    st.markdown("### 四、综合火灾风险评估")
    st.metric("综合风险值", f"{sample['risk_score']}", sample['risk_level'])
    
    st.markdown("### 五、管控建议")
    st.info(sample.get("suggestions", "暂无建议"))
    
    # 导出按钮
    report_text = f"""# {bridge_name} 火灾风险评估报告

## 一、桥梁基本信息
- 桥梁名称: {bridge_name}
- 所在省: {row['所在省']}
- 所在市: {row['所在市']}
- 所在县: {row['所在县']}
- 桥梁类型: {row['桥梁类型']}
- 建造年代: {row['建造年代']}
- 保护级别: {row['保护级别']}
- 地理坐标: ({row['纬度']}, {row['经度']})

## 二、致灾因子危险性评估
- 危险性总分: {sample['hazard_score']}
- 危险性等级: {sample['hazard_level']}

## 三、孕灾环境敏感性评估
- 敏感性总分: {sample['sensitivity_score']}
- 敏感性等级: {sample['sensitivity_level']}

## 四、综合火灾风险评估
- 综合风险值: {sample['risk_score']}
- 综合风险等级: {sample['risk_level']}

## 五、管控建议
{sample.get('suggestions', '暂无')}
"""
    
    st.download_button("下载报告(Markdown)", report_text, f"{bridge_name}_评估报告.md", "text/markdown")

# 系统说明
elif selection == "系统说明":
    st.title("❓ 系统说明")
    
    st.markdown("""
    ## 一、系统用途
    
    本系统用于古代木廊桥火灾风险评估与管理，帮助文物保护部门科学评估火灾风险等级，制定防控措施。
    
    ## 二、模块组成
    
    1. **桥梁档案管理** - 管理桥梁基本信息和地理坐标
    2. **致灾因子评估** - 评估火灾源头风险因素
    3. **敏感性评估** - 评估环境因素敏感性
    4. **综合评估** - 计算综合火灾风险
    5. **地图可视化** - 天地图展示风险点位
    6. **结果分析** - 图表统计分析
    7. **报告导出** - 生成评估报告
    
    ## 三、操作流程
    
    首页 → 桥梁档案 → 危险性评估 → 敏感性评估 → 综合评估 → 地图查看 → 结果分析 → 导出报告
    
    ## 四、评估方法
    
    危险性评估采用加权求和法，敏感性评估采用多因子综合法，综合风险 = 危险性×0.5 + 敏感性×0.5
    
    ## 五、颜色分级
    
    - 绿色(低): 风险值 0-25
    - 黄色(中): 风险值 25-50
    - 橙色(较高): 风险值 50-75
    - 红色(高): 风险值 75-100
    
    ## 六、地图模式说明
    
    - 孕灾环境敏感性: 显示环境因素风险
    - 致灾因子危险性: 显示火灾源头风险
    - 综合火灾风险: 显示整体风险
    """)