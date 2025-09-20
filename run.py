# Nhập các thư viện cần thiết
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# --- PHẦN CẤU HÌNH ---

# 1. Từ điển lưu trữ từ khóa và link
# Bạn có thể dễ dàng thêm các cặp khác vào đây
URL_MAP = {
    "kubet": "https://judaism.us.com/"
    # "tu_khoa_khac": "https://link_khac.com/"
}

# 2. Cấu hình Profile Chrome
# THAY THẾ các thông tin dưới đây bằng đường dẫn và tên profile của bạn
# (Tìm bằng cách vào chrome://version)
USER_DATA_DIR = r"C:\Users\chung\AppData\Local\Google\Chrome\User Data" # Thay 'chung' nếu cần
PROFILE_DIRECTORY = "Profile 1" # Thay bằng "Default", "Profile 2"... của bạn


# --- BẮT ĐẦU CHƯƠNG TRÌNH ---

# Yêu cầu người dùng nhập từ khóa
keyword = input("Vui long nhap tu khoa: ").lower()

# Tìm link tương ứng với từ khóa
url_to_open = URL_MAP.get(keyword)

# Kiểm tra xem từ khóa có hợp lệ không
if not url_to_open:
    print(f"Loi: Tu khoa '{keyword}' khong duoc tim thay.")
    print("Chuong trinh se ket thuc.")
else:
    # Cấu hình để sử dụng Profile có sẵn
    print(f"Dang su dung Profile: {PROFILE_DIRECTORY}")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_DIRECTORY}")

    # Khởi tạo trình duyệt
    print("Dang khoi dong trinh duyet Chrome...")
    driver = webdriver.Chrome(options=chrome_options)

    # Đoạn mã JavaScript để tạo hiệu ứng cuộn mượt
    smooth_scroll_js = """
    const smoothScroll = (targetY, duration) => {
        let startY = window.pageYOffset;
        let distance = targetY - startY;
        let startTime = null;
        const animation = (currentTime) => {
            if (startTime === null) startTime = currentTime;
            let timeElapsed = currentTime - startTime;
            let run = Math.min(timeElapsed / duration, 1);
            run = 0.5 - Math.cos(run * Math.PI) / 2;
            window.scrollTo(0, startY + distance * run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        };
        requestAnimationFrame(animation);
    };
    """

    try:
        # Mở trang web
        print(f"Da tim thay tu khoa! Dang mo trang web: {url_to_open}")
        driver.get(url_to_open)
        driver.maximize_window()
        time.sleep(3)

        print("\nBat dau tu dong cuon trang...")
        print("Nhan Ctrl + C trong terminal de dung chuong trinh.")

        # Logic tự động cuộn trang
        while True:
            page_height = driver.execute_script("return document.body.scrollHeight")
            
            print("-> Cuon muot xuong cuoi trang...")
            driver.execute_script(smooth_scroll_js + f"smoothScroll({page_height}, 4000);")
            time.sleep(5) # Chờ 5 giây ở cuối trang

            print("-> Cuon muot ve dau trang...")
            driver.execute_script(smooth_scroll_js + "smoothScroll(0, 3000);")
            time.sleep(4) # Chờ 4 giây ở đầu trang

    except KeyboardInterrupt:
        print("\nDa nhan lenh dung chuong trinh.")
    except Exception as e:
        # In ra các lỗi khác nếu có
        print(f"Da xay ra mot loi khong mong muon: {e}")
    finally:
        # Luôn đóng trình duyệt sau khi hoàn tất
        print("Dang dong trinh duyet...")
        driver.quit()
        print("Chuong trinh da ket thuc.")