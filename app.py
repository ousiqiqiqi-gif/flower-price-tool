import streamlit as st
import pandas as pd


# =================
# 页面设置
# =================

st.set_page_config(
    page_title="花店报价工具",
    page_icon="🌸",
    layout="centered"
)


# =================
# 读取数据库
# =================

file_name = "flower_database.xlsx"

df = pd.read_excel(file_name)


required_columns = [
    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"
]


for col in required_columns:

    if col not in df.columns:

        st.error(f"Excel缺少字段：{col}")

        st.stop()



# =================
# 数据整理
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

st.caption(
    "内部员工使用｜快速计算花材成本与建议售价"
)



# =================
# 采购信息
# =================

with st.expander("📦 采购信息"):

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



# =================
# 搜索花材
# =================

st.divider()

st.subheader("🌹 选择花材")


search = st.text_input(
    "搜索花材名称"
)


all_names = list(flowers.keys())


if search:

    search_result = [

        x for x in all_names

        if search in x

    ]

else:

    search_result = all_names



selected_all = st.multiselect(

    "选择花材",

    search_result

)



# =================
# 数量
# =================


cost_total = 0



if selected_all:


    st.subheader("填写使用数量")


    for item in selected_all:


        quantity = st.number_input(

            f"{item}（枝）",

            min_value=1,

            value=1,

            step=1,

            key=item

        )


        freight_per_branch = (

            batch_freight

            /

            flowers[item]["count"]

        )


        real_single_cost = (

            flowers[item]["single_price"]

            +

            freight_per_branch

        )


        cost_total += (

            quantity

            *

            real_single_cost

        )



# =================
# 计算
# =================


if st.button(
    "🌸 生成报价",
    use_container_width=True
):


    if not selected_all:

        st.warning(
            "请选择花材"
        )


    else:


        labor = 100


        cost_x3 = cost_total * 3


        final_price = cost_x3 + labor



        st.divider()


        st.subheader(
            "报价明细"
        )


        detail = ""


        for item in selected_all:


            quantity = st.session_state[item]


            freight_per_branch = (

                batch_freight

                /

                flowers[item]["count"]

            )


            real_single_cost = (

                flowers[item]["single_price"]

                +

                freight_per_branch

            )


            detail += (

                f"""
🌸 {item}

数量：{quantity}枝

单枝成本：
¥{round(real_single_cost,2)}

小计：
¥{round(quantity*real_single_cost,2)}

---

"""
            )


        st.text(detail)



        st.divider()



        st.metric(
            "真实成本",
            f"¥{round(cost_total,2)}"
        )


        st.metric(
            "基础售价",
            f"¥{round(final_price,2)}"
        )



        price_level = [

            56,68,88,98,
            128,158,198,
            228,268,298,
            358,398,498,
            598,698,898,
            998,1098,
            1198,1298

        ]


        recommended_price = 1298


        for price in price_level:


            if final_price <= price:

                recommended_price = price

                break



        st.success(

            f"🌸 建议零售价：¥{recommended_price}"

        )
