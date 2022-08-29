import argparse, time, pyautogui
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import snp

# global setting
GOOGLE_LOGIN_PAGE = "https://drive.google.com/drive/u/0/my-drive?hl=zh-TW"
FOLDER_ICON_PATH = "./images/folder_icon.png"
SHARED_DRIVE_ICON_PATH = "./images/shared_drive_icon.png"
DOWNLOAD_ICON_PATH = "./images/download_icon.png"

# class
class DownloadGdirveFiles(object):

    def __init__(self, email, password,
                 num_of_sharedDrive = 0,
                 manual_login = False,
                 default_manual_delay = -1,
                 ) -> None:
        pyautogui.FAILSAFE = False
        self.chrome_options = None
        self.driver = None
        self.email = email
        self.password = password
        self.num_of_sharedDrive = num_of_sharedDrive
        self.manual_login = manual_login
        self.default_manual_delay = default_manual_delay

    def __set_chrome_option(self, headless = False):
        """
        Chrome瀏覽器設定
        """
        chrome_options = webdriver.ChromeOptions() 
        # 無頭模式(不提供可視化介面)
        if headless:
            chrome_options.add_argument('--headless')
        # 不使用自動擴增外掛
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # 不要自動關閉視窗
        chrome_options.add_experimental_option("detach", True)
        # 不顯示"自動控制"的提示、避免"連結到系統的某個裝置失去作用(0x1F)"
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        # 最高權限執行
        chrome_options.add_argument('--no-sandbox')
        # Windows避免bug
        chrome_options.add_argument('--disable-gpu')
        # 禁止彈跳視窗、允許自動下載多個檔案
        prefs = { 'profile.default_content_setting_values' :{'notifications' : 2},
                  'profile.default_content_setting_values.automatic_downloads': 1,
                  'profile.password_manager_enabled': False, 
                  'credentials_enable_service': False } 
        chrome_options.add_experimental_option('prefs',prefs)
        # 設定屬性 chrome_options
        self.chrome_options = chrome_options

    def __open_website(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        driver.get(GOOGLE_LOGIN_PAGE)
        driver.maximize_window()
        # 設定屬性 driver
        self.driver = driver

    def __login(self):
        if (self.manual_login): # 手動登入
            # 等待使用者手動登入
            print("Please log in to your Gsuite account manually.")
            input("Press Enter to continue ...")
            # 給使用者時間回到 Chrome 視窗
            manual_delay = self.__get_manual_delay()
            print("Please go to the Chrome window in {} seconds.".format(manual_delay))
            time.sleep(manual_delay)
        else: # 自動登入
            input_email = self.driver.find_element('xpath','/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input')
            # 輸入Gsuite信箱 (個人Gmail因為低安全性所以不行)
            input_email.send_keys(self.email)
            input_email.send_keys('\n')
            time.sleep(1)
            # 輸入密碼
            input_password = self.driver.find_element('xpath', '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input')
            input_password.send_keys(self.password)
            input_password.send_keys('\n')
            time.sleep(5)

    def __de_identify(self):
        self.email = None
        self.password = None

    def __download_Drive(self):
        folder_icon_location = snp.locateOnScreen(FOLDER_ICON_PATH, threshold=0.99)
        # 在資料夾上點擊滑鼠右鍵
        if folder_icon_location != None:
            loc_x, loc_y, width, height = folder_icon_location
            pyautogui.hotkey('shift', 'a')
            time.sleep(2)
            pyautogui.rightClick(loc_x, loc_y)
            time.sleep(2)
            download_icon_location = snp.locateOnScreen(DOWNLOAD_ICON_PATH, threshold=0.99)
            # 點擊下載
            if download_icon_location != None:
                loc_x, loc_y, width, height = download_icon_location
                pyautogui.click(loc_x, loc_y)
                time.sleep(2)
            else:
                # 找不到圖標
                pyautogui.click(0, 0)
                print("download_icon not found")  
                time.sleep(2)              
        else:
            # 找不到圖標
            pyautogui.click(0, 0)
            print("folder_icon not found") 
            time.sleep(2)
    
    def __download_sharedDrive(self):
        shared_drive_icon_location = snp.locateOnScreen(SHARED_DRIVE_ICON_PATH, threshold=0.99)
        # 打開共用雲端硬碟列表
        if shared_drive_icon_location != None:
            loc_x, loc_y, width, height = shared_drive_icon_location
            for sd_ith in range(1, self.num_of_sharedDrive + 1):
                pyautogui.click(loc_x, loc_y, clicks=2)
                time.sleep(2)
                pyautogui.press('down', presses = sd_ith)
                time.sleep(2)
                pyautogui.press('enter')
                time.sleep(2)
                self.__download_Drive()
                time.sleep(2)
                pyautogui.click(loc_x, loc_y, clicks=2)
                time.sleep(2)
        else:
            # 找不到圖標就關閉網頁
            pyautogui.click(0, 0)
            pyautogui.hotkey('alt', 'f4')
            print("shared_drive_icon not found") 

    def __get_manual_delay(self) -> int:
        if self.default_manual_delay >= 0:
            return self.default_manual_delay
        else:
            print("How many times do you need to go to the Chrome window?")
            answer_raw = input('Delay in seconds (default to 10): ').strip()
            try:
                answer = int(answer_raw)
            except ValueError:
                answer = 10
            assert answer >= 0
            return answer

    def download_all(self):
        print("set chrome option...")
        self.__set_chrome_option()
        print("open website...")
        self.__open_website()
        print("login...")
        self.__login()
        print("We will NOT record your password.")
        self.__de_identify()
        print("start downloading my drive...")
        self.__download_Drive()
        print("finish")
        if self.num_of_sharedDrive >= 1:
            print("start downloading shared drive...")
            self.__download_sharedDrive()
            print("finish")
        print("You can close the website after all files are downloaded.")

if __name__ == '__main__':
    """
    使用指令: python download_gdrive.py --email myEmail --pwd myPassword --sdrive 0  
    注意: 雲端硬碟至少要有一個資料夾才能被下載
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', type=str, default='', required=False, help='Gsuite account email like jason022085.ie07g@nctu.edu.tw If omitted, the email will be acquired through an input prompt.')
    parser.add_argument('--pwd', type=str, default='', required=False, help='Gsuite account password. Do NOT worry, we will NOT steal your information. If omitted, the password will be acquired through an input prompt.')
    parser.add_argument('--sdrive', type=int, default=0, required=False, help='How many shared drives do you want to download ? If not, skip this argument.')
    parser.add_argument('--manual-login', action='store_true', help='Wait for the user to log in the Gsuite manually. This is useful should login interface got changed. See also --manual-delay')
    parser.add_argument('--manual-delay', type=int, default=-1, required=False, help='Seconds to wait after the user finishes the manual operations. If omitted, it will be acquired through an input prompt.')
    args = parser.parse_args()
    manual_login = args.manual_login
    email = args.email
    password = args.pwd
    if (not manual_login):
        # 若未使用 --email 跳出輸入列 `Email:` 以取得帳號
        # 去掉輸入值前後的空白字符以避免可能的錯誤
        # 若為空字串或空白，則丟出例外
        if not email:
            email = input("Email: ").strip()
            assert email
        # 若未使用 --pwd 跳出輸入列 `Password:` 以取得密碼
        # 若為空字串，則丟出例外
        if not password:
            password = getpass()
            assert password
    num_of_sharedDrive = args.sdrive
    DownloadGdirveFiles(email, password, num_of_sharedDrive,
                        manual_login=manual_login,
                        default_manual_delay=args.manual_delay,
                        ).download_all()


