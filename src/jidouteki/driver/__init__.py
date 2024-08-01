from selenium import webdriver

WebDriver = webdriver.Chrome | webdriver.Firefox

class _DriverManagerClass():
    def __init__(self, browser = "chrome", headless=True) -> None:
        self.driver = None
        
        if browser == "chrome":
            from selenium.webdriver.chromium.service import ChromiumService as Service
            from webdriver_manager.chrome import ChromeDriverManager as Manager
            from selenium.webdriver.chromium.options import ChromiumOptions as Options 
            from selenium.webdriver import Chrome as WebDriver
        elif browser == "firefox":
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import DriverManager as Manager
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver import Firefox as WebDriver
        else:
            raise ValueError("Unexpected browser value")
        
        options = Options()
        options.add_argument("--no-sandbox")
        if headless: options.add_argument("--headless=new")
        self.driver =  WebDriver(service=Service(Manager().install()), options=options)
    
    def __del__(self):
        if self.driver:
            self.driver.quit()

    def get(self):
        return self.driver

DriverManager = None # _DriverManagerClass()