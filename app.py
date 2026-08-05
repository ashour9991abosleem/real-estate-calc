import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة التمويل العقاري - أبو سليم", layout="wide", initial_sidebar_state="expanded")

# تصميم واجهة الويب مع اللون الأخضر الخاص بالبنك الأهلي وتعديل زر الشريط الجانبي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    /* تثبيت لون خلفية التطبيق بالأخضر الهادئ المستوحى من البنك الأهلي السعودي */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #F1F8F5 !important;
    }
    
    /* تنسيق زر فتح/إغلاق الشريط الجانبي (السهمين) وإضافة عبارة لوحة الإدخال بجانبه */
    [data-testid="collapsedControl"] {
        background-color: #006A4E !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        border: 2px solid #FFD700 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999;
    }
    
    [data-testid="collapsedControl"]::after {
        content: "لوحة الإدخال";
        font-family: 'Cairo', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #FFFFFF !important;
        white-space: nowrap;
    }
    
    [data-testid="collapsedControl"] svg {
        width: 20px !important;
        height: 20px !important;
        fill: #FFFFFF !important;
    }
    
    /* إخفاء القائمة الرئيسية الافتراضية والفوتر */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تصميم الحاويات والبطاقات الفاخرة */
    .custom-card {
        background-color: #ffffff;
        border: 1px solid #d1e7dd;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 106, 78, 0.05), 0 2px 4px -1px rgba(0, 106, 78, 0.03);
        margin-bottom: 20px;
    }
    
    /* تنسيق التابات الاحترافية */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #d1e7dd;
        padding: 6px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #004d38;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #006A4E !important;
        color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    @keyframes smoothAppear {
        0% { opacity: 0; transform: scale(0.96); }
        50% { opacity: 1; transform: scale(1); }
        80% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; display: none; }
    }
    
    .splash-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #006A4E 0%, #004d38 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        animation: smoothAppear 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        color: white;
        text-align: center;
        padding: 20px;
    }
    
    .splash-overlay h1 {
        font-size: 2.3rem;
        font-weight: 900;
        color: #FFD700;
        margin-bottom: 15px;
    }
    
    .splash-overlay h3 {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
    }
</style>

<div class="splash-overlay">
    <h1>حاسبة التمويل العقاري للبنك الأهلي</h1>
    <h3>سيد عاشور (ابو سليم)</h3>
