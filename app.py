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

flower_file = "flower_database.xlsx"

material_file = "material_database.xlsx"


df = pd.read_excel(
    flower_file
)


material_df = pd.read_excel(
    material_file
)



# =====================
# 花材字段检查
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
            f"花材表缺少字段：{c}"
        )

        st.stop()



# =====================
# 包装字段检查
# =====================

material_columns = [
    "名称",
    "一级分类",
    "二级分类",
    "规格"
]


for c in material_columns:

    if c not in material_df.columns:

        st.error(
            f"包装表缺少字段：{c}"
        )

        st.stop()



# =====================
# 花材数据整理
# =====================

# =====================
# 花材数据整理
# =====================

flowers = {}


for _, row in df.iterrows():

    name = row["名称"]


    # 计算单枝成本

    if (
        "单枝成本" in df.columns
        and pd.notna(row["单枝成本"])
    ):

        cost = float(
            row["单枝成本"]
        )

    else:

        try:

            price = float(
                row["单价"]
            )

            bunch_count = float(
                row["每扎数量"]
            )

            if bunch_count <= 0:
                bunch_count = 1


            cost = price / bunch_count


        except:

            cost = 0



    # 处理每扎数量

    try:

        bunch_count = int(
            float(row["每扎数量"])
        )


    except:

        bunch_count = 1



    flowers[name] = {


        "类别":

            str(row["类别"])
            if pd.notna(row["类别"])
            else "花材",



        "花材类型":

            str(row["花材类型"])
            if pd.notna(row["花材类型"])
            else "其他",



        "单枝成本":

            cost,



        "每扎数量":

            bunch_count

    }


# =====================
# 包装数据整理
# =====================

materials = {}


for _, row in material_df.iterrows():

    name = row["名称"]


    # 价格处理

    price = 0


    if "价格" in material_df.columns:

        raw_price = row["价格"]


        try:

            price = float(raw_price)


        except:

            price = 0



    # 现金代取特殊处理

    if "现金代取" in str(name):

        price = 0.003



    materials[name] = {


        "一级分类":

            str(row["一级分类"]),


        "二级分类":

            str(row["二级分类"]),


        "规格":

            str(row["规格"]),


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
# 分类整理
# =====================


flower_types = {}

leaf_types = {}

dry_types = {}



for name,data in flowers.items():


    category = data["类别"]

    flower_type = data["花材类型"]



    # 花材

    if category == "花材":


        if flower_type not in flower_types:

            flower_types[flower_type] = []


        flower_types[flower_type].append(name)



    # 叶材

    elif category == "叶材":


        if flower_type not in leaf_types:

            leaf_types[flower_type] = []


        leaf_types[flower_type].append(name)



    # 干花

    elif category == "干花":


        if flower_type not in dry_types:

            dry_types[flower_type] = []


        dry_types[flower_type].append(name)




# =====================
# 包装分类整理
# =====================


material_types = {}



for name,data in materials.items():


    first = data["一级分类"]

    second = data["二级分类"]



    # 娃娃特殊处理

    if first == "娃娃":


        second = "娃娃款式"



    if first not in material_types:

        material_types[first] = {}



    if second not in material_types[first]:

        material_types[first][second] = []



    material_types[first][second].append(name)# =====================
# 采购设置
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

                st.session_state.selected_flowers.append(item)




# =====================
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
# 已选花材
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



        key = "qty_"+item



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




        # 花材成本


        freight_cost = (

            batch_freight

            /

            flowers[item]["每扎数量"]

        )



        single_cost = (

            flowers[item]["单枝成本"]

            +

            freight_cost

        )



        total_cost += (

            qty *

            single_cost

        )





# =====================
# 选择包装/辅材
# =====================


st.divider()


st.subheader(
    "🎀 选择包装/辅材"
)



for first,second_dict in material_types.items():


    with st.expander(first):


        for second,items in second_dict.items():


            # 娃娃不显示二级标题

            if first != "娃娃":


                st.markdown(

                    f"### 【{second}】"

                )



            result = st.multiselect(



                "选择",



                [

                    f"{name} | {materials[name]['规格']} | ¥{materials[name]['价格']}"

                    for name in items

                ],


                key="material_"+first+"_"+second



            )



            for value in result:



                name = value.split(" | ")[0]



                if name not in [


                    x["名称"]

                    for x in st.session_state.selected_materials

                ]:


                    st.session_state.selected_materials.append(



                        {


                            "名称":name,


                            "规格":materials[name]["规格"],


                            "价格":materials[name]["价格"]


                        }


                    )





# =====================
# 已选包装
# =====================


material_cost = 0



if st.session_state.selected_materials:


    st.divider()


    st.subheader(

        "🎁 已选包装"

    )



    for item in st.session_state.selected_materials:



        name = item["名称"]

        price = item["价格"]



        # 现金代取

        if "现金代取" in name:


            amount = st.number_input(

                "请输入代取金额",

                min_value=0,

                value=0,

                key="cash_"+name

            )


            price = amount * 0.003



        material_cost += price



        col1,col2 = st.columns([4,1])



        with col1:


            st.write(

                f"{name} | {item['规格']} | ¥{round(price,2)}"

            )


        with col2:


            if st.button(

                "删除",

                key="remove_"+name

            ):


                st.session_state.selected_materials.remove(item)

                st.rerun()# =====================
# 计算报价
# =====================


if st.button(
    "💰 计算报价"
):


    # 允许：
    # 1. 只买花材
    # 2. 只买包装
    # 3. 花材+包装


    if (
        not st.session_state.selected_flowers
        and
        not st.session_state.selected_materials
    ):


        st.warning(
            "请至少选择花材或包装"
        )


    else:



        # =====================
        # 人工费用
        # =====================

        labor = 100



        # 花材售价逻辑

        flower_price = total_cost * 3



        # 基础售价

        base_price = (

            flower_price

            +

            material_cost

            +

            labor

        )



        # =====================
        # 推荐售价阶梯
        # =====================


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




        # =====================
        # 成本计算
        # =====================


        real_cost = (

            total_cost

            +

            material_cost

            +

            labor

        )



        profit = recommend - real_cost




        # =====================
        # 保存当前报价
        # =====================


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

                [

                    x["名称"]

                    for x in st.session_state.selected_materials

                ]

            ),



            "花材成本":

            round(

                total_cost,

                2

            ),



            "包装成本":

            round(

                material_cost,

                2

            ),



            "建议售价":

            recommend



        }




        # =====================
        # 展示结果
        # =====================


        st.divider()



        st.subheader(

            "🌸 报价结果"

        )



        st.write(

            f"花材真实成本：¥{round(total_cost,2)}"

        )


        st.write(

            f"花材成本×3：¥{round(flower_price,2)}"

        )


        st.write(

            f"包装辅材：¥{round(material_cost,2)}"

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


    st.session_state.selected_flowers = []


    st.session_state.selected_materials = []



    for key in list(

        st.session_state.keys()

    ):



        if (

            key.startswith("flower_")

            or

            key.startswith("leaf_")

            or

            key.startswith("dry_")

            or

            key.startswith("material_")

            or

            key.startswith("qty_")

            or

            key.startswith("cash_")

        ):


            del st.session_state[key]




    if "current_quote" in st.session_state:


        del st.session_state["current_quote"]



    st.rerun()





# =====================
# 历史报价
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
