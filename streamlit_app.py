"""
streamlit_app.py

Copyright (c) 2022 yoririn

This software is released under the MIT license.
See https://opensource.org/licenses/MIT

"""

import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import io
import pickle
import time

if "x_interval_list" not in st.session_state:
    st.session_state.x_interval_list = [0]
if "y_interval_list" not in st.session_state:
    st.session_state.y_interval_list = [0]
if "x_interval" not in st.session_state:
    st.session_state.x_interval = 0
if "y_interval" not in st.session_state:
    st.session_state.y_interval = 0
if "color_max" not in st.session_state:
    st.session_state.color_max = 0
if "color_min" not in st.session_state:
    st.session_state.color_min = 0
if "color_interval_list" not in st.session_state:
    st.session_state.color_interval_list = [0]
if "color_interval" not in st.session_state:
    st.session_state.color_interval = 0
if "x_label" not in st.session_state:
    st.session_state.x_label = "x"
if "y_label" not in st.session_state:
    st.session_state.y_label = "y"
if "colorbar_label" not in st.session_state:
    st.session_state.colorbar_label = "z()"
if "axis_label_size" not in st.session_state:
    st.session_state.axis_label_size = 18
if "ticks_label_size" not in st.session_state:
    st.session_state.ticks_label_size = 12
if "df" not in st.session_state:
    st.session_state.df = None
if "df_width" not in st.session_state:
    st.session_state.df_width = 0
if "df_height" not in st.session_state:
    st.session_state.df_height = 0
if "df_max" not in st.session_state:
    st.session_state.df_max = 0
if "df_min" not in st.session_state:
    st.session_state.df_min = 0
if "fig" not in st.session_state:
    st.session_state.fig = None
if "fig_info" not in st.session_state:
    st.session_state.fig_info = []
if "cmap" not in st.session_state:
    st.session_state.cmap = "magma"
if "cmap_isReversed" not in st.session_state:
    st.session_state.cmap_isReversed = False

# @st.cache
def load_data(file):
    if(file.type == "text/csv"):
        df = pd.read_csv(file,header=None).dropna(axis=1)
    else:
        df_file = pd.ExcelFile(file)
        df = df_file.parse(sheet_name=0,header=None).dropna(axis=1)
    return df

