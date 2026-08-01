import streamlit as st
import pandas as pd
from datetime import datetime


# =================
# 页面设置
# =================

st.set_page_config(
    page_title="花店报价工具",
    layout="centered"
)


# =================
# 读取花材数据库
# =================

file_name = "flower_database.xlsx"

df = pd.read_excel(file_name)



# =================
# 检查字段
# =================

required_columns = [
    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"
]


for col in required_columns:

    if col not in df.columns:

        st.error(
            f"Excel缺少字段：{col}"
        )

        st.stop()



# =================
# 花材数据整理
# =================

flowers = {}


for _, row in df.iterrows():

    name = row["名称"]


    if "单枝成本" in df.columns and pd.notna(row["单枝成本"]):

        single_cost = float(row["单枝成本"])

    else:

        single_cost = (
            float(row["单价"])
            /
            int(row["每扎数量"])
        )


    flowers[name] = {

        "type": row["类别"],

        "flower_type": row["花材类型"],

        "batch_price": float(row["单价"]),

        "count": int(row["每扎数量"]),

        "single_price": single_cost
    }



# =================
# 标题
# =================

st.title("🌸 花店报价工具")



# =================
# 初始化历史记录
# =================

if "history" not in st.session_state:

    st.session_state.history = []



# =================
# 采购信息
# =================

st.subheader("采购信息")


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


st.info(
    f"平均每扎运费：{round(batch_freight,2)}元"
)



st.divider()



# =================
# 分类
# =================

flower_types = {}

leaf_types = {}


for name,data in flowers.items():


    if data["type"] == "花材":

        category=data["flower_type"]

        if category not in flower_types:

            flower_types[category]=[]

        flower_types[category].append(name)



    elif data["type"]=="叶材":

        category=data["flower_type"]

        if category not in leaf_types:

            leaf_types[category]=[]

        leaf_types[category].append(name)




# =================
# 选择花材
# =================

st.subheader("选择花材")


selected_flowers=[]


for category,items in flower_types.items():

    with st.expander(category):

        result=st.multiselect(
            "选择",
            items,
            key="flower_"+category
        )

        selected_flowers.extend(result)



# =================
# 选择叶材
# =================

st.subheader("选择叶材")


selected_leaf=[]


for category,items in leaf_types.items():

    with st.expander(category):

        result=st.multiselect(
            "选择",
            items,
            key="leaf_"+category
        )

        selected_leaf.extend(result)



selected_all = selected_flowers + selected_leaf



# =================
# 数量
# =================

cost_total=0


if selected_all:


    st.subheader("填写使用数量")


    for item in selected_all:


        quantity=st.number_input(

            f"{item} 使用数量（枝）",

            min_value=1,

            value=1,

            key="num_"+item

        )


        freight_branch = (
            batch_freight
            /
            flowers[item]["count"]
        )


        real_cost = (

            flowers[item]["single_price"]

            +

            freight_branch

        )


        cost_total += quantity * real_cost




# =================
# 计算
# =================

if st.button("计算报价"):


    if not selected_all:

        st.warning(
            "请选择花材"
        )


    else:


        cost_x3 = cost_total*3


        labor=100


        final_price = cost_x3 + labor



        price_level=[

            56,68,88,98,
            128,158,198,
            228,268,298,
            358,398,498,
            598,698,898,
            998,1098,1198,
            1298

        ]


        recommended_price=1298


        for p in price_level:

            if final_price<=p:

                recommended_price=p

                break



        st.session_state.current_quote={

            "时间":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "花材":
            "、".join(selected_all),

            "成本":
            round(cost_total,2),

            "售价":
            recommended_price
        }




        st.divider()

        st.subheader("报价明细")


        for item in selected_all:


            quantity=st.session_state["num_"+item]


            freight_branch = (
                batch_freight
                /
                flowers[item]["count"]
            )


            real_cost=(

                flowers[item]["single_price"]

                +

                freight_branch

            )


            st.write(

                f"{item}：{quantity}枝 × {round(real_cost,2)}元 = {round(quantity*real_cost,2)}元"

            )



        st.divider()


        st.write(
            "真实成本：",
            round(cost_total,2),
            "元"
        )


        st.write(
            "成本×3：",
            round(cost_x3,2),
            "元"
        )


        st.write(
            "人工杂费：100元"
        )


        st.success(

            f"建议零售价：{recommended_price}元"

        )



# =================
# 保存报价
# =================

if "current_quote" in st.session_state:


    st.divider()


    if st.button("💾 保存本次报价"):


        st.session_state.history.append(

            st.session_state.current_quote

        )


        st.success(
            "✅报价已保存"
        )



# =================
# 历史记录
# =================

if st.session_state.history:


    st.divider()


    st.subheader("📋 历史报价")


    history_df=pd.DataFrame(
        st.session_state.history
    )


    st.dataframe(
        history_df,
        use_container_width=True
    )
