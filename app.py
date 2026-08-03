import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة التمويل العقاري - أبو سليم", layout="wide")

st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>نظام التطوير والتمويل العقاري المتقدم</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #6B7280;'>إعداد: أبو سليم</h4>", unsafe_allow_html=True)
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
st.sidebar.header("1. بيانات العميل والتواريخ")
birth_date_input = st.sidebar.text_input("تاريخ الميلاد (هجري أو ميلادي)", "1990-05-15")
hire_date_input = st.sidebar.text_input("تاريخ التعيين (هجري أو ميلادي)", "2015-01-01")

birth_year, birth_month, _ = parse_date_input(birth_date_input)
hire_year, hire_month, _ = parse_date_input(hire_date_input)

current_month = st.sidebar.number_input("الشهر الحالي (H27)", min_value=1, max_value=12, value=8)
current_year = st.sidebar.number_input("السنة الحالية (I27)", value=2026)
retirement_age = st.sidebar.number_input("العمر التقاعدي (J27)", value=60)

# حساب العمر والمدة المتبقية على التقاعد
client_age = current_year - birth_year
birth_total_months = (birth_year * 12) + birth_month
retirement_total_months = birth_total_months + (retirement_age * 12)
current_total_months = (current_year * 12) + current_month
k17_remaining_service = max(0, retirement_total_months - current_total_months)

st.sidebar.success(f"⏳ المدة المتبقية على التقاعد: {k17_remaining_service} شهراً ({(k17_remaining_service/12):.1f} سنة)")

base_salary = st.sidebar.number_input("الراتب الأساسي (L27)", value=10000.0)
net_salary = st.sidebar.number_input("الراتب الصافي (D3)", value=15000.0)

job_status = st.sidebar.selectbox("جهة العمل (N27)", ["مدني", "عسكري", "عسكري اعتزاز", "متقاعد"])

st.sidebar.markdown("---")
st.sidebar.header("2. التزامات العميل")

# الأزرار في البداية لمعالجة الحالة قبل إنشاء الـ widgets وتجنب خطأ Streamlit
col_btn1, col_btn2, col_btn3 = st.sidebar.columns(3)
calc_ratio_btn = col_btn1.button("حساب النسبة")
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

# حقول الالتزامات مع مفاتيح الحالة
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

# --- الفترة الأولى ---
e14_p1_months = d7_val

st.sidebar.markdown("---")
st.sidebar.header("3. خيارات الاستقطاع والدعم")
support_type = st.sidebar.selectbox("نوع الدعم (K21)", ["مدعوم", "غير مدعوم"])
pkg_type = st.sidebar.selectbox("طريقة الباقة / الشهري (K19)", ["شهري", "باقة"])

suggested_e15 = max(0, k17_remaining_service - e14_p1_months)

st.sidebar.markdown("##### التحكم اليدوي لشهور الفترات")
e15_p2_months = st.sidebar.number_input(f"عدد شهور الفترة الثانية (E15) ({int(suggested_e15)})", value=float(suggested_e15))
e16_p3_months = st.sidebar.number_input("عدد شهور الفترة الثالثة (E16)", value=0.0)

# استقطاع مخصص
st.sidebar.markdown("---")
st.sidebar.header("4. استقطاع مخصص")
m21_val = st.sidebar.number_input("استقطاع مخصص قبل التقاعد (M21)", value=0.0, format="%.2f")
m22_val = st.sidebar.number_input("استقطاع مخصص بعد التقاعد (M22)", value=0.0, format="%.2f")

# --- حسابات المدد والتقاعد والراتب التقاعدي ---
service_years_calc = (current_year - hire_year) + ((current_month - 1) / 12)
if job_status in ["عسكري", "عسكري اعتزاز"]:
    q27 = (((12 / 12) + service_years_calc) * base_salary) / 35
elif job_status == "مدني":
    q27 = (((12 / 12) + service_years_calc) * base_salary) / 40
else:
    q27 = 0

k14_support = 955 if support_type == "مدعوم" else 0
d4_pension = q27 + k14_support

# نسب الفترة الأولى
if job_status == "عسكري اعتزاز":
    p1_factor = 0.65 if pkg_type == "شهري" else 0.55
else:
    p1_factor = 0.55 if pkg_type == "باقة" else (0.65 if support_type == "مدعوم" else 0.55)

d14_p1_amount = (net_salary * p1_factor) - (personal_installment + other_installments) if e14_p1_months > 0 else 0.0

# معادلات الأقساط لفترة 2 و 3
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

# الإجماليات والمدة الكلية
d8_total_months = e14_p1_months + e15_p2_months + e16_p3_months
e8_total_years = d8_total_months / 12

total_financing = (d14_p1_amount * e14_p1_months) + (d15_p2_amount * e15_p2_months) + (d16_p3_amount * e16_p3_months)

# ==========================================
# معادلة نسبة البنك المطابقة لشيت الاكسيل
# ==========================================
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
            else: # باقة
                if e14_p1_months != 0:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [5.6,5.65,5.68,5.72,5.9,5.78,5.8,5.88,5.95,6.0,6.05,6.14,6.2,6.25,6.34,6.4,6.48,6.55,6.6,6.7,6.75,6.8,6.85,6.9,7.0,7.05,7.1])
                else:
                    profit_margin_result = excel_lookup(d8_total_months, standard_keys, [4.7,4.75,4.78,4.8,4.85,4.88,4.9,4.98,5.05,5.1,5.15,5.24,5.3,5.35,5.44,5.5,5.58,5.65,5.7,5.8,5.85,5.9,5.95,6.0,6.1,6.15,6.2])
        else: # غير مدعوم
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
            else: # باقة
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

# --- ملاحظات السداد ---
st.sidebar.markdown("---")
st.sidebar.header("5. ملاحظات السداد")
note_1 = st.sidebar.text_input("ملاحظة السداد 1", "")
note_2 = st.sidebar.text_input("ملاحظة السداد 2", "")
note_3 = st.sidebar.text_input("ملاحظة السداد 3", "")

# --- تقرير تصوير الحسبة النهائي ---
st.markdown("### 📊 تقرير تصوير الحسبة للعميل")

col_rep1, col_rep2 = st.columns(2)

with col_rep1:
    st.markdown("##### 📌 ملاحظات السداد")
    if note_1: st.write(f"• {note_1}")
    if note_2: st.write(f"• {note_2}")
    if note_3: st.write(f"• {note_3}")
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

# --- الحاسبتان المطابقتان لشيت الاكسيل (صافي التعريف وصافي التعريف - وزارة الدفاع) ---
st.markdown("---")
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
    
    # حساب خصم التقاعد العسكري 9% من الأساسي والوصول للصافي النهائي للتعريف
    mod_retirement_deduction = mod_base * 0.09
    net_mod_definition = mod_total - mod_retirement_deduction
    
    st.text(f"خصم التقاعد العسكري (9% من الأساسي): -{mod_retirement_deduction:,.2f}")
    st.success(f"الصافي النهائي للتعريف (وزارة الدفاع): **{net_mod_definition:,.2f} ر.س**")