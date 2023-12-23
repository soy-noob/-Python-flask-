from bs4 import BeautifulSoup
from flask import Flask,render_template,jsonify,request
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import json

app = Flask(__name__,static_folder="templates")

should_stop=False

isSpiderWorking=False

#设置headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 当前排行榜信息
leaderboardList=[]

# 当前封面信息
coverUrlList = []

# 已获取的封面链接
coverDB = {}

def WebDriverConfig():
    # 创建Chrome配置
    chrome_options = Options()
    # 添加配置
    chrome_options.add_argument(f"user-agent={headers['User-Agent']}")

    # 启用 headless 模式
    chrome_options.add_argument("--headless")
    return chrome_options

# 网址
url = 'https://www.bilibili.com/anime/index/'

# 初始化driver配置
chrome_options = WebDriverConfig()
# 初始化Chrome浏览器并传入选项
driver = webdriver.Chrome(options=chrome_options)

# 初始化封面driver
bgmUrl = "https://bangumi.tv/"
coverDriver = webdriver.Chrome(options=chrome_options)

# 打开排行榜网页
driver.get(url)

# 跳转评分
driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[1]/ul[1]/li[3]/span').click()

# 打开bgm等待获取封面url
coverDriver.get(bgmUrl)

# 获取排行榜信息
def GetLeaderBoardData(driver):
    # 获取页面源代码
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    list = soup.select("#app > div > .filter-body > ul > .bangumi-item")
    num = len(list)

    bgm_list = []

    for i in range(num):
        bgm_name = soup.find_all(class_="bangumi-title")[i].get_text()
        bgm_rate = soup.find_all(class_="shadow")[i].get_text()
        bgm_list.append({
            "name": bgm_name,
            "rate": bgm_rate
        })

    return bgm_list

# 更换排行榜
def ChangeLeaderBoard(region,state,season,year,style):
    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 选择地区
    regionChoices = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[3]/ul/li')
    regionIndex = 0
    for i in range(len(regionChoices)):
        if regionChoices[i].get_attribute("title") == region:
            regionIndex = i
            break
    re = driver.find_element(By.XPATH,'//*[@id="app"]/div[2]/div[2]/div[2]/div[3]/ul/li[' + str(regionIndex+1) + ']')
    driver.execute_script("arguments[0].scrollIntoView();", re)
    if(driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[3]/ul/li[' + str(regionIndex+1) + ']').get_attribute("class")!='filter-item on'):
        driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[3]/ul/li[' + str(regionIndex+1) + ']').click()

    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 选择状态
    stateChoices = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[4]/ul/li')
    stateIndex = 0
    for i in range(len(stateChoices)):
        if stateChoices[i].get_attribute("title") == state:
            stateIndex = i
            break
    st = driver.find_element(By.XPATH,'//*[@id="app"]/div[2]/div[2]/div[2]/div[4]/ul/li[' + str(stateIndex+1) + ']')
    driver.execute_script("arguments[0].scrollIntoView();", st)
    if (driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[4]/ul/li[' + str(stateIndex+1) + ']').get_attribute("class") != 'filter-item on'):
        driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[4]/ul/li[' + str(stateIndex+1) + ']').click()

    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 选择季度
    seasonChoices = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[7]/ul/li')
    seasonIndex = 0
    for i in range(len(seasonChoices)):
        if seasonChoices[i].get_attribute("title") == season:
            seasonIndex = i
            break
    se = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[7]/ul/li[' + str(seasonIndex + 1) + ']')
    driver.execute_script("arguments[0].scrollIntoView();", se)
    if (driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[7]/ul/li[' + str(
            seasonIndex + 1) + ']').get_attribute("class") != 'filter-item on'):
        driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[7]/ul/li[' + str(seasonIndex+1) + ']').click()

    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 选择年份
    yearChoices = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[8]/ul/li')
    yearIndex = 0
    for i in range(len(yearChoices)):
        if yearChoices[i].get_attribute("title") == year:
            yearIndex = i
            break
    ye = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[8]/ul/li[' + str(yearIndex + 1) + ']')
    driver.execute_script("arguments[0].scrollIntoView();", ye)
    if (driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[8]/ul/li[' + str(
            yearIndex + 1) + ']').get_attribute("class") != 'filter-item on'):
        driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[8]/ul/li[' + str(yearIndex+1) + ']').click()

    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 选择风格
    styleChoices = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[9]/ul/li')
    styleIndex = 0
    for i in range(len(styleChoices)):
        if styleChoices[i].get_attribute("title") == style:
            styleIndex = i
            break
    sty = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[9]/ul/li[' + str(styleIndex + 1) + ']')
    driver.execute_script("arguments[0].scrollIntoView();", sty)
    if (driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[9]/ul/li[' + str(
            styleIndex + 1) + ']').get_attribute("class") != 'filter-item on'):
        driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[9]/ul/li[' + str(styleIndex+1) + ']').click()

    # 页面重新定位
    driver.execute_script("window.scrollTo(0,0)")

    # 滑动页面，让封面全部加载出来
    for i in range(10):
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(0.01)

    return True

@app.route('/UpdateData',methods=['GET'])
def UpdateData():
    global should_stop,isSpiderWorking
    if(isSpiderWorking==True):
        should_stop=True
    else:
        should_stop=False

    filters = json.loads(request.args.get("filters"))

    region = filters['region']
    state = filters['state']
    season = filters['season']
    year = filters['year']
    style = filters['style']

    # 更新排行榜信息
    ChangeLeaderBoard(region,state,season,year,style)

    # 获取页面源代码
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    global leaderboardList

    # 获取排行榜数据
    leaderboardList = GetLeaderBoardData(driver)
    data = leaderboardList
    print(data)
    return jsonify(data)

def GetCoverUrl(coverDriver):
    global leaderboardList,isSpiderWorking
    isSpiderWorking=True
    print(leaderboardList)
    num = len(leaderboardList)

    url_list = []

    for i in range(num):
        bgm_url = GetCover(leaderboardList[i]['name'],coverDriver)
        url_list.append(bgm_url)
        global should_stop
        if(should_stop==True):
            isSpiderWorking=False
            should_stop=False
            break

    return url_list

# 获取番剧封面
def GetCover(name,coverDriver):
    errorUrl = "https://s11.ax1x.com/2023/12/22/pi7Csx0.png"
    coverUrl = ""
    coverDriver.find_element(By.XPATH,'//*[@id="search_text"]').send_keys(name)
    coverDriver.find_element(By.XPATH,'//*[@id="headerSearch"]/form/div/input[2]').click()
    # 等待页面加载完成
    coverDriver.implicitly_wait(0.01)  # 等待0.01秒
    if(name in coverDB):
        return coverDB.get(name)
    else:
        try:
            coverUrl = coverDriver.find_element(By.XPATH, '//*[@class="cover"][1]').get_attribute("src")
            print(f"{name}封面Url:{coverUrl}")
            coverDB[name]=coverUrl
            return coverUrl
        except NoSuchElementException as e:
            print("Error")
            print("未找到封面")
            coverDB[name]=errorUrl
            return errorUrl

@app.route('/UpdateCover',methods=['GET'])
def UpdateCover():
    # 获取封面链接
    coverUrlList = GetCoverUrl(coverDriver)
    data = coverUrlList
    return jsonify(data)

@app.route('/')
def index():
    return render_template("MainIndex.html")

if __name__ == '__main__':
    app.run(debug=False,port=5001)