# from selenium import webdriver

# option= webdriver.ChromeOptions()
# option.add_argument('--user-data-dir=C:\\Users\FF\AppData\Local\Google\Chrome\\User Data') #设置成用户自己的数据目录
# browser = webdriver.Chrome(chrome_options=option)

# browser.get('http://www.baidu.com/')

# browser.quit()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
 
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_driver = "D:\python37\chromedriver.exe"
driver = webdriver.Chrome(chrome_driver, chrome_options=chrome_options)

url = 'https://item.taobao.com/item.htm?spm=a1z0d.6639537.1997196601.4.4bb87484IB3252&id=618625357982'
driver.get(url)


while True :
    try:
        driver.find_element_by_xpath('//*[@id="J_LinkBuy"]').click()
        print('买')
        
    except:
        pass

    time.sleep(0.3)
    # 提交订单
    try:
        driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/div[1]/div/div[9]/div/div/a').click()
        break
    except:
        pass

    time.sleep(0.1)

print('over')

