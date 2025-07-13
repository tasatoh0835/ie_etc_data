import csv
import sub.Const

#--------------------------------------------------------------------------
# csvデータ取得
# 引数    file_path : 読込対象ファイルパス
# 戻り値  retlist   : 読込対象ファイルを行単位でリスト化したデータ
#--------------------------------------------------------------------------
def getFileDataList(file_path):
    retlist = list()
    with open(file_path) as f:
        reader = csv.reader(f)
        retlist = [row for row in reader]

    return retlist


#--------------------------------------------------------------------------
# ヘッダ部取得
# 戻り値  retlist   : 書込対象ファイルに出力するヘッダ部を3行のcsvリスト形式で返す
#--------------------------------------------------------------------------
def getHeader():
    # ヘッダ部
    retlist = []
    # 1行目
    retlist.append(['','','','','','','','','','','','','','','','','','','','','','','','','','','','','', \
               '','','','','','','','','','','','','','','','','','','','','','','','','','','', '', \
               'キーマン','','','','','','','','','','','','','','','','','','','','','','','','','','','', \
               'キーマン','','','','','','','','','','','','','','','','','','','','','','','','','','',''] )
    # 2行目
    retlist.append(['選手情報','','','','','', \
               'Lv1','','','','','','','','', \
               'Lv99','','','','','','','','',
               'Type','','', '','','','','','','','', \
               '技情報','','','','','','','','','','','','','','','','','','','','','', \
               '育成タイプ1','','','','','','','', \
               '装備込み','','','','','','','','','','', \
               '期待値','','','','','','','','', \
               '育成タイプ2','','','','','','','', \
               '装備込み','','','','','','','','','','', \
               '期待値','','','','','','','',''] )
    # 3行目
    retlist.append(['No','名前','略称','性別','属性','ポジション',\
               'GP','TP', 'KCK','BDY','CNT','GRD','SPF','STM','GUT', \
               'GP','TP', 'KCK','BDY','CNT','GRD','SPF','STM','GUT', \
               'GP','TP', 'KCK','BDY','CNT','GRD','SPF','STM','GUT','Fre','Total', \
               '技1','技種','威力','TP','属性','技2','技種','威力','TP','属性','技3','技種','威力','TP','属性','技4','技種','威力','TP','属性','最大GP','最大TP', \
               '特訓期限Lv','キック','ボディ','コントロール','ガード','スピード','スタミナ','ガッツ', \
               'GP','TP','キック','ボディ','コントロール','ガード','スピード','スタミナ','ガッツ', \
               '秘伝書1','秘伝書2', '最重要コマンド','最重要コマンド期待値','ドリブルコマンド','ドリブル期待値','ブロックコマンド','ブロック期待値','キープコマンド','キープ','最重要コマンド消費TP量', \
               '最終調整Lv','キック','ボディ','コントロール','ガード','スピード','スタミナ','ガッツ', \
               'GP','TP','キック','ボディ','コントロール','ガード','スピード','スタミナ','ガッツ', \
               '秘伝書1','秘伝書2', '最重要コマンド','最重要コマンド期待値','ドリブルコマンド','ドリブル期待値','ブロックコマンド','ブロック期待値','キープコマンド','キープ','最重要コマンド消費TP量'] )
    
    # ヘッダ部を返す
    return retlist


