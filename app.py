import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Olist 360 Business Intelligence", layout="wide")

# --- 1. โหลดข้อมูล (ใช้ Path แบบ Relative เพื่อให้รันบนเว็บได้) ---
@st.cache_data
def load_all_data():
    # สังเกตว่าจารย์ลบ D:\db\ ออกแล้วนะครับ เพื่อให้มันหาไฟล์ในโฟลเดอร์เดียวกัน
    rfm = pd.read_csv('rfm_result.csv')
    forecast = pd.read_csv('sales_forecast.csv')
    top_cats = pd.read_csv('top_categories.csv')
    forecast['ds'] = pd.to_datetime(forecast['ds'])
    return rfm, forecast, top_cats

rfm_table, forecast_data, top_cats = load_all_data()

priority_order = ['Champions (สุดยอดลูกค้า)', 'Loyal Customers (ขาประจำ)', 
                  'New Customers (ลูกค้าใหม่)', 'At Risk (เริ่มห่างเหิน)', 'Lost (ขาจรที่หายไป)']
rfm_table['Segment'] = pd.Categorical(rfm_table['Segment'], categories=priority_order, ordered=True)

# --- 2. Dashboard Layout ---
st.title("📦 Olist End-to-End Analytics")

tabs = st.tabs(["🏠 Executive Summary", "📈 Sales Forecast", "👥 Customer RFM", "🔍 Deep Dive"])

# --- Tab 1: Project 1 Content ---
with tabs[0]:
    st.subheader("Business Snapshot (Project 1)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Top 10 Product Categories")
        fig_bar = px.bar(top_cats, x='price', y='product_category_name_english', orientation='h', 
                         color='price', color_continuous_scale='Viridis')
        st.plotly_chart(fig_bar, width='stretch')
    with col2:
        st.info("💡 Insight: หมวดหมู่สินค้ากลุ่ม Health & Beauty และ Watches เป็นตัวขับเคลื่อนรายได้หลัก")

# --- Tab 2 & 3: เหมือนเดิม (Project 2 & 3) ---
with tabs[1]:
    st.subheader("Future Predictions (Project 2)")
    st.markdown("พยากรณ์ยอดขายพร้อมช่วงความเชื่อมั่น (Upper/Lower Bound)")
    
    fig_forecast = go.Figure()

    # เส้นขอบบน (Upper Bound)
    fig_forecast.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat_upper'],
        mode='lines', line=dict(width=0), showlegend=False, name='Upper Bound'
    ))

    # เส้นขอบล่าง (Lower Bound) - ใช้ fill='tonexty' เพื่อระบายสีระหว่างกลาง
    fig_forecast.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat_lower'],
        mode='lines', line=dict(width=0), fill='tonexty', 
        fillcolor='rgba(255, 75, 75, 0.2)', showlegend=False, name='Lower Bound'
    ))

    # เส้นพยากรณ์หลัก (yhat) - เส้นสีแดงเข้ม
    fig_forecast.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat'],
        mode='lines', line=dict(color='#FF4B4B', width=3), name='Predicted Sales'
    ))

    fig_forecast.update_layout(
        hovermode="x unified",
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Revenue (BRL)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_forecast, width='stretch')
    
    st.info("💡 บริเวณแถบสีแดงจางๆ คือช่วงที่ยอดขายมีโอกาสเกิดขึ้นจริง (Margin of Error)")

with tabs[2]:
    st.subheader("Customer Behavior (Project 3)")
    fig_pie = px.pie(rfm_table, names='Segment', hole=0.4, category_orders={"Segment": priority_order})
    st.plotly_chart(fig_pie, width='stretch')

with tabs[3]:
    st.subheader("Lost Customers Action Plan")
    st.dataframe(rfm_table[rfm_table['Segment'].str.contains('Lost')].sort_values('Monetary', ascending=False))

st.markdown("---")
st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} | Analyst: Pitch")