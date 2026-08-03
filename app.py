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
# 文件
# =====================

flower_file = "flower_database.xlsx"

material_file = "material_database.xlsx"



# =====================
# 读取Excel
# =====================

df = pd.read_excel(
    flower_file
)


material_df = pd.read_excel(
    material_file
)



# =====================
# 花材检查
# =====================

flower_columns = [

    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"

]


for c in flower_columns:

    if c not in df.columns:

        st.error(
            f"花材表缺少字段：{c}"
        )

        st.stop()



# =====================
# 包装检查
# =====================

material_columns = [

    "名称",
    "一级分类",
    "二级分类",
    "规格",
    "价格"

]


for c in material_columns:

    if c not in material_df.columns:

        st.error(
            f"包装表缺少字段：{c}"
        )

        st.stop()



# =====================
# 花材整理
# =====================


flowers = {}


for _,row in df.iterrows():


    name = row["名称"]


    if pd.isna(name):

        continue



    try:

        bunch_count = int(
            float(row["每扎数量"])
        )

    except:

        bunch_count = 1



    try:


        if (

            "单枝成本" in df.columns

            and

            pd.notna(row["单枝成本"])

        ):

            cost = float(
                row["单枝成本"]
            )


        else:


            cost = (

                float(row["单价"])

                /

                bunch_count

            )


    except:


        cost = 0



    flowers[str(name)] = {


        "类别":

            str(row["类别"])
            if pd.notna(row["类别"])
            else "花材",



        "花材类型":

            str(row["花材类型"])
            if pd.notna(row["花材类型"])
            else "其他花材",



        "单枝成本":

            cost,



        "每扎数量":

            bunch_count

    }# =====================
# 包装数据整理
# =====================

materials = {}


for _,row in material_df.iterrows():


    name = row["名称"]


    # 跳过空行
    if pd.isna(name):

        continue



    # 价格处理

    try:

        price = float(
            row["价格"]
        )

    except:

        price = 0



    materials[str(name)] = {


        "一级分类":

            str(row["一级分类"])
            if pd.notna(row["一级分类"])
            else "其他",



        "二级分类":

            str(row["二级分类"])
            if pd.notna(row["二级分类"])
            else "",



        "规格":

            str(row["规格"])
            if pd.notna(row["规格"])
            else "",



        "价格":

            price

    }



# =====================
# 初始化
# =====================


if "selected_flowers" not in st.session_state:

    st.session_state.selected_flowers = []



if "selected_materials" not in st.session_state:

    st.session_state.selected_materials = []



if "history" not in st.session_state:

    st.session_state.history = []




# =====================
# 标题
# =====================


st.title(
    "🌸 花店报价工具"
)




# =====================
# 采购设置
# =====================


with st.expander(
    "⚙️ 采购设置"
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




# =====================
# 花材分类
# =====================


flower_types = {}

leaf_types = {}

dry_types = {}



for name,data in flowers.items():


    category = data["类别"]


    flower_type = data["花材类型"]



    if category == "花材":


        if flower_type not in flower_types:

            flower_types[flower_type] = []


        flower_types[flower_type].append(name)




    elif category == "叶材":


        if flower_type not in leaf_types:

            leaf_types[flower_type] = []


        leaf_types[flower_type].append(name)




    elif category == "干花":


        if flower_type not in dry_types:

            dry_types[flower_type] = []


        dry_types[flower_type].append(name)





# =====================
# 包装分类
# =====================


material_types = {}



for name,data in materials.items():


    category = data["一级分类"]



    if category not in material_types:

        material_types[category] = []



    material_types[category].append(name)





# =====================
# 选择花材
# =====================


st.subheader(
    "🌸 选择花材"
)



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


st.subheader(
    "🌿 选择叶材"
)



for cat,items in leaf_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择叶材",

            items,

            key="leaf_"+cat

        )


        for item in result:


            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)# =====================
# 选择干花
# =====================


st.subheader(
    "🌾 选择干花"
)



for cat,items in dry_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择干花",

            items,

            key="dry_"+cat

        )


        for item in result:


            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)




# =====================
# 已选花材计算
# =====================


total_cost = 0



if st.session_state.selected_flowers:


    st.divider()


    st.subheader(
        "📋 已选花材"
    )


    for item in st.session_state.selected_flowers:



        col1,col2,col3 = st.columns(
            [3,1,1]
        )



        with col1:

            st.write(item)



        key = "quantity_"+item



        if key not in st.session_state:

            st.session_state[key]=1



        with col2:


            qty = st.number_input(

                "数量",

                min_value=1,

                step=1,

                key=key,

                label_visibility="collapsed"

            )



        with col3:


            if st.button(

                "删除",

                key="del_"+item

            ):


                st.session_state.selected_flowers.remove(item)

                st.rerun()



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



        total_cost += (

            qty

            *

            single_cost

        )





# =====================
# 选择包装
# =====================


st.divider()


st.subheader(
    "🎀 选择包装/辅材"
)



for category,items in material_types.items():


    with st.expander(category):


        result = st.multiselect(

            "选择包装",

            items,

            key="material_"+category

        )



        for item in result:


            if item not in st.session_state.selected_materials:


                st.session_state.selected_materials.append(item)





# =====================
# 已选包装
# =====================


material_cost = 0



if st.session_state.selected_materials:


    st.subheader(
        "🎁 已选包装"
    )



    for item in st.session_state.selected_materials:


        price = materials[item]["价格"]


        material_cost += price



        st.write(

            f"{item}：¥{price}"

        )





# =====================
# 计算报价
# =====================


if st.button(
    "💰 计算报价"
):


    if not st.session_state.selected_flowers:


        st.warning(
            "请选择花材"
        )


    else:


        # 花材成本×3

        flower_price = (

            total_cost

            *

            3

        )


        # 人工

        labor = 100



        base_price = (

            flower_price

            +

            material_cost

            +

            labor

        )



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



        real_cost = (

            total_cost

            +

            material_cost

            +

            labor

        )



        profit = recommend - real_cost



        st.session_state.current_quote = {


            "时间":

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),



            "花材":

                "、".join(
                    st.session_state.selected_flowers
                ),



            "包装":

                "、".join(
                    st.session_state.selected_materials
                ),



            "成本":

                round(real_cost,2),



            "售价":

                recommend

        }



        st.divider()


        st.subheader(
            "🌸 报价结果"
        )


        st.write(
            f"花材成本：¥{round(total_cost,2)}"
        )


        st.write(
            f"花材成本×3：¥{round(flower_price,2)}"
        )


        st.write(
            f"包装成本：¥{round(material_cost,2)}"
        )


        st.write(
            "制作费用：¥100"
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


    if st.button(
        "💾 保存报价"
    ):


        st.session_state.history.append(

            st.session_state.current_quote

        )


        st.success(
            "报价已保存"
        )





# =====================
# 新建报价
# =====================


if st.button(
    "🔄 新建报价"
):


    st.session_state.selected_flowers=[]

    st.session_state.selected_materials=[]



    for key in list(st.session_state.keys()):


        if (

            key.startswith("quantity_")

            or key.startswith("flower_")

            or key.startswith("leaf_")

            or key.startswith("dry_")

            or key.startswith("material_")

        ):

            del st.session_state[key]



    if "current_quote" in st.session_state:

        del st.session_state["current_quote"]



    st.rerun()




# =====================
# 历史记录
# =====================


if st.session_state.history:


    st.divider()


    st.subheader(
        "📋 历史报价"
    )


    st.dataframe(

        pd.DataFrame(
            st.session_state.history
        ),

        use_container_width=True

    )
