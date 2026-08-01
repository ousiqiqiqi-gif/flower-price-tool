import streamlit as st
import pandas as pd
import os
from datetime import datetime


# =================
# 页面设置
# =================

st.set_page_config(
    page_title="花店报价工具",
    page_icon="🌸",
    layout="centered"
)


# =================
# 花材数据库
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

        st.error(
            f"Excel缺少字段：{col}"
        )

        st.stop()



# =================
# 报价记录数据库
# =================

history_file = "quote_history.xlsx"


if os.path.exists(history_file):

    history_df = pd.read_excel(
        history_file
    )

else:

    history_df = pd.DataFrame(
        columns=[
            "编号",
            "时间",
            "花材",
            "真实成本",
            "建议售价"
        ]
    )



# =================
# 数据整理
# =================

flowers = {}


for _, row in df.iterrows():

    name = row["名称"]


    if (
        "单枝成本" in df.columns
        and pd.notna(row["单枝成本"])
    ):

        single_cost = float(
            row["单枝成本"]
        )

    else:

        single_cost = (

            float(row["单价"])

            /

            int(row["每扎数量"])

        )


    flowers[name] = {

        "type": row["类别"],

        "flower_type":
            row["花材类型"],

        "count":
            int(row["每扎数量"]),

        "single_price":
            single_cost

    }



# =================
# 标题
# =================

st.title(
    "🌸 花店报价工具"
)


st.caption(
    "内部员工使用｜快速计算花材成本"
)



# =================
# 采购信息
# =================


with st.expander(
    "📦 采购信息"
):


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



batch_freight = (
    freight
    /
    total_batch
)


st.info(
    f"平均每扎运费：{round(batch_freight,2)}元"
)



# =================
# 分类整理
# =================

flower_types = {}

leaf_types = {}


for name,data in flowers.items():


    category = data["flower_type"]


    if data["type"] == "花材":


        flower_types.setdefault(
            category,
            []
        ).append(name)



    elif data["type"] == "叶材":


        leaf_types.setdefault(
            category,
            []
        ).append(name)



# =================
# 搜索
# =================

st.divider()


st.subheader(
    "🔍 快速搜索"
)


keyword = st.text_input(
    "输入花材名称（可选）"
)


search_selected = []


if keyword:


    search_result = [

        x for x in flowers.keys()

        if keyword in x

    ]


    search_selected = st.multiselect(

        "搜索结果",

        search_result

    )



# =================
# 分类选择
# =================

st.subheader(
    "🌹 选择花材"
)


selected_flowers = []


for category,items in flower_types.items():


    with st.expander(category):


        result = st.multiselect(

            "选择",

            items,

            key="flower_"+category

        )


        selected_flowers.extend(result)



st.subheader(
    "🍃 选择叶材"
)


selected_leaf = []


for category,items in leaf_types.items():


    with st.expander(category):


        result = st.multiselect(

            "选择",

            items,

            key="leaf_"+category

        )


        selected_leaf.extend(result)



selected_all = list(
    set(
        selected_flowers
        +
        selected_leaf
        +
        search_selected
    )
)



# =================
# 数量计算
# =================

cost_total = 0


if selected_all:


    st.divider()


    st.subheader(
        "✏️ 填写使用数量"
    )


    for item in selected_all:


        quantity = st.number_input(

            item,

            min_value=1,

            value=1,

            step=1,

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


        cost_total += (

            quantity

            *

            real_cost

        )
        # =================
# 计算报价
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


        # 成本 × 3

        cost_x3 = cost_total * 3


        # 基础售价

        base_price = cost_x3 + labor



        # =================
        # 售价档位
        # =================

        price_level = [

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
            1098,
            1198,
            1298

        ]


        recommend = 1298


        for price in price_level:


            if base_price <= price:

                recommend = price

                break



        st.divider()


        st.subheader(
            "📋 报价明细"
        )


        flower_text = ""


        for item in selected_all:


            quantity = st.session_state[
                "num_"+item
            ]


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


            subtotal = (

                quantity

                *

                real_cost

            )


            flower_text += (

                f"{item}×{quantity} "

            )


            st.write(

                f"""
🌸 {item}

数量：{quantity}枝

单枝成本：¥{round(real_cost,2)}

小计：¥{round(subtotal,2)}

"""

            )



        st.divider()



        col1, col2 = st.columns(2)


        with col1:

            st.metric(

                "真实成本",

                f"¥{round(cost_total,2)}"

            )


        with col2:

            st.metric(

                "基础售价",

                f"¥{round(base_price,2)}"

            )



        st.success(

            f"🌸 建议零售价：¥{recommend}"

        )



        # =================
        # 保存报价
        # =================


        if st.button(

            "💾 保存本次报价",

            use_container_width=True

        ):


            quote_id = (

                "BJ"

                +

                datetime.now().strftime(

                    "%Y%m%d%H%M%S"

                )

            )


            new_record = pd.DataFrame(

                [

                    {

                        "编号":
                        quote_id,


                        "时间":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),


                        "花材":
                        flower_text,


                        "真实成本":
                        round(
                            cost_total,
                            2
                        ),


                        "建议售价":
                        recommend

                    }

                ]

            )



            history_df = pd.concat(

                [

                    history_df,

                    new_record

                ],

                ignore_index=True

            )



            history_df.to_excel(

                history_file,

                index=False

            )


            st.success(
                "✅ 报价已保存"
            )



# =================
# 历史报价
# =================

st.divider()


st.subheader(
    "📋 历史报价"
)


if os.path.exists(history_file):


    history = pd.read_excel(

        history_file

    )


    if len(history) > 0:


        st.dataframe(

            history,

            use_container_width=True

        )


    else:


        st.info(
            "暂无报价记录"
        )


else:


    st.info(
        "暂无报价记录"
    )
