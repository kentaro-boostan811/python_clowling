import time
import csv
import sys
import re
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# int args[1] : クローリング方法について
#   1 : 新着のみ取得 ケツから調べて、同一データが発見するまで
#   2 : 全件クローリング　重複してても取ってくる
# int args[2] : 開始ページ指定 （全件クローリングのみ使用）
#   int n : クローリングを開始するページ
#   None : 1ページ目から

# コマンドライン引数で指定されたページからクローリングをスタートさせる
# 引数がない場合、第一引数が数値でない場合は、最初のページからクローリング
args = sys.argv
if len(args) == 1:
    StartPage = 1
else:
    StartPage = args[1]

# 会社名
CompanyName = ''

fp_out = open('list.csv', 'a')

Driver = webdriver.Chrome()
# 国土交通省 建設業者・宅建業者検索システムを開く
Driver.get('https://etsuran.mlit.go.jp/TAKKEN/')

time.sleep(3)

# 宅地建物取引業者検索に移動
ClickPoint = Driver.find_element_by_xpath('//*[@id="top_btn"]/div[2]/div[1]/a/img')
ClickPoint.click()

time.sleep(3)

# 本店のみ検索
Dropdown = Driver.find_element_by_id("choice")
DropdownSelect = Select(Dropdown)
DropdownSelect.select_by_value("1")

# 表示件数を50件に変更
Dropdown = Driver.find_element_by_id("dispCount")
DropdownSelect = Select(Dropdown)
DropdownSelect.select_by_value("50")

# 都道府県選択
# 今後ループ処理で全県取得するかもしれない。
Dropdown = Driver.find_element_by_id("kenCode")
DropdownSelect = Select(Dropdown)
DropdownSelect.select_by_value("13")

 # 検索開始する
ClickPoint = Driver.find_element_by_xpath('//*[@id="input"]/div[6]/div[5]/img')
ClickPoint.click()

time.sleep(2)

# 検索結果 / 1ページの表示数でクローリングするページ数を取得
MaxPages = Driver.find_element_by_xpath('//*[@id="container_cont"]/div[6]/p').text
MaxPages = MaxPages.split("\n")
MaxPage = int(int(re.sub("\\D", "", MaxPages[0])) / 50) + 1
print(MaxPage)

#ユーザ指定のページから始める
Dropdown = Driver.find_element_by_id("pageListNo1")
DropdownSelect = Select(Dropdown)
DropdownSelect.select_by_value(str(StartPage))
StartPage = int(StartPage) + 1

# 検索結果を1ページずつ移動する
for PageCnt in range(StartPage, MaxPage+2):
    print(PageCnt)
    cnt = 0
    # 検索結果の詳細ページを開いていく
    for cnt in range(50):
        # +=3 なのは一番上のデータが
        # //*[@id="container_cont"]/table/tbody/tr[3]/td[4]/a
        # からスタートなため
        cnt += 3
        FindXPath = '//*[@id="container_cont"]/table/tbody/tr[' + str(cnt) + ']/td[4]/a'

        ClickPoint = Driver.find_element_by_xpath(FindXPath)
        ClickPoint.click()

        time.sleep(1.5)

        CompanyName = Driver.find_element_by_xpath('//*[@id="input"]/table/tbody/tr[1]/td').text
        CompanyName = CompanyName.split("\n")

        # 事務所タブに移動
        ClickPoint = Driver.find_element_by_xpath('//*[@id="tab_builing"]/ul/li[2]/a/img')
        ClickPoint.click()

        #row = Driver.find_element_by_xpath('//*[@id="input"]/div/table').find_element(By.TAG_NAME('tr')).size()
        Tables = Driver.find_element_by_xpath('//*[@id="input"]/div/table/tbody')
        Trs = Tables.find_elements(By.TAG_NAME, 'tr')
        # print(len(Trs))

        # 店舗のテーブルから情報を取得
        for i in range(len(Trs)):
            Tds = Trs[i].find_elements(By.TAG_NAME, "td")
            line = ""
            for j in range(0,len(Tds)):
                    if j < len(Tds)-1:
                        line += "%s," % (Tds[j].text)
                        # データが取得できなかった場合は、テーブルからのデータ取得を
                        if j == 0:
                            if Tds[j].text == "":
                                break
                    else:
                        line += "%s" % (Tds[j].text)

            # データがない場合
            if len(line) != 1:
                line = CompanyName[0] + "," + CompanyName[1] + "," + line.replace("\n", ",") + "\n"
                fp_out.write(line)

        Driver.back()
        Driver.back()
        #print("after back")

        time.sleep(1.5)
        #print("inner loop end")
    time.sleep(1.5)

    #ページ遷移
    Dropdown = Driver.find_element_by_id("pageListNo1")
    DropdownSelect = Select(Dropdown)
    DropdownSelect.select_by_value(str(PageCnt))
    print("outer loop end")

Driver.close()
fp_out.close()
