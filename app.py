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
# 标题
# =====================

st.title("🌸 花店报价工具")


# =====================
# 读取数据库
# =====================

flower_file = "flower_database.xlsx"

material_file = "material_database.xlsx"


try:

    df = pd.read_excel(
        flower_file
    )

except Exception as e:

    st.error(
        f"花材数据库读取失败：{e}"
    )

    st.stop()



try:

    material_df = pd.read_excel(
        material_file
    )

except Exception as e:

    st.error(
        f"包装数据库读取失败：{e}"
    )

    st.stop()



# =====================
# 数据清洗
# =====================

def clean_value(value):

    """
    清理Excel空值
    """

    if pd.isna(value):

        return ""

    return str(value).strip()



# 清洗花材表

df = df.fillna("")



# 清洗包装表

material_df = material_df.fillna("")



# =====================
# 花材字段检查
# =====================


flower_columns = [

    "名称",
    "类别",
    "花材类型",
    "单价",
    "每扎数量"

]


for col in flower_columns:

    if col not in df.columns:

        st.error(
            f"花材表缺少字段：{col}"
        )

        st.stop()



# =====================
# 包装字段检查
# =====================


material_columns = [

    "名称",
    "一级分类",
    "二级分类",
    "规格",
    "价格"

]


for col in material_columns:

    if col not in material_df.columns:

        st.error(
            f"包装表缺少字段：{col}"
        )

        st.stop()



# =====================
# 花材数据库整理
# =====================


flowers = {}



for _, row in df.iterrows():


    name = clean_value(
        row["名称"]
    )


    if name == "":

        continue



    # 单枝成本

    if (

        "单枝成本" in df.columns

        and

        str(row["单枝成本"]).strip() != ""

    ):

        try:

            cost = float(
                row["单枝成本"]
            )

        except:

            cost = 0


    else:


        try:

            price = float(
                row["单价"]
            )


            qty = float(
                row["每扎数量"]
            )


            if qty <= 0:

                qty = 1


            cost = price / qty


        except:

            cost = 0



    # 数量处理

    try:

        bunch_qty = int(
            float(
                row["每扎数量"]
            )
        )

    except:

        bunch_qty = 1



    flowers[name] = {


        "类别":
            clean_value(
                row["类别"]
            ),


        "花材类型":
            clean_value(
                row["花材类型"]
            ),


        "单枝成本":
            cost,


        "每扎数量":
            bunch_qty

    }




# =====================
# 包装数据库整理
# =====================


materials = {}



for _, row in material_df.iterrows():


    name = clean_value(
        row["名称"]
    )


    if name == "":
        continue


    spec = clean_value(
        row["规格"]
    )


    key = name + "_" + spec


    try:

        price = float(
            row["价格"]
        )

    except:

        price = 0



    materials[key] = {


        "名称":
            name,


        "一级分类":
            clean_value(
                row["一级分类"]
            ),


        "二级分类":
            clean_value(
                row["二级分类"]
            ),


        "规格":
            spec,


        "价格":
            price

    }




# =====================
# Session 初始化
# =====================


if "selected_flowers" not in st.session_state:

    st.session_state.selected_flowers = []



if "selected_materials" not in st.session_state:

    st.session_state.selected_materials = []



if "history" not in st.session_state:

    st.session_state.history = []



# =====================
# 采购设置
# =====================


with st.expander("⚙️采购设置"):


    freight = st.number_input(

        "本次采购运费",

        min_value=0.0,

        value=80.0

    )


    total_batch = st.number_input(

        "采购总扎数",

        min_value=1,

        value=50

    )



batch_freight = (

    freight / total_batch

)



# =====================
# 花材分类
# =====================


flower_types = {}

leaf_types = {}

dry_types = {}



for name,data in flowers.items():


    category = str(
        data["类别"]
    ).strip()


    flower_type = str(
        data["花材类型"]
    ).strip()



    # 花材

    if category in [
        "花材",
        "鲜花"
    ]:


        flower_types.setdefault(

            flower_type,

            []

        ).append(name)



    # 叶材

    elif category in [
        "叶材",
        "绿叶"
    ]:


        leaf_types.setdefault(

            flower_type,

            []

        ).append(name)



    # 干花（兼容各种写法）

    elif (

        "干" in category

        or

        "干" in flower_type

    ):


        dry_types.setdefault(

            flower_type,

            []

        ).append(name)



    elif category == "干花":


        dry_types.setdefault(

            flower_type,

            []

        ).append(name)



