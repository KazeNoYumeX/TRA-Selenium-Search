from selenium import webdriver
from pyquery import PyQuery as pq
from tabulate import tabulate
import time

# 來源網址
url = 'https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime'

# 選單內容
url_map = {
    1: {"name": "火車時刻查詢"},
}


# 顯示主選單
def print_menu():
    print("========== 20221128 ============")
    for k, v in url_map.items():
        print("%s. %s" % (k, v.get('name')))
    print("0. 離開")
    print("======================")


# 顯示次要選單
def print_list(key, data):
    print("========== %s ============" % key)
    for k, v in data.items():
        print("%s. %s" % (k, v.get('name')))
    print("======================")


# 主選單判斷
def method():
    """
    Get action nuber
    Return ...ummm {url,method,...}
    """
    action = int(input("請選擇要進行的操作 [0-1] : "))

    # 0 is always exit
    if action == 0:
        exit()
    elif url_map.get(action) is None:
        return

    return action


def train_search():
    driver = webdriver.Chrome()
    driver.get(url)

    html = driver.find_element('css selector', '*').get_attribute('outerHTML')
    doc = pq(html)

    # 縣市、站名
    cites = {}
    stations = {}

    # 結果班次
    ret_trans = []

    # 蒐集縣市資訊
    city_count = 2
    for station in doc('#mainline > div:nth-child(1) > ul > li:nth-child(n+2)').items():
        name = station.text()
        city_id = doc('#mainline > div:nth-child(1) > ul > li:nth-child(' + str(city_count) + ') > button').attr(
            'data-type')
        cites[len(cites) + 1] = {'id': city_id, 'name': name, 'count': city_count}
        city_count += 1

    # 顯示出發縣市列表
    print_list('出發縣市', cites)

    # 選擇出發縣市
    input_start_city = input('請輸入出發縣市 [1-%s]: ' % str(len(cites) - 1))
    input_start_city = cites[int(input_start_city)]
    time.sleep(3)

    # 點擊出發站按鈕
    driver.find_element('xpath', "//*[@id='queryForm']/div/div[1]/div[2]/div[2]/button[1]").click()
    time.sleep(1)

    # 點選縣市
    driver.find_element('xpath',
                        "//*[@id='mainline']/div[1]/ul/li[{0}]/button".format(
                            input_start_city['count'])).click()

    # 蒐集出發站資訊
    station_start_count = 1
    for station in doc('#{0} > ul > li:nth-child(n+1) > button'.format(input_start_city['id'])).items():
        name = station.text()
        stations[len(stations) + 1] = {'name': name, 'count': station_start_count}
        station_start_count += 1

    # 顯示出發站列表
    print_list('出發站', stations)

    # 點選出出發站
    input_start_station = input('請輸入出發站 [1-%s]: ' % str(len(stations) - 1))
    input_start_station = stations[int(input_start_station)]
    time.sleep(1)

    driver.find_element('xpath',
                        "//*[@id='{0}']/ul/li[{1}]/button".format(input_start_city['id'],
                                                                  input_start_station['count'])).click()

    # 顯示抵達縣市列表
    print_list('抵達縣市', cites)

    # 點選抵達縣市
    input_end_city = input('請輸入抵達縣市 [1-%s]: ' % str(len(cites) - 1))
    input_end_city = cites[int(input_end_city)]
    time.sleep(3)

    driver.find_element('xpath', "//*[@id='queryForm']/div/div[1]/div[4]/div[2]/button[1]").click()
    time.sleep(1)

    # 點開抵達站按鈕
    driver.find_element('xpath',
                        "//*[@id='mainline']/div[1]/ul/li[{0}]/button".format(
                            input_end_city['count'])).click()

    # 蒐集抵達站資訊
    stations = {}
    station_end_count = 1
    for station in doc('#{0} > ul > li:nth-child(n+1) > button'.format(input_end_city['id'])).items():
        name = station.text()
        stations[len(stations) + 1] = {'name': name, 'count': station_end_count}
        station_end_count += 1

    # 顯示抵達站列表
    print_list('抵達站', stations)

    # 點選抵達縣市
    input_end_station = input('請輸入抵達站 [1-%s]: ' % str(len(stations) - 1))
    input_end_station = stations[int(input_end_station)]
    time.sleep(1)

    driver.find_element('xpath',
                        "//*[@id='{0}']/ul/li[{1}]/button".format(input_start_city['id'],
                                                                  input_end_station['count'])).click()

    # 選擇時間
    input_date = input('請輸入日期 [年/月/日] :  ')
    driver.execute_script("document.getElementById('rideDate').value='{0}'".format(input_date))
    input_start_time = input('請輸入出發時間(起) [時:分] :  ')
    driver.execute_script("document.getElementById('startTime').value='{0}'".format(input_start_time))
    input_end_time = input('請輸入出發時間(迄) [時:分] :  ')
    driver.execute_script("document.getElementById('endTime').value='{0}'".format(input_end_time))

    # 送出表單
    ori_url = driver.current_url
    driver.find_element('xpath', "//*[@id='queryForm']/div/div[3]/div[2]/input").click()
    time.sleep(1)

    retry = 30
    msg = ''

    while ori_url == driver.current_url and retry > 0:
        retry -= 1
        if doc('#errorDiv').attr('style') != 'display: none':
            msg = doc('#errorDiv .mag-error').text()
            break
        time.sleep(1)

    if doc('#errorDiv').attr('style') == 'display: none' and msg == '':
        ret_html = driver.find_element('css selector', '*').get_attribute('outerHTML')
        ret_doc = pq(ret_html)

        alter_msg = ret_doc('#content > div.alert.alert-warning').text()

        if alter_msg != '':
            print(alter_msg)
        else:
            ret_doc('#pageContent > div > table > tbody > tr.trip-column')

            for train in ret_doc('#pageContent > div > table > tbody > tr.trip-column').items():
                train_num = train.find('ul.train-number a').text()
                departure = train.children('td').eq(1).text()
                arrival = train.children('td').eq(2).text()
                ret_trans.append({'車次': train_num, '出發時間': departure, '抵達時間': arrival})

            # 顯示結果表單
            print(tabulate(ret_trans, headers='keys', tablefmt='grid'))

    else:
        print(msg)

    # 關閉瀏覽器
    driver.quit()

    # 搜尋完後是否進行二次搜尋
    action = input("是否要重新搜尋 [y/n] : ")

    # 0 is always exit
    if action == 1 or 'Y' or 'y':
        train_search()
    elif action == 0 or 'N' or 'n':
        start()
    else:
        print("無效的選項，返回選單")
        start()


def start():
    while True:
        print_menu()

        option = method()
        if option is None:
            print("無效的選項，請重新選擇")
            continue

        if option == 1:
            train_search()


if __name__ == '__main__':
    start()