#--------------------------------------------------------------------------
# 読み込んだステータスの列番号から処理対象のステータスとカテゴリを取得する
# 引数
# priority    : 読み込み対象のステータス列番号。以下のいずれかが含まれる
#             : _KCK_MAX_ 最大値(キック)
#             : _BDY_MAX_ 最大値(ボディ)
#             : _CNT_MAX_ 最大値(コントロール)
#             : _GRD_MAX_ 最大値(ガード)
#             : _SPD_MAX_ 最大値(スピード)
#             : _STM_MAX_ 最大値(スタミナ)
#             : _GUT_MAX_ 最大値(ガッツ)
# 戻り値
# row         :ステータス配列の列番号(1～7)
# categoryType:カテゴリ番号(0:Aカテ、1:Bカテ、2:Cカテ)
#--------------------------------------------------------------------------
def getCsvRowToStatusRowAndCtgry(priority):
    # priorityからステータス配列(targetStatus)の列番号を求める
    row = priority - sub.Const._TP_MAX_
    # 変換結果がKicまたはConの場合、Aカテ
    if row in [ sub.Const._STATUS_ROW_KCK_, sub.Const._STATUS_ROW_CNT_ ]:
        categoryType = sub.Const._CTGRY_A_
    # 変換結果がSpeまたはStaの場合、Cカテ
    elif row in [ sub.Const._STATUS_ROW_SPD_, sub.Const._STATUS_ROW_STM_ ]:
        categoryType = sub.Const._CTGRY_C_
    # その他はB
    else:
        categoryType = sub.Const._CTGRY_B_
    
    # 列番号とカテゴリ番号を返す
    return row, categoryType


#--------------------------------------------------------------------------
# カテゴリごとの優先順位を取得
# 引数
# priority    : 読み込み対象のステータス列番号。以下のいずれかが含まれる
#             : _KCK_MAX_ 最大値(キック)
#             : _BDY_MAX_ 最大値(ボディ)
#             : _CNT_MAX_ 最大値(コントロール)
#             : _GRD_MAX_ 最大値(ガード)
#             : _SPD_MAX_ 最大値(スピード)
#             : _STM_MAX_ 最大値(スタミナ)
#             : _GUT_MAX_ 最大値(ガッツ)
# 戻り値
# retCategory[0] :Aカテ内での優先順
#            [1] :Bカテ内での優先順
#            [2] :Cカテ内での優先順
#--------------------------------------------------------------------------
def getCtgryPriority(priorities):
    ctgryA = []
    ctgryB = []
    ctgryC = []
    # 優先順位の数だけ繰り返す
    for cnt, priority in enumerate(priorities[1:],1):
        # カテゴリ番号を取得
        info = getCsvRowToStatusRowAndCtgry(priority)
        # Aカテの場合
        if sub.Const._CTGRY_A_ == info[1]:
            ctgryA.append(priority)
        # Cカテの場合
        elif sub.Const._CTGRY_C_ == info[1]:
            ctgryC.append(priority)
        # その他はBカテ
        else:
            ctgryB.append(priority)
    
    # Aカテ、Bカテ、Cカテごとの優先順を返す
    return [ctgryA, ctgryB, ctgryC]


#--------------------------------------------------------------------------
# ステータス配列の番号からカテゴリごとの優先順位を取得
# 引数
# priority    : 読み込み対象のステータス列番号。以下のいずれかが含まれる
#             : _STATUS_ROW_KCK_ キック
#             : _STATUS_ROW_BDY_ ボディ
#             : _STATUS_ROW_CNT_ コントロール
#             : _STATUS_ROW_GRD_ ガード
#             : _STATUS_ROW_SPD_ スピード
#             : _STATUS_ROW_STM_ スタミナ
#             : _STATUS_ROW_GUT_ ガッツ
# 戻り値
# retCategory : _CTGRY_A_または_CTGRY_B_または_CTGRY_C_
#--------------------------------------------------------------------------
def getStatusRowToCtgryPriority(priority):
    # 初期値にBカテを設定
    retCategory = sub.Const._CTGRY_B_
    # Aカテの場合
    if priority in [sub.Const._STATUS_ROW_KCK_, sub.Const._STATUS_ROW_CNT_]:
        # 戻り値にAカテを設定
        retCategory = sub.Const._CTGRY_A_
    # Cカテの場合
    elif priority in [sub.Const._STATUS_ROW_SPD_, sub.Const._STATUS_ROW_STM_]:
        # 戻り値にCカテを設定
        retCategory = sub.Const._CTGRY_C_
    
    # 戻り値を返す
    return retCategory


