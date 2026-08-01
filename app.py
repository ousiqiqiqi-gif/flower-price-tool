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
# 数据读取
# =====================

file_name = "flower_database.xlsx"

df = pd.read_excel(file_name)


required = [
    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"
]


for c in required:
    if c not in df.columns:
        st.error(f"缺少字段：{c}")
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

        "类型": row["花材类型"],

        "单枝成本": cost,

        "每扎数量": int(row["每扎数量"])

    }



# =====================
# 初始化
# =====================

if "selected" not in st.session_state:

    st.session_state.selected = []


if "history" not in st.session_state:

    st.session_state.history = []



# =====================
# 标题
# =====================

st.title("🌸 花店报价工具")



# =====================
# 搜索
# =====================

st.subheader("🔍 搜索花材")


keyword = st.text_input(
    "输入花材名称"
)



if keyword:


    results = [

        x for x in flowers.keys()

        if keyword in x

    ]


    if results:


        for item in results:


            col1,col2 = st.columns([3,1])


            with col1:

                st.write(
                    f"{item}  单枝成本 {round(flowers[item]['单枝成本'],2)}元"
                )


            with col2:

                if st.button(
                    "添加",
                    key="add_"+item
                ):

                    if item not in st.session_state.selected:

                        st.session_state.selected.append(item)

                        st.rerun()



# =====================
# 分类选择
# =====================

st.subheader("选择花材")


categories={}


for name,data in flowers.items():

    if data["类别"]=="花材":

        cat=data["类型"]

        if cat not in categories:

            categories[cat]=[]

        categories[cat].append(name)



for cat,items in categories.items():

    with st.expander(cat):


        choose = st.multiselect(

            "选择",

            items,

            key="cat_"+cat

        )


        for item in choose:

            if item not in st.session_state.selected:

                st.session_state.selected.append(item)




# =====================
# 已选花材
# =====================


if st.session_state.selected:


    st.divider()

    st.subheader("📋 已选花材")


    total_cost=0



    for item in st.session_state.selected:


        num_key="num_"+item


        if num_key not in st.session_state:

            st.session_state[num_key]=1



        col1,col2,col3=st.columns(
            [3,1,1]
        )


        with col1:

            st.write(item)


        with col2:


            st.session_state[num_key]=st.number_input(

                "数量",

                min_value=1,

                step=1,

                key=num_key,

                label_visibility="collapsed"

            )


        with col3:


            if st.button(
                "删除",
                key="del_"+item
            ):

                st.session_state.selected.remove(item)

                st.rerun()



        qty=st.session_state[num_key]


        total_cost += (

            qty
            *
            flowers[item]["单枝成本"]

        )



    st.divider()


    # =====================
    # 报价
    # =====================


    if st.button(
        "💰 生成报价"
    ):



        labor=100


        base_price=(

            total_cost*3

            +

            labor

        )


        levels=[

            56,68,88,98,
            128,158,198,
            228,268,298,
            358,398,498,
            598,698,898,
            998,1298

        ]


        price=1298


        for p in levels:

            if base_price<=p:

                price=p

                break



        profit=price-total_cost-labor



        st.session_state.quote={

            "时间":

            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),

            "花材":

            "、".join(st.session_state.selected),

            "成本":

            round(total_cost,2),

            "售价":

            price

        }



        st.success(
            "报价生成完成"
        )


        st.divider()


        st.subheader(
            "🌸 报价结果"
        )


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
            f"建议售价：¥{price}"
        )


        st.write(
            f"预计利润：¥{round(profit,2)}"
        )



# =====================
# 保存
# =====================


if "quote" in st.session_state:


    if st.button(
        "💾 保存报价"
    ):


        st.session_state.history.append(

            st.session_state.quote

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


    st.session_state.selected=[]


    for key in list(st.session_state.keys()):

        if key.startswith("num_"):

            del st.session_state[key]


    if "quote" in st.session_state:

        del st.session_state["quote"]


    st.rerun()



# =====================
# 历史记录
# =====================


if st.session_state.history:


    st.divider()

    st.subheader(
        "📋 最近报价"
    )


    st.dataframe(

        pd.DataFrame(
            st.session_state.history
        ),

        use_container_width=True

    )