# =====================
# 包装分类
# =====================



material_types = {}


for name,data in materials.items():

    first = data.get("一级分类","")


    if pd.isna(first):
        first = ""


    if first.strip() == "":
        first = "其他"


    if first in ["一级分类","二级分类"]:
        continue


    material_types.setdefault(
        first,
        []
    ).append(name)



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

                key="delete_flower_"+str(item)

            ):


                st.session_state.selected_flowers.remove(item)


                del st.session_state[qty_key]


                st.rerun()



        # 运费分摊

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



for category,items in material_types.items():


    with st.expander(category):


        # 娃娃直接选择

        if category == "娃娃":


            options = []

            option_map = {}


            for name in items:


                display = (

                    materials[name]["名称"]

                    +

                    " | "

                    +

                    materials[name]["规格"]

                    +

                    " | ¥"

                    +

                    str(materials[name]["价格"])

                )


                options.append(display)


                option_map[display] = name



            selected_display = st.multiselect(

                "选择娃娃",

                options,

                key="doll_select_"+category

            )


            result = []


            for x in selected_display:

                result.append(option_map[x])





        else:


            # 普通分类显示二级分类


            sub_tree = {}



            for name in items:


                second = materials[name].get(
                    "二级分类",
                    ""
                )


                if second == "":

                   second = "其他"


                sub_tree.setdefault(

                    second,

                    []

                ).append(name)



            result = []



            for second,names in sub_tree.items():


                st.markdown(

                    f"**{second}**"

                )


                options = []

                option_map = {}



                for name in names:


                    display = (

                       materials[name]["名称"]

                       +

                       " | "

                       +

                       materials[name]["规格"]

                       +

                       " | ¥"

                       +

                       str(materials[name]["价格"])

                    )


                    options.append(display)


                    option_map[display] = name



                selected = st.multiselect(

                    "选择",

                    options,

                    key="material_"+category+"_"+second

                )



                for x in selected:


                    if x in option_map:


                        name = option_map[x]


                        if name not in result:

                            result.append(name)




        # 保存包装选择


        for name in result:


            if name not in st.session_state.selected_materials:

                st.session_state.selected_materials.append(name)   
# =====================
# 已选包装
# =====================


material_cost = 0



if st.session_state.selected_materials:


    st.divider()


    st.subheader(
        "🎁 已选包装"
    )


    for name in st.session_state.selected_materials:


        data = materials[name]


        price = data["价格"]



        # 现金代取特殊计算

        if "现金" in name:


            amount = st.number_input(

                "输入代取金额",

                min_value=0,

                value=0,

                key="cash_"+name

            )


            price = amount * 0.003



        material_cost += price



        col1,col2 = st.columns([4,1])


        with col1:


            st.write(

                f"{data['名称']} | {data['规格']} | ¥{round(price,2)}"

            )


        with col2:


            if st.button(

                "删除",

                key="delete_material_"+name

            ):


                st.session_state.selected_materials.remove(name)

                st.rerun()
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
        # 花材价格
        # =====================


        if st.session_state.selected_flowers:


            flower_price = (

                total_cost

                *

                3

            )


            labor = 100



        else:


            # 只有包装

            flower_price = 0


            labor = 0





        # =====================
        # 最终成本
        # =====================


        base_price = (

            flower_price

            +

            material_cost

            +

            labor

        )



        # =====================
        # 售价阶梯
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
        # 真实成本
        # =====================


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





        # =====================
        # 保存报价数据
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
                        materials[x]["名称"]+"-"+materials[x]["规格"]

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
        # 展示报价
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


if st.session_state.get(
    "current_quote"
):


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



    st.session_state.current_quote = None



    # 清理选择状态

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

            key.startswith("doll_")

            or

            key.startswith("qty_")

            or

            key.startswith("cash_")

        ):


            del st.session_state[key]



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
