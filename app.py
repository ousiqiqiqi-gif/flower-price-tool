import streamlit as st
import pandas as pd
from datetime import datetime


# =====================
# 页面设置
# =====================

st.set_page_config(
    page_title="花店报价工具",
    layout="centered"
)


# =====================
# 读取数据库
# =====================

file_name = "flower_database.xlsx"

df = pd.read_excel(file_name)


# =====================
# 数据检查
# =====================

need_columns = [
    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"
]


for c in need_columns:

    if c not in df.columns:

        st.error(
            f"Excel缺少字段：{c}"
        )

        st.stop()



# =====================
# 数据整理
# =====================

flowers = {}


for _, row in df.iterrows():

    name = row["名称"]


    if (
        "单枝成本" in df.columns
        and pd.notna(row["单枝成本"])
    ):

        cost = float(row["单枝成本"])

    else:

        cost = (
            float(row["单价"])
            /
            int(row["每扎数量"])
        )


    flowers[name] = {

        "类别": row["类别"],

        "花材类型": row["花材类型"],

        "单枝成本": cost,

        "每扎数量": int(row["每扎数量"])

    }



# =====================
# 初始化
# =====================

if "selected_flowers" not in st.session_state:

    st.session_state.selected_flowers = []


if "history" not in st.session_state:

    st.session_state.history = []



# =====================
# 标题
# =====================

st.title("🌸 花店报价工具")
# =====================
# 采购设置（折叠）
# =====================

with st.expander("⚙️ 采购设置"):

    freight = st.number_input(
        "本次采购运费（元）",
        min_value=0,
        value=80
    )


    total_batch = st.number_input(
        "本次采购总扎数",
        min_value=1,
        value=50
    )


batch_freight = freight / total_batch



# =====================
# 分类整理
# =====================

flower_types = {}

leaf_types = {}


for name,data in flowers.items():


    if data["类别"] == "花材":

        cat = data["花材类型"]

        if cat not in flower_types:

            flower_types[cat] = []

        flower_types[cat].append(name)



    elif data["类别"] == "叶材":

        cat = data["花材类型"]

        if cat not in leaf_types:

            leaf_types[cat] = []

        leaf_types[cat].append(name)



# =====================
# 选择花材
# =====================

st.subheader("🌸 选择花材")


for cat,items in flower_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择花材",

            items,

            key="flower_"+cat

        )


        for item in result:

            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)



# =====================
# 选择叶材
# =====================

st.subheader("🌿 选择叶材")


for cat,items in leaf_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择叶材",

            items,

            key="leaf_"+cat

        )


        for item in result:

            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)



# =====================
# 已选花材
# =====================

if st.session_state.selected_flowers:


    st.divider()

    st.subheader("📋 已选花材")


    total_cost = 0



    for item in st.session_state.selected_flowers:


        col1,col2,col3 = st.columns(
            [3,1,1]
        )


        with col1:

            st.write(item)



        num_key = "quantity_"+item


        if num_key not in st.session_state:

            st.session_state[num_key]=1



        with col2:


            qty = st.number_input(

                "数量",

                min_value=1,

                step=1,

                key=num_key,

                label_visibility="collapsed"

            )



        with col3:


            if st.button(
                "删除",
                key="delete_"+item
            ):

                st.session_state.selected_flowers.remove(item)

                st.rerun()



        # 运费分摊

        freight_branch = (

            batch_freight

            /

            flowers[item]["每扎数量"]

        )


        single_cost = (

            flowers[item]["单枝成本"]

            +

            freight_branch

        )


        total_cost += qty * single_cost



# =====================
# 计算报价
# =====================

if st.button("💰 计算报价"):


    if not st.session_state.selected_flowers:


        st.warning(
            "请先选择花材"
        )


    else:


        labor = 100


        cost_x3 = total_cost * 3


        base_price = cost_x3 + labor



        price_list = [

            56,
            68,
            88,
            98,
            128,
            158,
            198,
            228,
            268,
            298,
            358,
            398,
            498,
            598,
            698,
            898,
            998,
            1298

        ]



        recommend = 1298


        for p in price_list:

            if base_price <= p:

                recommend = p

                break



        profit = recommend - total_cost - labor



        st.session_state.current_quote = {


            "时间":

            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),


            "花材":

            "、".join(
                st.session_state.selected_flowers
            ),


            "成本":

            round(total_cost,2),


            "售价":

            recommend

        }



        st.divider()


        st.subheader("🌸 报价结果")



        st.write(
            f"花材成本：¥{round(total_cost,2)}"
        )


        st.write(
            "制作费用：¥100"
        )


        st.write(
            f"基础售价：¥{round(base_price,2)}"
        )


        st.success(
            f"建议售价：¥{recommend}"
        )


        st.info(
            f"预计利润：¥{round(profit,2)}"
        )



# =====================
# 保存报价
# =====================

if "current_quote" in st.session_state:


    st.divider()


    if st.button(
        "💾 保存报价"
    ):


        st.session_state.history.append(

            st.session_state.current_quote

        )


        st.success(
            "✅报价已保存"
        )



# =====================
# 新建报价
# =====================

if st.button(
    "🔄 新建报价"
):


    st.session_state.selected_flowers=[]


    for key in list(st.session_state.keys()):

        if key.startswith("quantity_"):

            del st.session_state[key]


    if "current_quote" in st.session_state:

        del st.session_state["current_quote"]


    st.rerun()



# =====================
# 历史记录
# =====================

if st.session_state.history:


    st.divider()

    st.subheader("📋 历史报价")


    st.dataframe(

        pd.DataFrame(
            st.session_state.history
        ),

        use_container_width=True

    )
