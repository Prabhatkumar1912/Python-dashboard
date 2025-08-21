import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="Hostel Power Usage", page_icon=":bar_chart:", layout="wide")
st.title("⚡ Hostel Electricity Usage Dashboard")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

# ---------------- Load Data ----------------
df = pd.read_csv("sample_power_usage_500.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["month_year"] = df["Date"].dt.to_period("M").astype(str)

# ---------------- Interactivity Filters with Select All ----------------
room_options = sorted(df["Room"].unique())
month_options = sorted(df["month_year"].unique())

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    select_all_rooms = st.checkbox("Select All Rooms", value=True)
    if select_all_rooms:
        selected_rooms = st.multiselect("Filter by Room", room_options, default=room_options, key="rooms")
    else:
        selected_rooms = st.multiselect("Filter by Room", room_options, key="rooms")

with col_filter2:
    select_all_months = st.checkbox("Select All Months", value=True)
    if select_all_months:
        selected_months = st.multiselect("Filter by Month-Year", month_options, default=month_options, key="months")
    else:
        selected_months = st.multiselect("Filter by Month-Year", month_options, key="months")

filtered_df = df[df["Room"].isin(selected_rooms) & df["month_year"].isin(selected_months)]
monthly_consumption = filtered_df.groupby(["month_year", "Room"], as_index=False)["Units_Consumed"].sum()
total_monthly = filtered_df.groupby("month_year", as_index=False)["Units_Consumed"].sum()

# ---------------- Monthly Consumption per Room ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Monthly Consumption by Room")
    fig1 = px.bar(
        monthly_consumption,
        x="month_year",
        y="Units_Consumed",
        color="Room",
        barmode="group",
        template="seaborn",
        title="Monthly Consumption by Room"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📈 Total Monthly Consumption (All Rooms)")
    fig2 = px.line(
        total_monthly,
        x="month_year",
        y="Units_Consumed",
        markers=True,
        title="Total Monthly Consumption"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- Average vs Highest Rooms ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("📉 Average Monthly Consumption per Room")
    avg_monthly = monthly_consumption.groupby("Room", as_index=False)["Units_Consumed"].mean()
    fig_avg = px.bar(
        avg_monthly,
        x="Room",
        y="Units_Consumed",
        title="Average Monthly Consumption per Room",
        color="Units_Consumed",
        color_continuous_scale="Greens"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("🏆 Highest Consuming Rooms per Month (Matplotlib)")
    if not monthly_consumption.empty:
        highest_rooms = monthly_consumption.loc[
            monthly_consumption.groupby("month_year")["Units_Consumed"].idxmax()
        ]
        fig, ax = plt.subplots(figsize=(6,4))
        bars = ax.bar(highest_rooms["month_year"], highest_rooms["Units_Consumed"], color="orange")

        # Add room names above bars
        for bar, room in zip(bars, highest_rooms["Room"]):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + 5,
                room,
                ha='center',
                va='bottom',
                fontsize=9,
                rotation=45
            )

        ax.set_title("Highest Consuming Rooms per Month", fontsize=12)
        ax.set_xlabel("Month-Year")
        ax.set_ylabel("Units Consumed")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("No data for selected filters.")

# ---------------- Raw Data ----------------
st.subheader("🗂 Raw Data Preview")
da=pd.read_csv("sample_power_usage_500.csv")
st.dataframe(da.head(100))  # interactive table with scroll

# ---------------- Download Processed Data ----------------
st.subheader("⬇️ Download Processed Data")

# Monthly consumption per room
csv_monthly = monthly_consumption.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Monthly Consumption Data",
    data=csv_monthly,
    file_name="monthly_consumption.csv",
    mime="text/csv"
)

# Highest consuming rooms per month
if not monthly_consumption.empty:
    csv_highest = highest_rooms.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Highest Consuming Rooms Data",
        data=csv_highest,
        file_name="highest_consuming_rooms.csv",
        mime="text/csv"
    )

# Full processed dataset
csv_full = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Full Processed Dataset",
    data=csv_full,
    file_name="processed_data.csv",
    mime="text/csv"
)