</div>
""", unsafe_allow_html=True)

# الترويسة الرئيسية للنظام
st.markdown("<h2 style='text-align: center; color: #006A4E; font-weight: 900;'>نظام التطوير والتمويل العقاري المتقدم</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #52796f;'>إعداد الخبير المالي: أبو سليم</h4>", unsafe_allow_html=True)
st.markdown("---")

# دالة تحويل وتفسير التواريخ (هجري / ميلادي)
def parse_date_input(date_str):
    if not date_str:
        return 2000, 1, 1
    date_str = str(date_str).strip().replace("/", "-").replace(".", "-")
    parts = date_str.split("-")
    if len(parts) != 3:
        return 2000, 1, 1
    
    if len(parts[0].strip()) == 4:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        
    if str(y).startswith("14") or y < 1900:
        y = int(y * 0.97022 + 621.5643)
        
    return y, m, d

# دالة مطابقة لدالة LOOKUP في الاكسيل
def excel_lookup(val, keys, values):
    if val is None or val < keys[0]:
        return values[0]
    chosen_idx = 0
    for i, k in enumerate(keys):
        if val >= k:
            chosen_idx = i
        else:
            break
    return values[chosen_idx]

# الشريط الجانبي للإدخالات الأساسية
st.sidebar.markdown("### ⚙️ لوحة التحكم والإدخال")
st.sidebar.markdown("---")
st.sidebar.header("1. بيانات العميل والتواريخ")
birth_date_input = st.sidebar.text_input("تاريخ الميلاد (هجري أو ميلادي)", "1990-05-15")
hire_date_input = st.sidebar.text_input("تاريخ التعيين (هجري أو ميلادي)", "2015-01-01")

birth_year, birth_month, _ = parse_date_input(birth_date_input)
hire_year, hire_month, _ = parse_date_input(hire_date_input)

current_month = st.sidebar.number_input("الشهر الحالي (H27)", min_value=1, max_value=12, value=8)
current_year = st.sidebar.number_input("السنة الحالية (I27)", value=2026)
retirement_age = st.sidebar.number_input("العمر التقاعدي (J27)", value=60)

client_age = current_year - birth_year
birth_total_months = (birth_year * 12) + birth_month
retirement_total_months = birth_total_months + (retirement_age * 12)
current_total_months = (current_year * 12) + current_month
k17_remaining_service = max(0, retirement_total_months - current_total_months)

st.sidebar.info(f"⏳ المدة المتبقية على التقاعد: {k17_remaining_service} شهراً ({(k17_remaining_service/12):.1f} سنة)")

base_salary = st.sidebar.number_input("الراتب الأساسي (L27)", value=10000.0)
net_salary = st.sidebar.number_input("الراتب الصافي (D3)", value=15000.0)

job_status = st.sidebar.selectbox("جهة العمل (N27)", ["مدني", "عسكري", "عسكري اعتزاز", "متقاعد"])

st.sidebar.markdown("---")
st.sidebar.header("2. التزامات العميل")

col_btn1, col_btn2, col_btn3 = st.sidebar.columns(3)
calc_ratio_btn = col_btn1.button("قسط الشخصي")
buy_debt_btn = col_btn2.button("شراء المديونية")
no_debt_btn = col_btn3.button("بدون التزامات")

if "d7_val_state" not in st.session_state:
    st.session_state.d7_val_state = 0.0

if no_debt_btn:
    st.session_state.p_inst_input = 0.0
    st.session_state.p_rem_input = 0.0
    st.session_state.o_inst_input = 0.0
    st.session_state.d7_val_state = 0.0

if buy_debt_btn:
    if job_status in ["عسكري", "عسكري اعتزاز", "مدني"]:
        st.session_state.p_inst_input = net_salary * 0.3333
    elif job_status == "متقاعد":
        st.session_state.p_inst_input = net_salary * 0.25
    st.session_state.d7_val_state = 58.0

personal_installment = st.sidebar.number_input("قسط الشخصي (D5)", value=0.0, key="p_inst_input")
personal_remaining = st.sidebar.number_input("المبلغ المتبقي للتمويل الشخصي (E5)", value=0.0, key="p_rem_input")
other_installments = st.sidebar.number_input("الأقساط الأخرى (D6)", value=0.0, key="o_inst_input")

if calc_ratio_btn and personal_installment > 0:
    st.session_state.d7_val_state = personal_remaining / personal_installment
elif not calc_ratio_btn and not buy_debt_btn and not no_debt_btn:
    if personal_installment > 0:
        st.session_state.d7_val_state = personal_remaining / personal_installment
    else:
        st.session_state.d7_val_state = 0.0

d7_val = st.session_state.d7_val_state
st.sidebar.text(f"عدد الأقساط (D7): {d7_val:.1f}")

e14_p1_months = d7_val

st.sidebar.markdown("---")
st.sidebar.header("3. خيارات الاستقطاع والدعم")
support_type = st.sidebar.selectbox("نوع الدعم (K21)", ["مدعوم", "غير مدعوم"])
pkg_type = st.sidebar.selectbox("طريقة الباقة / الشهري (K19)", ["شهري", "باقة"])

suggested_e15 = max(0, k17_remaining_service - e14_p1_months)

st.sidebar.markdown("##### التحكم اليدوي لشهور الفترات")
e15_p2_months = st.sidebar.number_input(f"عدد شهور الفترة الثانية (E15) ({int(suggested_e15)})", value=float(suggested_e15))
e16_p3_months = st.sidebar.number_input("عدد شهور الفترة الثالثة (E16)", value=0.0)

st.sidebar.markdown("---")
st.sidebar.header("4. استقطاع مخصص")
m21_val = st.sidebar.number_input("استقطاع مخصص قبل التقاعد (M21)", value=0.0, format="%.2f")
m22_val = st.sidebar.number_input("استقطاع مخصص بعد التقاعد (M22)", value=0.0, format="%.2f")

service_years_calc = (current_year - hire_year) + ((current_month - 1) / 12)
if job_status in ["عسكري", "عسكري اعتزاز"]:
    q27 = (((12 / 12) + service_years_calc) * base_salary) / 35
elif job_status == "مدني":
    q27 = (((12 / 12) + service_years_calc) * base_salary) / 40
else:
    q27 = 0

k14_support = 955 if support_type == "مدعوم" else 0
d4_pension = q27 + k14_support

if job_status == "عسكري اعتزاز":
    p1_factor = 0.65 if pkg_type == "شهري" else 0.55
else:
    p1_factor = 0.55 if pkg_type == "باقة" else (0.65 if support_type == "مدعوم" else 0.55)

d14_p1_amount = (net_salary * p1_factor) - (personal_installment + other_installments) if e14_p1_months > 0 else 0.0

if m21_val == 0:
    if job_status == "عسكري اعتزاز":
        f2 = 0.65
    elif support_type == "مدعوم" and pkg_type == "شهري":
        f2 = 0.65
    elif support_type == "مدعوم" and pkg_type == "باقة":
        f2 = 0.55
    elif support_type == "غير مدعوم" and net_salary <= 15000:
        f2 = 0.55
    else:
        f2 = 0.65
    d15_p2_amount = (net_salary * f2) - other_installments
else:
    d15_p2_amount = (net_salary * m21_val) - other_installments

if job_status == "متقاعد":
    d16_p3_amount = 0.0
else:
    if m22_val == 0:
        if support_type == "مدعوم":
            f3 = 0.65
        elif support_type == "غير مدعوم" and net_salary <= 15000:
            f3 = 0.55
        else:
            f3 = 0.65
        d16_p3_amount = d4_pension * f3
    else:
        d16_p3_amount = d4_pension * m22_val

d8_total_months = e14_p1_months + e15_p2_months + e16_p3_months
e8_total_years = d8_total_months / 12

total_financing = (d14_p1_amount * e14_p1_months) + (d15_p2_amount * e15_p2_months) + (d16_p3_amount * e16_p3_months)

standard_keys = [1, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360]

if e8_total_years > 30:
    profit_margin_result = "قلل مدة التمويل"
elif client_age < 20:
    profit_margin_result = "العميل صغير"
elif job_status == "متقاعد" and client_age > 65:
    profit_margin_result = "عمر العميل عالي"
else:
    if job_status in ["مدني", "عسكري", "متقاعد"]:
        if support_type == "مدعوم":
            if pkg_type == "شهري":
                if e14_p1_months != 0:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [4.7,4.75,4.78,4.8,4.85,4.88,4.9,4.98,5.05,5.1,5.15,5.24,5.3,5.35,5.44,5.5,5.58,5.65,5.7,5.8,5.85,5.9,5.95,6.0,6.1,6.15,6.2])
                else:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [3.8,3.85,3.88,3.9,3.95,3.98,4.0,4.08,4.15,4.2,4.25,4.34,4.4,4.45,4.54,4.6,4.68,4.75,4.8,4.9,4.95,5.0,5.05,5.1,5.2,5.25,5.3])
            else:
                if e14_p1_months != 0:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [5.6,5.65,5.68,5.72,5.9,5.78,5.8,5.88,5.95,6.0,6.05,6.14,6.2,6.25,6.34,6.4,6.48,6.55,6.6,6.7,6.75,6.8,6.85,6.9,7.0,7.05,7.1])
                else:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [4.7,4.75,4.78,4.8,4.85,4.88,4.9,4.98,5.05,5.1,5.15,5.24,5.3,5.35,5.44,5.5,5.58,5.65,5.7,5.8,5.85,5.9,5.95,6.0,6.1,6.15,6.2])
        else:
            if e14_p1_months != 0:
                profit_margin_result = excel_lookup(d8_total_months, standard_keys, [5.2,5.25,5.28,5.3,5.35,5.38,5.4,5.48,5.55,5.6,5.65,5.74,5.8,5.85,5.94,6.0,6.08,6.15,6.2,6.3,6.35,6.4,6.45,6.5,6.6,6.65,6.7])
            else:
                profit_margin_result = excel_lookup(d8_total_months, standard_keys, [4.3,4.35,4.38,4.4,4.45,4.48,4.5,4.58,4.65,4.7,4.75,4.84,4.9,4.95,5.04,5.1,5.18,5.25,5.3,5.4,5.45,5.5,5.55,5.6,5.7,5.75,5.8])
    elif job_status == "عسكري اعتزاز":
        if support_type == "غير مدعوم":
            profit_margin_result = "غير مدعوم"
        else:
            if pkg_type == "شهري":
                if e14_p1_months != 0:
                    profit_margin_result = excel_lookup(d8_total_months, [1,72,192,264], [3.4,4.4,4.55,4.75])
                else:
                    profit_margin_result = excel_lookup(d8_total_months, [1,72,192,264,312], [2.5,3.5,3.65,3.75,3.85])
            else:
                if e14_p1_months != 0:
                    profit_margin_result = excel_lookup(d8_total_months, [1,72,192,264], [4.3,5.3,5.45,5.65])
                else:
                    profit_margin_result = excel_lookup(d8_total_months, [1,72,192,264,312], [3.4,4.4,4.55,4.65,4.75])
    else:
        profit_margin_result = 5.25

if isinstance(profit_margin_result, str):
    profit_margin = 0.0
    net_financing = 0.0
    display_margin = profit_margin_result
    st.sidebar.error(f"⚠️ تنبيه: {profit_margin_result}")
else:
    profit_margin = profit_margin_result
    profit_factor = (profit_margin * e8_total_years) + 100
    net_financing = (total_financing / profit_factor) * 100 if profit_factor > 0 else 0
    display_margin = f"{profit_margin}%"

st.sidebar.markdown("---")
st.sidebar.header("5. ملاحظات السداد")
note_1 = st.sidebar.text_input("ملاحظة السداد 1", "")
note_2 = st.sidebar.text_input("ملاحظة السداد 2", "")
note_3 = st.sidebar.text_input("ملاحظة السداد 3", "")

# --- ترتيب الأقسام داخل تابات تفاعلية (Tabs) أنيقة ---
tab1, tab2, tab3 = st.tabs([
    "📊 بيانات الحسبة", 
    "🧮 حاسبات صافي التعريف", 
    "💰 احتساب التمويل الشخصي"
])

with tab1:
    st.markdown("### 📊 بيانات الحسبة")
    
    client_name_input = st.text_input("اسم العميل", "محمد بن عبد الله", key="report_client_name")
    st.markdown(f"**العميل الكريم:** `{client_name_input}`")
    st.markdown("---")

    col_rep1, col_rep2 = st.columns(2)

    with col_rep1:
        st.markdown("##### 📌 ملاحظات السداد")
        if note_1: st.write(f"• {note_1}")
        if note_2: st.write(f"• {note_2}")
        if note_3: st.write(f"• {note_3}")
        if not note_1 and not note_2 and not note_3:
            st.info("لا توجد ملاحظات سداد مدخلة حالياً.")
        st.markdown(f"**جهة العمل:** {job_status}")
        st.markdown(f"**المدة المتبقية على التقاعد:** {k17_remaining_service} شهراً")

    with col_rep2:
        summary_data = {
            "البيان": ["مبلغ التمويل", "الدعم الشهري", "مدة التمويل", "هامش الربح (نسبة البنك)"],
            "القيمة": [f"{net_financing:,.0f} ر.س", f"{k14_support} ر.س", f"{e8_total_years:.1f} سنة", display_margin]
        }
        st.table(pd.DataFrame(summary_data))

    st.markdown("#### 📑 تفصيل الأقساط والفترات")
    periods_data = {
        "الفترة": ["الفترة الأولى", "الفترة الثانية", "الفترة الثالثة"],
        "عدد الشهور": [int(e14_p1_months), int(e15_p2_months), int(e16_p3_months)],
        "القسط العقاري (ر.س)": [f"{d14_p1_amount:,.0f}", f"{d15_p2_amount:,.0f}", f"{d16_p3_amount:,.0f}"]
    }
    st.table(pd.DataFrame(periods_data))

    col_bot1, col_bot2 = st.columns(2)
    col_bot1.metric("الدعم", support_type)
    col_bot2.metric("صافي راتب الاحتساب", f"{net_salary:,.0f} ر.س")

    # --- زر التصدير والإرسال عبر الواتساب ---
    st.markdown("---")
    
    notes_combined = ""
    if note_1: notes_combined += f"\n- {note_1}"
    if note_2: notes_combined += f"\n- {note_2}"
    if note_3: notes_combined += f"\n- {note_3}"

    whatsapp_message = f"""📊 *بيانات الحسبة العقارية*