def decide_interval(length):
    if length >= 50:
        return ((length//5)//10)*10
    elif length >= 25:
        return ((length//5)//5)*5
    else:
        return 1

# @st.cache
def change_color_intervals():
    if(st.session_state.color_max <= st.session_state.color_min):
        return
    mm_range = st.session_state.color_max-st.session_state.color_min
    _ = make_divisors(mm_range)
    return [i for i in _ if mm_range/i < 21]
def make_divisors(n):
    multiplier = 10**len(str(n).split('.')[-1])
    n_bymultiplier = int(n*multiplier) # Multiply a decimal by a power of 10 to make it an integer
    lower_divisors , upper_divisors = [], []
    for i in range(1, n_bymultiplier+1):
        if i * i > n_bymultiplier:
            break
        if n_bymultiplier % i == 0:
            lower_divisors.append(i)
            if i != n_bymultiplier // i:
                upper_divisors.append(n_bymultiplier//i)
    return [i/multiplier for i in lower_divisors + upper_divisors[::-1]]
    


def update_form():
    st.session_state.fig = None

    file = st.session_state.uploaded_file
    try:
        if(file.type == "application/octet-stream"):
            (st.session_state.df, st.session_state.x_interval, st.session_state.y_interval,
                st.session_state.color_max, st.session_state.color_min,
                st.session_state.color_interval, st.session_state.x_label,
                st.session_state.y_label, st.session_state.colorbar_label,
                st.session_state.axis_label_size, st.session_state.ticks_label_size,
                st.session_state.cmap, st.session_state.cmap_isReversed
                ) = pickle.load(file)
            st.session_state.df_width = df_width =  len(st.session_state.df.columns)
            st.session_state.df_height = df_height = len(st.session_state.df)
        else:
            # Convert uploaded file to pandas dataframe
            st.session_state.df = df = load_data(file)
            st.session_state.df_max = df_max = float(df.max().max())
            st.session_state.df_min = df_min = float(df.min().min())
            st.session_state.df_width = df_width =  len(st.session_state.df.columns)
            st.session_state.df_height = df_height = len(st.session_state.df)

            st.session_state.x_interval = decide_interval(df_width)
            st.session_state.y_interval = decide_interval(df_height)
            st.session_state.color_max = math.ceil(df_max)
            st.session_state.color_min = math.floor(df_min)
            st.session_state.color_interval = (st.session_state.color_max-st.session_state.color_min)/10

        _ = list(range(1,10))+[i for i in range(10, df_width, 5)]+[df_width] if df_width > 10 else list(range(1, df_width+1))
        st.session_state.x_interval_list = [i for i in _ if df_width/i < 21]
        _ = list(range(1,10))+[i for i in range(10, df_height, 5)]+[df_height] if df_height > 10 else list(range(1, df_height+1))
        st.session_state.y_interval_list = [i for i in _ if df_height/i < 21]
        st.session_state.color_interval_list = change_color_intervals()
    except(AttributeError):
        time.sleep(0.1)

# @st.cache
def draw():
    color_max = st.session_state.color_max
    color_min = st.session_state.color_min
    color_interval = st.session_state.color_interval
    cmap = st.session_state.cmap
    if color_max > color_min:
        st.session_state.color_interval_list = _ = change_color_intervals()
        if color_interval not in _:
            st.session_state.color_interval = color_interval = (st.session_state.color_max-st.session_state.color_min)/10
        df_width = st.session_state.df_width
        df_height = st.session_state.df_height
        fig = plt.figure(figsize=(9,6), dpi=100)
        ax = fig.add_subplot(111)
        extent = 0.5, df_width+0.5, df_height+0.5, 0.5
        cbar_step = int((color_max-color_min)/st.session_state.color_interval)
        cbar_norm = mpl.colors.Normalize(color_min, color_max)
        if(cmap_isReversed):
            cmap = cmap+"_r"
        ax.matshow(st.session_state.df, norm=cbar_norm, cmap=cmap, extent=extent)
        cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=cbar_norm, cmap=cmap),ax=ax,)
        
        
        ax.xaxis.set_label_position('top')
        ax.yaxis.set_ticks_position('both')
        cbar.ax.set_yticks([color_min+i*color_interval for i in range(cbar_step+1)])
        cbar.ax.set_yticklabels([fr"$\leq {float(color_min)}$"]+[f"${round(color_min+(i+1)*color_interval, 3)}$" for i in range(cbar_step-1)]+[fr"$\geq {float(color_max)}$"])
        ax.set_xticks([1]+[i for i in range(int(x_interval), df_width+1, int(x_interval))])
        ax.set_yticks([1]+[i for i in range(int(y_interval), df_height+1, int(y_interval))])
        cbar.ax.tick_params(axis='y', labelsize=ticks_label_size)
        ax.tick_params(axis='x', labelsize=ticks_label_size)
        ax.tick_params(axis='y', labelsize=ticks_label_size)
        cbar.set_label(fr"${colorbar_label}$", fontsize=axis_label_size)
        ax.set_xlabel(fr"${x_label}$", fontsize=axis_label_size)
        ax.set_ylabel(fr"${y_label}$", fontsize=axis_label_size)
        
        st.session_state.fig = fig
        st.session_state.fig_info = [st.session_state.df, int(x_interval), int(y_interval)
            , color_max, color_min, color_interval, x_label, y_label, colorbar_label
            , axis_label_size, ticks_label_size, st.session_state.cmap, cmap_isReversed]
        st.experimental_rerun()

def pickle_figinfo(figinfo):
    """Pickle the model inside bytes. In our case, it is the "same" as
    storing a file, but in RAM.
    """
    data = io.BytesIO()
    pickle.dump(figinfo, data)
    return data

# tab1, tab2 = st.tabs(["Main", "Color maps"])
# with tab1:
st.title("CsvHeatmapper")
uploaded_file = st.file_uploader("Choose a CSV-like file", type=[".csv", ".xlsx", ".chwk"], on_change=update_form, key="uploaded_file")

with st.form(key="draw_form"):
    # col1, col2, col3 = st.columns(3)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.subheader("Axis scale")
        x_interval = st.selectbox(label="x-Interval", options=st.session_state.x_interval_list, index=st.session_state.x_interval_list.index(st.session_state.x_interval))
        y_interval = st.selectbox(label="y-Interval", options=st.session_state.y_interval_list, index=st.session_state.y_interval_list.index(st.session_state.y_interval))
    with col2:
        st.subheader("Color scale")
        color_max = st.session_state.color_max = float(st.text_input(label="Max", value=st.session_state.color_max))
        color_min = st.session_state.color_min = float(st.text_input(label="Min", value=st.session_state.color_min))
        color_interval = st.session_state.color_interval = float(st.selectbox(label="Interval", options=st.session_state.color_interval_list,
            index=st.session_state.color_interval_list.index(st.session_state.color_interval)))
    with col3:
        st.subheader("Label")
        x_label = st.text_input(label="x-Label", value=st.session_state.x_label)
        y_label = st.text_input(label="y-Label", value=st.session_state.y_label)
        colorbar_label = st.text_input(label="Colorbar Label", value=st.session_state.colorbar_label)
    # col4, col5 = st.columns(2)
    with col4:
        st.subheader("Label size")
        axis_label_size= st.slider("Axis Label", 1, 40, value=st.session_state.axis_label_size)
        ticks_label_size= st.slider("Ticks Label", 1, 40, value=st.session_state.ticks_label_size)
    with col5:
        st.subheader("Color map")
        cmaps = list(mpl.cm._colormaps._cmaps.keys())
        cm_num = int(len(cmaps)/2)
        cmap = st.session_state.cmap = st.selectbox("", cmaps[:cm_num], index=cmaps[:cm_num].index(st.session_state.cmap))
        cmap_isReversed = st.checkbox("reversed", value=st.session_state.cmap_isReversed)
        st.markdown("[Check out Colormaps here.](https://matplotlib.org/stable/gallery/color/colormap_reference.html)")

    draw_button = st.form_submit_button(label="Draw")
    if draw_button and st.session_state.df is not None:
        draw()

if st.session_state.fig:
    fn = 'heatmap.png'
    img = io.BytesIO()
    st.session_state.fig.savefig(img, format='png')
    col1, col2 = st.columns([4,1])
    with col1:
        st.pyplot(st.session_state.fig)
    with col2:
        btn = st.download_button(
        label="Download image",
        data=img,
        file_name=fn,
        mime="image/png"
        )
        btn2 = st.download_button(
        label="Download work file(.chwk)",
        data=pickle_figinfo(st.session_state.fig_info),
        file_name="image.chwk",
        )
# with tab2:
#     with open("cm.png", "rb") as img:
#         encoded_string = base64.b64encode(img.read())
#         page_bg_img = f'''
#         <style>
#         .stApp {{
#         background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
#         background-repeat: no-repeat;
#         background-position: center;
#         background-size: 85%;
#         }}
#         </style>
#         '''
#         st.markdown(page_bg_img, unsafe_allow_html=True)

#     st.radio("Color Map", [i for i in range(28)], horizontal=True)