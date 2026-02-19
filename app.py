import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Olist Ultimate Dashboard", layout="wide")

# ลำดับความสำคัญของกลุ่มลูกค้า
priority_order = ['Champions (สุดยอดลูกค้า)', 'Loyal Customers (ขาประจำ)', 
                  'New Customers (ลูกค้าใหม่)', 'At Risk (เริ่มห่างเหิน)', 'Lost (ขาจรที่หายไป)']

# 2. ฟังก์ชันโหลดข้อมูล (Relative Path สำหรับ GitHub)
@st.cache_data
def load_all_data():
    return {
        'rfm': pd.read_csv('rfm_result.csv'),
        'forecast': pd.read_csv('sales_forecast.csv'),
        'monthly': pd.read_csv('monthly_sales.csv'),
        'cats': pd.read_csv('top_categories.csv'),
        'logistics': pd.read_csv('category_logistics.csv'),
        'states': pd.read_csv('state_sales.csv'),
        'payments': pd.read_csv('payment_methods.csv'),
        'hourly': pd.read_csv('hourly_orders.csv')
    }

try:
    data = load_all_data()
    rfm_table = data['rfm']
    rfm_table['Segment'] = pd.Categorical(rfm_table['Segment'], categories=priority_order, ordered=True)
except Exception as e:
    st.error(f"กรุณาตรวจสอบว่ามีไฟล์ข้อมูลครบถ้วนใน Repository: {e}")
    st.stop()

# 3. Sidebar
st.sidebar.title("🎯 Olist BI Control")
st.sidebar.info("Dashboard นี้รวม Insight จาก 3 โปรเจกต์หลัก")
selected_segments = st.sidebar.multiselect("Filter by RFM Segment:", priority_order, default=priority_order)

# 4. Main Dashboard Layout
st.title("🏆 Olist 360° Comprehensive Analytics")
tabs = st.tabs(["🏠 Sales Overview", "🚚 Logistics & Geo", "👥 Customer RFM", "🔮 Forecasting"])

# --- Tab 1: Sales Performance ---
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Historical Revenue Trend")
        fig_rev = px.line(data['monthly'], x='order_purchase_timestamp', y='price', template="plotly_white")
        fig_rev.update_traces(line_color='#2E86C1', fill='tozeroy')
        st.plotly_chart(fig_rev, use_container_width=True)
    with col2:
        st.subheader("Payment Methods")
        fig_pay = px.pie(data['payments'], values='payment_value', names='payment_type', hole=0.4)
        st.plotly_chart(fig_pay, use_container_width=True)

    st.subheader("Top 10 Selling Categories")
    st.bar_chart(data['cats'].set_index('product_category_name_english'))

# --- Tab 2: Logistics & Geography ---
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Average Delivery Delay")
        fig_log = px.bar(data['logistics'], x='delivery_time', y='product_category_name_english', 
                         orientation='h', color='delivery_time', color_continuous_scale='Reds')
        st.plotly_chart(fig_log, use_container_width=True)
    with c2:
        st.subheader("Hourly Ordering Pattern")
        st.line_chart(data['hourly'].set_index('order_hour'))

    st.subheader("Sales by State")
    st.bar_chart(data['states'].set_index('customer_state'))

# --- Tab 3: Customer RFM ---
with tabs[2]:
    st.subheader("RFM Customer Segmentation")
    f_rfm = rfm_table[rfm_table['Segment'].isin(selected_segments)]
    
    c3, c4 = st.columns([1, 2]) # c3 คือฝั่งกราฟ, c4 คือฝั่งตาราง
    
    with c3:
        # --- ก๊อปปี้ส่วนนี้ไปทับของเดิมใน c3 ได้เลยครับ ---
        fig_pie = px.pie(
            f_rfm, 
            names='Segment', 
            hole=0.4, 
            category_orders={"Segment": priority_order},
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )

        # สั่งจัดการตัวหนังสือที่มัน 'แปลก' ให้คลีนขึ้น
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent',    # โชว์แค่ % ในวงกลม
            insidetextorientation='horizontal'
        )

        fig_pie.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        # ---------------------------------------------

    with c4:
        # ตรงนี้ไม่ต้องแก้ครับ เป็นตารางสรุปเหมือนเดิม
        summary = f_rfm.groupby('Segment', observed=True).agg({
            'Monetary': 'mean', 
            'customer_unique_id': 'count'
        }).reset_index()
        st.dataframe(summary.style.format({'Monetary': '{:,.2f}'}), use_container_width=True)
      
# --- Tab 4: Forecasting ---
with tabs[3]:
    st.subheader("📈 Sales Forecast (Prophet Model)")
    f_data = data['forecast']
    f_data['ds'] = pd.to_datetime(f_data['ds'])
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(x=f_data['ds'], y=f_data['yhat_upper'], line=dict(width=0), showlegend=False))
    fig_f.add_trace(go.Scatter(x=f_data['ds'], y=f_data['yhat_lower'], fill='tonexty', fillcolor='rgba(255,0,0,0.1)', line=dict(width=0), showlegend=False))
    fig_f.add_trace(go.Scatter(x=f_data['ds'], y=f_data['yhat'], line=dict(color='#FF4B4B', width=3), name='Predicted'))
    st.plotly_chart(fig_f, use_container_width=True)

st.caption(f"Developed by Pitch | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}")


