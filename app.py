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
# 读取数据库
# =====================

df = pd.read_excel(
    flower_file
)


material_df = pd.read_excel(
    material_file
)



# =====================
# 字段检查
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
# 花材数据整理
# =====================

flowers = {}


for _, row in df.iterrows():


    if pd.isna(row["名称"]):

        continue


    name = str(
        row["名称"]
    )


    # 每扎数量

    try:

        bunch_count = int(
            float(row["每扎数量"])
        )

    except:

        bunch_count = 1



    # 单枝成本

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

materials = []


for _, row in material_df.iterrows():


    if pd.isna(row["名称"]):

        continue



    name = str(
        row["名称"]
    )



    try:

        price = float(
            row["价格"]
        )

    except:

        price = 0



    materials.append({

        "名称":

            name,


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

    })



# =====================
# 初始化
# =====================

if "selected_flowers" not in st.session_state:

    st.session_state.selected_flowers = []



if "selected_materials" not in st.session_state:

    st.session_state.selected_materials = []



if "history" not in st.session_state:

    st.session_state.history = []



if "current_quote" not in st.session_state:

    st.session_state.current_quote = None



# =====================
# 标题
# =====================

st.title(
    "🌸 花店报价工具"
)# =====================
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
# 分类整理
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
# 包装三级分类整理
# =====================

material_tree = {}



for item in materials:


    level1 = item["一级分类"]

    level2 = item["二级分类"]



    if level1 not in material_tree:

        material_tree[level1] = {}



    if level2 not in material_tree[level1]:

        material_tree[level1][level2] = []



    material_tree[level1][level2].append(item)




# =====================
# 花材选择
# =====================

st.subheader(
    "🌸 选择花材"
)



for cat,items in flower_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择",

            items,

            key="flower_"+cat

        )


        for item in result:


            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)




# =====================
# 叶材选择
# =====================

st.subheader(
    "🌿 选择叶材"
)



for cat,items in leaf_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择",

            items,

            key="leaf_"+cat

        )


        for item in result:


            if item not in st.session_state.selected_flowers:

                st.session_state.selected_flowers.append(item)




# =====================
# 干花选择
# =====================

st.subheader(
    "🌾 选择干花"
)



for cat,items in dry_types.items():


    with st.expander(cat):


        result = st.multiselect(

            "选择",

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



        qty_key = "qty_"+item



        if qty_key not in st.session_state:

            st.session_state[qty_key] = 1



        with col2:


            qty = st.number_input(

                "数量",

                min_value=1,

                step=1,

                key=qty_key,

                label_visibility="collapsed"

            )



        with col3:


            if st.button(

                "删除",

                key="del_flower_"+item

            ):


                st.session_state.selected_flowers.remove(item)


                del st.session_state[qty_key]


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
# 包装选择
# =====================

st.divider()


st.subheader(
    "🎀 选择包装/辅材"
)



for level1,level2_data in material_tree.items():


    with st.expander(level1):


        for level2,items in level2_data.items():


            st.write(
                "【"+level2+"】"
            )


            options = []


            option_map = {}



            for item in items:


                display = (

                    item["名称"]

                    +

                    "（"

                    +

                    item["规格"]

                    +

                    "）"

                    +

                    " ¥"

                    +

                    str(item["价格"])

                )


                options.append(display)


                option_map[display] = item




            selected = st.multiselect(

                "选择",

                options,

                key="material_"+level1+"_"+level2

            )



            for display in selected:


                item = option_map[display]


                if item not in st.session_state.selected_materials:


                    st.session_state.selected_materials.append(item)# =====================
# 已选包装
# =====================

material_cost = 0



if st.session_state.selected_materials:


    st.divider()


    st.subheader(
        "🎁 已选包装"
    )


    for index,item in enumerate(
        st.session_state.selected_materials
    ):


        col1,col2 = st.columns(
            [5,1]
        )


        with col1:


            st.write(

                f"{item['名称']}"

                f"（{item['规格']}）"

                f"：¥{item['价格']}"

            )



        with col2:


            if st.button(

                "删除",

                key="del_material_"+str(index)

            ):


                st.session_state.selected_materials.pop(index)

                st.rerun()



        material_cost += item["价格"]





# =====================
# 计算报价
# =====================

if st.button(
    "💰 计算报价"
):


    # 没选择任何东西

    if (

        not st.session_state.selected_flowers

        and

        not st.session_state.selected_materials

    ):


        st.warning(

            "请选择花材或包装辅材"

        )


    else:



        # =====================
        # 花材费用
        # =====================


        if st.session_state.selected_flowers:


            flower_price = (

                total_cost

                *

                3

            )


            labor = 100



        else:


            # 只买辅材

            flower_price = 0


            labor = 0




        # =====================
        # 最终价格
        # =====================


        base_price = (

            flower_price

            +

            material_cost

            +

            labor

        )



        # 自动匹配售价

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




        # 实际成本

        real_cost = (

            total_cost

            +

            material_cost

            +

            labor

        )



        profit = (

            recommend

            -

            real_cost

        )




        # 保存当前报价

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

                        +

                        "（"

                        +

                        x["规格"]

                        +

                        "）"

                        for x in st.session_state.selected_materials

                    ]

                ),



            "真实成本":

                round(

                    real_cost,

                    2

                ),



            "售价":

                recommend

        }




        # =====================
        # 展示报价
        # =====================


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

            f"包装辅材：¥{round(material_cost,2)}"

        )



        if labor > 0:


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

if st.session_state.current_quote:


    st.divider()



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


    st.session_state.selected_flowers = []


    st.session_state.selected_materials = []



    for key in list(

        st.session_state.keys()

    ):


        if (

            key.startswith("qty_")

            or

            key.startswith("flower_")

            or

            key.startswith("leaf_")

            or

            key.startswith("dry_")

            or

            key.startswith("material_")

        ):


            del st.session_state[key]



    st.session_state.current_quote = None



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
