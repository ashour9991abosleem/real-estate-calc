import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="حاسبة التمويل العقاري والشخصي",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Animations and Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    /* Animation for Welcome Header */
    @keyframes fadeInDown {
        0% {
            opacity: 0;
            transform: translateY(-30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #002D62 0%, #0056b3 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        animation: fadeInDown 1.2s ease-out;
        margin-bottom: 25px;
    }
    
    .welcome-box h1 {
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 10px;
        color: #FFD700;
    }
    
    .welcome-box h3 {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f0f0f0;
        margin: 0;
    }
    
    /* Sidebar styling for smooth slide feel */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-left: 1px solid #e0e0e0;
        transition: transform 0.3s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Animated Header
st.markdown("""
<div class="welcome-box">
    <h1>حاسبة التمويل العقاري للبنك الأهلي</h1>
    <h3>إعداد الخبير المالي: سيد عاشور (أبو سليم)</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar instructions
st.sidebar.header("⚙️ إعدادات النظام")
st.sidebar.markdown("اسحب القائمة أو اضغط على زر القائمة (☰) في الجوال لإظهار أو إخفاء لوحة التحكم.")

# Tabs for different calculators
tab1, tab2, tab3 = st.tabs(["🏠 حاسبة التمويل العقاري", "🏗️ حاسبة البناء الذاتي", "💰 حاسبة التمويل الشخصي"])

with tab1:
    st.subheader("حاسبة التمويل العقاري")
    property_price = st.number_input("قيمة العقار (ريال/جنيه)", min_value=100000, value=1000000, step=50000, key="re_price")
    down_payment_pct = st.slider("نسبة الدفعة المقدمة (%)", min_value=10, max_value=50, value=15, key="re_dp")
    interest_rate = st.number_input("نسبة المرابحة السنوية (%)", min_value=1.0, max_value=10.0, value=4.5, step=0.1, key="re_rate")
    years = st.slider("مدة التمويل العقاري (سنوات)", min_value=5, max_value=30, value=20, key="re_years")
    
    dp_amount = property_price * (down_payment_pct / 100)
    loan_amount = property_price - dp_amount
    total_interest = loan_amount * (interest_rate / 100) * years
    total_payment = loan_amount + total_interest
    monthly_payment = total_payment / (years * 12)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("مبلغ التمويل", f"{loan_amount:,.2f}")
    col2.metric("القسط الشهري", f"{monthly_payment:,.2f}")
    col3.metric("إجمالي الأرباح", f"{total_interest:,.2f}")

with tab2:
    st.subheader("حاسبة البناء الذاتي (التطوير العقاري)")
    land_value = st.number_input("قيمة الأرض (ريال/جنيه)", min_value=0, value=500000, step=50000, key="sb_land")
    construction_cost = st.number_input("تكلفة البناء التقديرية", min_value=100000, value=600000, step=25000, key="sb_const")
    self_finance = st.number_input("المبلغ المتوفر ذاتياً", min_value=0, value=200000, step=25000, key="sb_self")
    
    total_project_cost = land_value + construction_cost
    required_finance = max(0, total_project_cost - self_finance)
    
    col1, col2 = st.columns(2)
    col1.metric("إجمالي تكلفة المشروع", f"{total_project_cost:,.2f}")
    col2.metric("التمويل المطلوب للبناء الذاتي", f"{required_finance:,.2f}")

with tab3:
    st.subheader("💰 حاسبة التمويل الشخصي")
    st.markdown("حساب الحد الأقصى لمبلغ التمويل الشخصي والقسط الشهري بناءً على دخلك والتزاماتك.")
    
    salary = st.number_input("الراتب الشهري (الأساسي + البدلات)", min_value=3000, value=12000, step=500, key="pers_salary")
    other_commitments = st.number_input("الالتزامات الشهرية الحالية (قروض/بطاقات)", min_value=0, value=1000, step=100, key="pers_commit")
    max_deduction_pct = st.slider("نسبة الاستقطاع القصوى (%)", min_value=30, max_value=65, value=55, key="pers_deduct")
    pers_years = st.slider("مدة التمويل الشخصي (سنوات)", min_value=1, max_value=5, value=5, key="pers_years")
    pers_rate = st.number_input("نسبة المرابحة السنوية للتمويل الشخصي (%)", min_value=2.0, max_value=10.0, value=4.0, step=0.1, key="pers_rate")
    
    max_allowed_monthly = salary * (max_deduction_pct / 100)
    net_available_monthly = max(0, max_allowed_monthly - other_commitments)
    total_months = pers_years * 12
    
    pers_loan_amount = (net_available_monthly * total_months) / (1 + (pers_rate / 100) * pers_years)
    pers_total_profit = pers_loan_amount * (pers_rate / 100) * pers_years
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("القسط الشهري المتاح", f"{net_available_monthly:,.2f}")
    col2.metric("إجمالي مبلغ التمويل الشخصي", f"{pers_loan_amount:,.2f}")
    col3.metric("إجمالي الأرباح", f"{pers_total_profit:,.2f}")
