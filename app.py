import streamlit as st
import pandas as pd
import requests
import os

# Cấu hình giao diện
st.set_page_config(page_title="VietQR Manager", layout="centered")

# Từ điển mã BIN
BANK_MAP = {
    "VCB": "970436", "TCB": "970407", "MB": "970422", 
    "BIDV": "970418", "CTG": "970415", "ACB": "970416",
    "VPB": "970432", "TPB": "970423", "VIB": "970441",
    "STB": "970403", "HDB": "970437", "VBA": "970405",
}

st.title("📲 VietQR Web Manager")

excel_file = 'danh_sach_ck.xlsx'

if os.path.exists(excel_file):
    try:
        # Đọc dữ liệu từ Excel
        df = pd.read_excel(excel_file, dtype={'STK': str, 'MaBIN': str})
        df['Display'] = df['HoTen'] + " (" + df['STK'] + ")"
        
        # 1. CHỌN NGƯỜI NHẬN
        selected_display = st.selectbox("Chọn người nhận từ danh sách:", df['Display'].tolist())
        receiver_info = df[df['Display'] == selected_display].iloc[0]
        
        st.divider()

        # 2. TINH CHỈNH THÔNG TIN
        col1, col2 = st.columns(2)
        with col1:
            madon = st.text_input("Mã đơn hàng", value="#XBQ6 #16.01 mã phiếu DO-107779-N03")
        
        with col2:
            # Nhập số tiền - hiển thị đẹp
            amount = st.number_input(
                "Số tiền thanh toán (VNĐ)", 
                min_value=0, 
                value=int(receiver_info['SoTien']), 
                step=1000,
                format="%d"
            )
            st.caption(f"Xác nhận: **{amount:,.0f} VNĐ**".replace(",", "."))

        # Nội dung cố định
        st.text_input("Nội dung chuyển khoản", value="Q6", disabled=True)

        if st.button("Tạo mã QR", type="primary"):
            # Xử lý mã BIN và link
            raw_bin = str(receiver_info['MaBIN']).upper()
            bin_code = BANK_MAP.get(raw_bin, raw_bin)
            stk = str(receiver_info['STK'])
            content_fixed = requests.utils.quote("Q6")
            
            # Link API chuẩn - Dòng 61 quan trọng
            qr_url = f"https://img.vietqr.io/image/{bin_code}-{stk}-print.png?amount={int(amount)}&addInfo={content_fixed}"
            
            # Hiển thị
            st.image(qr_url, caption=f"QR đơn: {madon}", use_container_width=True)
            
            # Nút tải ảnh
            img_data = requests.get(qr_url).content
            filename = f"{madon.replace(' ', '_')}_{amount}d.png"
            st.download_button("📥 Tải ảnh QR", data=img_data, file_name=filename, mime="image/png")

    except Exception as e:
        st.error(f"Lỗi dữ liệu: {e}")
else:
    st.error(f"Không tìm thấy file {excel_file} trong thư mục!")