--------------------------------
👤 *اسم العميل:* {client_name_input}
🏢 *جهة العمل:* {job_status}
⏳ *المدة المتبقية للتقاعد:* {k17_remaining_service} شهراً

💰 *تفاصيل التمويل:*
- مبلغ التمويل: {net_financing:,.0f} ر.س
- الدعم الشهري: {k14_support} ر.س
- مدة التمويل: {e8_total_years:.1f} سنة
- هامش الربح: {display_margin}

📑 *الأقساط والفترات:*
- الفترة الأولى ({int(e14_p1_months)} شهر): {d14_p1_amount:,.0f} ر.س
- الفترة الثانية ({int(e15_p2_months)} شهر): {d15_p2_amount:,.0f} ر.س
- الفترة الثالثة ({int(e16_p3_months)} شهر): {d16_p3_amount:,.0f} ر.س
{f"📌 *ملاحظات:* {notes_combined}" if notes_combined else ""}
--------------------------------
إعداد الخبير العقاري: أبو سليم 🏡"""

    encoded_message = urllib.parse.quote(whatsapp_message)
    whatsapp_url = f"https://wa.me/?text={encoded_message}"

    st.link_button("📲 إرسال التقرير عبر واتساب", url=whatsapp_url)

with tab2:
    st.markdown("### 🧮 حاسبات صافي التعريف وصافي التعريف (وزارة الدفاع)")
    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        st.markdown("##### صافي التعريف (العام)")
        def_base = st.number_input("الأساسي (صافي التعريف)", value=4000.0, key="def_base")
        def_allowances = st.number_input("البدلات", value=1400.0, key="def_allow")
        
        def_retirement = def_base * 0.09
        net_definition = (def_base - def_retirement) + def_allowances
        
        st.text(f"خصم التقاعد (9%): -{def_retirement:,.2f}")
        st.success(f"صافي التعريف النهائي: **{net_definition:,.2f} ر.س**")

    with calc_col2:
        st.markdown("##### صافي التعريف (وزارة الدفاع)")
        mod_base = st.number_input("الأساسي (وزارة الدفاع)", value=4000.0, key="mod_base")
        mod_total = st.number_input("الإجمالي (وزارة الدفاع)", value=10000.0, key="mod_total")
        
        mod_retirement_deduction = mod_base * 0.09
        net_mod_definition = mod_total - mod_retirement_deduction
        
        st.text(f"خصم التقاعد العسكري (9% من الأساسي): -{mod_retirement_deduction:,.2f}")
        st.success(f"الصافي النهائي للتعريف (وزارة الدفاع): **{net_mod_definition:,.2f} ر.س**")

with tab3:
    st.markdown("### 💰 احتساب التمويل الشخصي")
    p_col1, p_col2 = st.columns(2)

    with p_col1:
        pers_net_salary = st.number_input("الراتب الصافي", value=15000.0, key="pers_net_salary_input")
        pers_months = st.number_input("المدة بالأشهر", value=60, min_value=1, max_value=360, key="pers_months_input")
        
        if job_status in ["عسكري", "عسكري اعتزاز"]:
            pers_rate = excel_lookup(pers_net_salary, [0, 4000, 10000], [0, 3.99, 3.03])
        elif job_status in ["متقاعد", "مدني"]:
            pers_rate = excel_lookup(pers_net_salary, [0, 4000, 7000, 10000], [0, 3.99, 3.89, 3.03])
        else:
            pers_rate = 0.0
            
        st.info(f"🔒 نسبة الربح السنوية (تلقائية حسب الشيت): **{pers_rate}%**")

    with p_col2:
        pers_deduct_pct = 0.25 if job_status == "متقاعد" else 0.3333
        
        max_allowed_monthly = pers_net_salary * pers_deduct_pct
        pers_total_years = pers_months / 12
        
        pers_total_due = max_allowed_monthly * pers_months
        denominator = 1 + ((pers_rate / 100) * pers_total_years)
        pers_loan_amount = pers_total_due / denominator if denominator > 0 else 0

    st.markdown("---")
    res_pc1, res_pc2 = st.columns(2)
    res_pc1.metric("قسط الشخصي (الشهري)", f"{max_allowed_monthly:,.2f} ر.س")
    res_pc2.metric("صافي التمويل", f"{pers_loan_amount:,.2f} ر.س")
