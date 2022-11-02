# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.08,   yo.
# 2022.10.20 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: ログイン、信用建玉一覧取得、ログアウト を行ないます。
#
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    
    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_url = str_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, url_base, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     url_base, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------




# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p10/46 No.9 CLMShinyouTategyokuList を参照してください。
#
#   9 CLMShinyouTategyokuList
#  1	sCLMID	メッセージＩＤ	char*	I/O	'CLMShinyouTategyokuList'
#  2	sIssueCode	銘柄コード	char[12]	I/O	銘柄コード（6501 等）
#  3	sResultCode	結果コード	char[9]	O	業務処理．エラーコード 0：正常、5桁数字：「結果テキスト」に対応するエラーコード
#  4	sResultText	結果テキスト	char[512]	O	ShiftJis  「結果コード」に対応するテキスト
#  5	sWarningCode	警告コード	char[9]	O	業務処理．ワーニングコード 0：正常、5桁数字：「警告テキスト」に対応するワーニングコード
#  6	sWarningText	警告テキスト	char[512]	O	ShiftJis  「警告コード」に対応するテキスト
#  7	sUritateDaikin	売建代金合計	char[9]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.2。
#							0～9999999999999999、左詰め、マイナスの場合なし
#  8	sKaitateDaikin	買建代金合計	char[16]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.1。
#								0～9999999999999999、左詰め、マイナスの場合なし
#  9	sTotalDaikin	総代金合計	char[16]	O	照会機能仕様書 ２－２．（３）、（１）残高 No.3。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 10	sHyoukaSonekiGoukeiUridate	評価損益合計_売建	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.7。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 11	sHyoukaSonekiGoukeiKaidate	評価損益合計_買建	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.8。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 12	sTotalHyoukaSonekiGoukei	総評価損益合計	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.6。
#									-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 13	sTokuteiHyoukaSonekiGoukei	特定口座残高評価損益合計    char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.4。
#									        -999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 14	sIppanHyoukaSonekiGoukei	一般口座残高評価損益合計	char[16]    O	照会機能仕様書 ２－２．（３）、（１）残高 No.5。
#									        -999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 15	aShinyouTategyokuList	信用建玉リスト	char[17]	O	以下レコードを配列で設定
# 16-1	sOrderWarningCode	警告コード	char[9]	O	業務処理．ワーニングコード 
#										0：正常、
#										5桁数字：「警告テキスト」に対応するワーニングコード
# 17-2	sOrderWarningText	警告テキスト	char[512]	O	ShiftJis  「警告コード」に対応するテキスト
# 18-3	sOrderTategyokuNumber	建玉番号	char[15]	O	-
# 19-4	sOrderIssueCode	銘柄コード	char[12]	O	-
# 20-5	sOrderSizyouC	市場	char[2]	O	00：東証
# 21-6	sOrderBaibaiKubun	売買区分	char[1]	O	1：売
#   					3：買
#   					5：現渡
#   					7：現引
# 22-7	sOrderBensaiKubun	弁済区分	char[2]	O	00：なし
#   					26：制度信用6ヶ月
#   					29：制度信用無期限
#   					36：一般信用6ヶ月
#   					39：一般信用無期限
# 23-8	sOrderZyoutoekiKazeiC	譲渡益課税区分	char[1]	O	1：特定
#   					3：一般
#   					5：NISA
# 24-9	sOrderTategyokuSuryou	建株数	char[13]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.10。
#								0～9999999999999、左詰め、マイナスの場合なし
# 25-10	sOrderTategyokuTanka	建単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 26-11	sOrderHyoukaTanka	評価単価	char[14]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.13。
#								0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 27-12	sOrderGaisanHyoukaSoneki	評価損益	char[16]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.14。
#								-999999999999999～9999999999999999、左詰め、マイナスの場合あり
# 28-13	sOrderGaisanHyoukaSonekiRitu	評価損益率   char[13]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.22。
#								    -999999999.99～9999999999.99、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 29-14	sTategyokuDaikin	建玉代金	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.23。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 30-15	sOrderTateTesuryou	建手数料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.15。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 31-16	sOrderZyunHibu	順日歩	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.16。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 32-17	sOrderGyakuhibu	逆日歩	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.17。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 33-18	sOrderKakikaeryou	書換料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.18。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 34-19	sOrderKanrihi	管理費	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.19。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 35-20	sOrderKasikaburyou	貸株料	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.20。
#								0～9999999999999999、左詰め、マイナスの場合なし
# 36-21	sOrderSonota	その他	char[16]	O	照会機能仕様書 ２－２．（３）、（２）一覧 No.21。
#							0～9999999999999999、左詰め、マイナスの場合なし
# 37-22	sOrderTategyokuDay	建日	char[8]	O	YYYYMMDD,00000000
# 38-23	sOrderTategyokuKizituDay	建玉期日日	char[8]	O	YYYYMMDD、無期限の場合は 00000000
# 39-24	sTategyokuSuryou	建玉数量	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 40-25	sOrderYakuzyouHensaiKabusu	約定返済株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 41-26	sOrderGenbikiGenwatasiKabusu	現引現渡株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 42-27	sOrderOrderSuryou	注文中数量	char[13]    O	0～9999999999999、左詰め、マイナスの場合なし
# 43-28	sOrderHensaiKanouSuryou	返済可能数量	char[13]    O	照会機能仕様書 ２－２．（３）、（２）一覧 No.31。
#								0～9999999999999、左詰め、マイナスの場合なし
# 44-29	sSyuzituOwarine	前日終値	    char[14]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.24。
#						    0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 45-30	sZenzituHi	前日比	    char[14]    O   照会機能仕様書 ２－２．（３）、（２）一覧 No.25。
#						    -9999999.9999～99999999.9999、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 46-31	sZenzituHiPer	前日比()      char[7]	O   照会機能仕様書 ２－２．（３）、（２）一覧 No.26。
#						    -999.99～999.99、左詰め、マイナスの場合あり、小数点以下桁数切詰めなし
# 47-32	sUpDownFlag	騰落率Flag     char[2]	O   照会機能仕様書 ２－２．（３）、（２）一覧 No.27 11段階のFlag
#   					            01：+5.01  以上
#   					            02：+3.01  ～+5.00
#   					            03：+2.01  ～+3.00
#   					            04：+1.01  ～+2.00
#   					            05：+0.01  ～+1.00
#   					            06：0 変化なし
#   					            07：-0.01  ～-1.00
#   					            08：-1.01  ～-2.00
#   					            09：-2.01  ～-3.00
#   					            10：-3.01  ～-5.00
#   					            11：-5.01  以下




