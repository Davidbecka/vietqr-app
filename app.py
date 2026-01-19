import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="VietQR Pro Manager", layout="centered")

# Khởi tạo Lịch sử trong Session State (để không bị mất khi thao tác)
if 'history' not in st.session_state:
    st.session_state.history = []

BANK_MAP = {
    "VCB": "970436", "TCB": "970407", "MB": "970422", 
    "BIDV": "970418", "CTG": "970415", "ACB": "970416",
    "VPB": "970432", "TPB": "970423", "VIB": "970441",
    "STB": "970403", "HDB": "970437", "VBA": "970405",
}

st.title("🚀 VietQR Pro Manager")

excel_file = 'danh_sach_ck.xlsx'

if os.path.exists(excel_file):
    try:
        df = pd.read_excel(excel_file, dtype={'STK': str, 'MaBIN': str})
        df['Display'] = df['HoTen'] + " (" + df['STK'] + ")"
        
        # --- PHẦN NHẬP LIỆU ---
        with st.expander("➕ Tạo mã QR mới", expanded=True):
            selected_display = st.selectbox("Chọn người nhận:", df['Display'].tolist())
            receiver_info = df[df['Display'] == selected_display].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                madon = st.text_input("Mã đơn hàng", value="#XBQ6 #16.01 mã phiếu DO-107779-N03")
            with col2:
                amount = st.number_input("Số tiền (VNĐ)", min_value=0, value=int(receiver_info['SoTien']), step=1000, format="%d")
                st.caption(f"Số tiền: **{amount:,.0f} VNĐ**".replace(",", "."))

            # Nội dung chuyển khoản mặc định
            nd_ck = "Q6"
            
            # Nút Tạo QR
            if st.button("Tạo mã & Lưu lịch sử", type="primary", use_container_width=True):
                raw_bin = str(receiver_info['MaBIN']).upper()
                bin_code = BANK_MAP.get(raw_bin, raw_bin)
                stk = str(receiver_info['STK'])
                
                qr_url = f"https://img.vietqr.io/image/{bin_code}-{stk}-print.png?amount={int(amount)}&addInfo={nd_ck}"
                
                # Hiển thị kết quả
                st.image(qr_url, caption=f"QR đơn: {madon}", use_container_width=True)
                
                # Lưu vào lịch sử
                new_entry = {
                    "Thời gian": datetime.now().strftime("%H:%M:%S"),
                    "Mã đơn": madon,
                    "Số tiền": f"{amount:,.0f}".replace(",", "."),
                    "Người nhận": receiver_info['HoTen'],
                    "QR_URL": qr_url
                }
                st.session_state.history.insert(0, new_entry) # Đưa lên đầu danh sách

        # --- PHẦN COPY NHANH & TẢI VỀ ---
        if st.session_state.history:
            current = st.session_state.history[0]
            st.subheader("📋 Thao tác nhanh cho đơn vừa tạo")
            
            copy_text = f"Người nhận: {current['Người nhận']}\nSTK: {receiver_info['STK']}\nNgân hàng: {receiver_info['MaBIN']}\nSố tiền: {current['Số tiền']}đ\nNội dung: {nd_ck}"
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.copy_to_clipboard(copy_text)
                st.success("Bấm vào nút trên để Copy thông tin gửi khách!")
            with col_b:
                img_data = requests.get(current['QR_URL']).content
                st.download_button("📥 Tải ảnh QR", data=img_data, file_name=f"{current['Mã đơn']}.png", use_container_width=True)

        st.divider()

        # --- PHẦN LỊCH SỬ ---
        st.subheader("🕒 Lịch sử tạo QR (Trong phiên này)")
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history).drop(columns=['QR_URL'])
            st.table(history_df)
            if st.button("Xóa lịch sử"):
                st.session_state.history = []
                st.rerun()
        else:
            st.write("Chưa có mã nào được tạo.")

    except Exception as e:
        st.error(f"Lỗi: {e}")
else:
    st.error(f"Không tìm thấy file {excel_file}!")