# --------------------------
# 機能: 信用建玉一覧取得
# 返値: API応答（辞書型）
# 引数1: p_no
# 引数2: 銘柄コード（6501等、'':省略時全銘柄取得）
# 引数3: class_cust_property（request通番）, 口座属性クラス
# 備考:
#       銘柄コードは省略可。
def func_get_shinyou_tategyoku_list(int_p_no,
                                str_sIssueCode,
                                class_cust_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # コマンド
    str_key = '"sCLMID"'
    str_value = 'CLMShinyouTategyokuList'  # 信用建玉一覧取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 銘柄コード
    str_key = '"sIssueCode"'
    str_value = str_sIssueCode      # 銘柄コード（6501等、'':省略時全銘柄取得）。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)

    return json_return





    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'
##my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'


# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える

# コマンド用パラメーター -------------------    
my_sIssueCode  = ''     # 銘柄コード  '':省略時全銘柄取得


# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)

# ログインOKの場合
if bool_login :
    
    
    print()
    print('-- 信用建玉一覧 取得 -------------------------------------------------------------')
    int_p_no = int_p_no + 1
    dic_return = func_get_shinyou_tategyoku_list(int_p_no,
                                                my_sIssueCode,
                                                class_cust_property)
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/46 No.9 CLMShinyouTategyokuList を参照してください

    print(' 1  メッセージＩＤ:\t', dic_return.get('sCLMID'))
    print(' 2  銘柄コード:\t', dic_return.get('sIssueCode'))
    print(' 3  結果コード:\t', dic_return.get('sResultCode'))
    print(' 4  結果テキスト:\t', dic_return.get('sResultText'))
    print(' 5  警告コード:\t', dic_return.get('sWarningCode'))
    print(' 6  警告テキスト:\t', dic_return.get('sWarningText'))
    print(' 7  売建代金合計:\t', dic_return.get('sUritateDaikin'))
    print(' 8  買建代金合計:\t', dic_return.get('sKaitateDaikin'))
    print(' 9  総代金合計:\t', dic_return.get('sTotalDaikin'))
    print('10  評価損益合計_売建:\t', dic_return.get('sHyoukaSonekiGoukeiUridate'))
    print('11  評価損益合計_買建:\t', dic_return.get('sHyoukaSonekiGoukeiKaidate'))
    print('12  総評価損益合計:\t', dic_return.get('sTotalHyoukaSonekiGoukei'))
    print('13  特定口座残高評価損益合計:\t', dic_return.get('sTokuteiHyoukaSonekiGoukei'))
    print('14  一般口座残高評価損益合計:\t', dic_return.get('sIppanHyoukaSonekiGoukei'))
    print()
    print()
    
    print('==========================')
    list_aShinyouTategyokuList = dic_return.get("aShinyouTategyokuList")
    print('15 信用建玉リスト:  aShinyouTategyokuList')
    print('件数:', len(list_aShinyouTategyokuList))
    print()
    # 'aShinyouTategyokuList'の返値の処理。
    # データ形式は、"aShinyouTategyokuList":[{...},{...}, ... ,{...}]
    for i in range(len(list_aShinyouTategyokuList)):
        print('No.', i+1, '---------------')
        print('16-1 警告コード:\t', list_aShinyouTategyokuList[i].get('sOrderWarningCode'))
        print('17-2 警告テキスト:\t', list_aShinyouTategyokuList[i].get('sOrderWarningText'))
        print('18-3 建玉番号:\t', list_aShinyouTategyokuList[i].get('sOrderTategyokuNumber'))
        print('19-4 銘柄コード:\t', list_aShinyouTategyokuList[i].get('sOrderIssueCode'))
        print('20-5 市場:\t', list_aShinyouTategyokuList[i].get('sOrderSizyouC'))
        print('21-6 売買区分:\t', list_aShinyouTategyokuList[i].get('sOrderBaibaiKubun'))
        print('22-7 弁済区分:\t', list_aShinyouTategyokuList[i].get('sOrderBensaiKubun'))
        print('23-8 譲渡益課税区分:\t', list_aShinyouTategyokuList[i].get('sOrderZyoutoekiKazeiC'))
        print('24-9 建株数:\t', list_aShinyouTategyokuList[i].get('sOrderTategyokuSuryou'))
        print('25-10 建単価:\t', list_aShinyouTategyokuList[i].get('sOrderTategyokuTanka'))
        print('26-11 評価単価:\t', list_aShinyouTategyokuList[i].get('sOrderHyoukaTanka'))
        print('27-12 評価損益:\t', list_aShinyouTategyokuList[i].get('sOrderGaisanHyoukaSoneki'))
        print('28-13 評価損益率:\t', list_aShinyouTategyokuList[i].get('sOrderGaisanHyoukaSonekiRitu'))
        print('29-14 建玉代金:\t', list_aShinyouTategyokuList[i].get('sTategyokuDaikin'))
        print('30-15 建手数料:\t', list_aShinyouTategyokuList[i].get('sOrderTateTesuryou'))
        print('31-16 順日歩:\t', list_aShinyouTategyokuList[i].get('sOrderZyunHibu'))
        print('32-17 逆日歩:\t', list_aShinyouTategyokuList[i].get('sOrderGyakuhibu'))
        print('33-18 書換料:\t', list_aShinyouTategyokuList[i].get('sOrderKakikaeryou'))
        print('34-19 管理費:\t', list_aShinyouTategyokuList[i].get('sOrderKanrihi'))
        print('35-20 貸株料:\t', list_aShinyouTategyokuList[i].get('sOrderKasikaburyou'))
        print('36-21 その他:\t', list_aShinyouTategyokuList[i].get('sOrderSonota'))
        print('37-22 建日:\t', list_aShinyouTategyokuList[i].get('sOrderTategyokuDay'))
        print('38-23 建玉期日日:\t', list_aShinyouTategyokuList[i].get('sOrderTategyokuKizituDay'))
        print('39-24 建玉数量:\t', list_aShinyouTategyokuList[i].get('sTategyokuSuryou'))
        print('40-25 約定返済株数:\t', list_aShinyouTategyokuList[i].get('sOrderYakuzyouHensaiKabusu'))
        print('41-26 現引現渡株数:\t', list_aShinyouTategyokuList[i].get('sOrderGenbikiGenwatasiKabusu'))
        print('42-27 注文中数量:\t', list_aShinyouTategyokuList[i].get('sOrderOrderSuryou'))
        print('43-28 返済可能数量:\t', list_aShinyouTategyokuList[i].get('sOrderHensaiKanouSuryou'))
        print('44-29 前日終値:\t', list_aShinyouTategyokuList[i].get('sSyuzituOwarine'))
        print('45-30 前日比:\t', list_aShinyouTategyokuList[i].get('sZenzituHi'))
        print('46-31 前日比():\t', list_aShinyouTategyokuList[i].get('sZenzituHiPer'))
        print('47-32 騰落率Flag:\t', list_aShinyouTategyokuList[i].get('sUpDownFlag'))
        print()
        print()
    
        
            
    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
