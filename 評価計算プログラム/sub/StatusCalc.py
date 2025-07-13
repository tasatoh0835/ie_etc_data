import sub.Const
import sub.GlobalList
import copy
import math

#--------------------------------------------------------------------------
# 指定Lvでのステータス計算
# targetStatus[_CRNT_ROW_]に現在Lvを格納して返す
# 引数
# calcLv       : 計算対象のLv
# targetStatus : Lv～ガッツの値を格納した計算対象のステータス
#              : [0] 各最小ステータス
#              : [1] 各最大ステータス
#              : [2] 各ステータスの成長タイプ
#              : [3] 各現在ステータス値
# 戻り値
# 再計算後の現在ステータス値(calcTarget)
#--------------------------------------------------------------------------
def getCurrentStatus(calcLv, targetStatus):
    # 引数より戻り値をコピー
    calcTarget = copy.deepcopy(targetStatus)
    # typeListから現在Lvの補正値を取得
    calcStatus = []
    for cnt, type in enumerate(targetStatus[sub.Const._GRWT_ROW_][1:],0):
        calcStatus.append(int(sub.GlobalList.typeList[type][calcLv]))
    # 現在Lvのステータス値を算出した値に置き換え
    for cnt, type in enumerate(calcStatus):
        # 現在Lvのステータス = 最小ステータス + ((最大ステータス - 最小ステータス) * 成長タイプ / 100)(小数点以下切捨)
        calcTarget[sub.Const._CRNT_ROW_][cnt + 1] = targetStatus[sub.Const._LV_MIN_ROW_][cnt + 1] + \
                                                      math.floor((targetStatus[sub.Const._LV_MAX_ROW_][cnt + 1] - \
                                                           targetStatus[sub.Const._LV_MIN_ROW_][cnt + 1]) * type / 100 )
    # 計算結果を返す
    return calcTarget[sub.Const._CRNT_ROW_]


#--------------------------------------------------------------------------
# のびしろ調整開始Lvと特訓優先度に従った特訓後のステータスを計算する
#
# 引数
# targetStatus[0]   :Lv1時のステータス
#             [1]   :Lv99時のステータス,
#             [2]   :成長タイプ
#             [3]   :現在Lv時のステータス
# potentialValue    :ステータスMAX値
# priorities[0]     :育成方針(Aカテ重視、Bカテ重視、バランス型など)
#           [1]～[7]:優先ステータス1～7(先に格納されているステータスを優先)
# trainingPosition  :育成ポジション(FW、MF、DF、GK)
# 戻り値
# retStatus:特訓後のステータス
#--------------------------------------------------------------------------
def getTrainingResults(targetStatus, potentialValue, priorities, trainingPosition):
    
    # ステータス計算用変数([現在Lv],[次Lv],[現在Lvから次LvにUPする際の上昇量])
    calcStatus = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
    _NOW_LV_     = 0 # 現在Lv
    _NEXT_LV_    = 1 # 次Lv
    _LVUP_VALUE_ = 2 # 現在Lvから次LvにUPする際の上昇量
    # LvUP処理完了フラグ
    flgLvUP = False
    # カテゴリ別合計値([現在値],[保持値(1Lv前の値を保持)])
    categoryValue = [[0,0,0],[0,0,0]]
    _NOW_  = 0 # 現在値
    _KEEP_ = 1 # 保持値
    
    # カテゴリ別合計値の現在値にLv1の値を設定
    categoryValue[_NOW_] = [
        targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_KCK_] + targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_CNT_],
        targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_BDY_] + targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_GRD_] + targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_GUT_],
        targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_SPD_] + targetStatus[sub.Const._LV_MIN_ROW_][sub.Const._STATUS_ROW_STM_]
    ]
    # 特化育成計算用処理
    # 2.育成ポジションがFWかつ、Aカテ特化(競り合い)型の場合
    if trainingPosition in [sub.Const._POS_FW_] and priorities[0] in [sub.Const._KCK_AND_CNT_]:
        # Aカテ特化後の特訓値+100
        categoryValue[_NOW_][sub.Const._CTGRY_A_] += 100
    # 4.育成ポジションがMFまたはDFかつ、B特化型の場合
    # 5.育成ポジションがGKかつ、B特化型の場合
    elif ( trainingPosition in [sub.Const._POS_MF_, sub.Const._POS_DF_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_] ) or \
         ( trainingPosition in [sub.Const._POS_GK_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_] ):
        # Bカテ特化後の特訓値+150
        categoryValue[_NOW_][sub.Const._CTGRY_B_] += 150
    # 現在のカテゴリ別合計値を保持する
    categoryValue[_KEEP_] = copy.deepcopy(categoryValue[_NOW_])
    # Lv1のステータスをセット。
    for lvUpCnt in range(2, 100):
        # 現在Lvと次のステータスを取得
        calcStatus[_NOW_LV_] = sub.StatusCalc.getCurrentStatus(lvUpCnt - 1, targetStatus)
        calcStatus[_NEXT_LV_] = sub.StatusCalc.getCurrentStatus(lvUpCnt, targetStatus)
        # 次Lvのステータスから現在Lvのステータスを差し引いた値をLvUP時の上昇ステータスとして格納する
        for statusCnt in range(0, len(calcStatus[_NEXT_LV_])):
            calcStatus[_LVUP_VALUE_][statusCnt] = calcStatus[_NEXT_LV_][statusCnt] - calcStatus[_NOW_LV_][statusCnt]
        # 各ステータスの上昇量取得
        for statusCnt in range(7):
            calcRow = sub.CsvControl.getStatusRowToCtgryPriority(sub.GlobalList.lvUpStatusList[statusCnt])
            # ステータスの加算処理を実施
            categoryValue[_NOW_][calcRow] += calcStatus[_LVUP_VALUE_][sub.GlobalList.lvUpStatusList[statusCnt]]
        # LvUP処理の終了条件チェック
        requestFreVal = 0
        # 1.育成ポジションがFWかつ、バランス型の場合
        if trainingPosition in [sub.Const._POS_FW_] and priorities[0] in [sub.Const._NORMAL_]:
            # ・要求のびしろ量 = ( Aカテ目標値 - 現在LvのAカテ合計 ) + ( Cカテ目標値 - 現在LvのCカテ合計 )
            # ・Aカテ目標値=Lv99時のKCK+51
            # ・Cカテ目標値=Lv99時のSPD+51
            requestFreVal = ( targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_KCK_] + 51 - categoryValue[_NOW_][sub.Const._CTGRY_A_] ) + \
                            ( targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51 - categoryValue[_NOW_][sub.Const._CTGRY_C_] )
        # 2.育成ポジションがFWかつ、Aカテ特化(競り合い)型の場合
        elif trainingPosition in [sub.Const._POS_FW_] and priorities[0] in [sub.Const._KCK_AND_CNT_]:
            # ・要求のびしろ量 = Cカテ目標値 - 現在LvのCカテ合計 - 1
            # ・Cカテ目標値=Lv99時のSPD+50
            requestFreVal = targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 50 - categoryValue[_NOW_][sub.Const._CTGRY_C_]
        # 3.育成ポジションがMFまたはDFまたはGKかつ、バランス型の場合
        elif trainingPosition in [sub.Const._POS_MF_, sub.Const._POS_DF_, sub.Const._POS_GK_] and priorities[0] in [sub.Const._NORMAL_]:
            # ・要求のびしろ量 = ( Aカテ目標値 - 現在LvのAカテ合計 ) + ( Cカテ目標値 - 現在LvのCカテ合計 )
            # ・Aカテ目標値=Lv99時のCNT+51
            # ・Cカテ目標値=Lv99時のSPD+51
            requestFreVal = ( targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_CNT_] + 51 - categoryValue[_NOW_][sub.Const._CTGRY_A_] ) + \
                            ( targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51 - categoryValue[_NOW_][sub.Const._CTGRY_C_] )
        # 4.育成ポジションがMFまたはDFかつ、B特化型の場合
        elif trainingPosition in [sub.Const._POS_MF_, sub.Const._POS_DF_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_]:
            # ・要求のびしろ量 = Cカテ目標値 - 現在LvのCカテ合計
            # ・Cカテ目標値=Lv99時のSPD+51
            requestFreVal = targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51 - categoryValue[_NOW_][sub.Const._CTGRY_C_]
        # 5.育成ポジションがGKかつ、B特化型の場合
        elif trainingPosition in [sub.Const._POS_GK_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_]:
            # ・要求のびしろ量 = 0
            requestFreVal = 0
        # 現在ののびしろ残量が要求のびしろ量を下回った場合
        if potentialValue -  sum(categoryValue[_NOW_]) < requestFreVal:
            # 1つ下のLvを目標Lvに設定
            lvUpCnt -= 1
            # 1つ下のLvを目標Lvに設定
            categoryValue[_NOW_] = copy.deepcopy(categoryValue[_KEEP_])
            # LvUP処理完了フラグをTrueに設定
            flgLvUP = True
            # パラメータ加算処理を終了
            break
        # 現在のcategoryValueを1つ下のLvとして保持
        categoryValue[_KEEP_] = copy.deepcopy(categoryValue[_NOW_])
    # のびしろ残量計算
    remainValue = potentialValue -  sum(categoryValue[_NOW_])
    # のびしろ残量がある場合、最優先するステータスにのびしろを付与
    if 0 < remainValue:
        # 育成ポジションがFWかつ、バランス型の場合
        # Aカテ＞Cカテ＞Bカテの優先順にのびしろを付与
        if trainingPosition in [sub.Const._POS_FW_] and priorities[0] in [sub.Const._NORMAL_]:
            # Aカテ合計がLv99時のキック値+51に到達していない場合
            if categoryValue[_NOW_][sub.Const._CTGRY_A_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_KCK_] + 51:
                # Aカテに加算する値を計算
                addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_KCK_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_A_]
                # のびしろ残量がAカテに加算する値より大きい場合
                if remainValue > addValue:
                    # のびしろ残量からAカテに加算する値を減算
                    remainValue -= addValue 
                else:
                    # のびしろ残量をAカテに加算する値に設定
                    addValue = remainValue
                    # のびしろ残量を0に設定
                    remainValue = 0
                # Aカテにのびしろを加算
                categoryValue[_NOW_][sub.Const._CTGRY_A_] += addValue
                # のびしろ残量がある場合、Cカテにのびしろを付与
                if 0 < remainValue:
                    # Cカテ合計がLv99時のスピード値+51に到達していない場合
                    if categoryValue[_NOW_][sub.Const._CTGRY_C_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51:
                        # Cカテにのびしろを加算
                        addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                        # のびしろ残量がCカテに加算する値より大きい場合
                        if remainValue > addValue:
                            # のびしろ残量からCカテに加算する値を減算
                            remainValue -= addValue 
                        else:
                            # のびしろ残量をCカテに加算する値に設定
                            addValue = remainValue
                            # のびしろ残量を0に設定
                            remainValue = 0
                        # Cカテにのびしろを加算
                        categoryValue[_NOW_][sub.Const._CTGRY_C_] += addValue
                        # のびしろ残量がある場合、Bカテにのびしろを付与
                        if 0 < remainValue:
                            categoryValue[_NOW_][sub.Const._CTGRY_B_] += remainValue
                            # のびしろ残量を0に設定
                            remainValue = 0
        # 育成ポジションがGKかつ、B特化型の場合
        # Bカテ＞Cカテ＞Aカテの優先順にのびしろを付与
        # Bカテは特化育成計算用処理で調整済みのため、ここでは割り振らない
        elif trainingPosition in [sub.Const._POS_GK_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_]:
            # のびしろ残量がある場合、Cカテにのびしろを付与
            if 0 < remainValue:
                # Cカテ合計がLv99時のスピード値+51に到達していない場合
                if categoryValue[_NOW_][sub.Const._CTGRY_C_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51:
                    # Cカテにのびしろを加算
                    addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                    # のびしろ残量がCカテに加算する値より大きい場合
                    if remainValue > addValue:
                        # のびしろ残量からCカテに加算する値を減算
                        remainValue -= addValue 
                    else:
                        # のびしろ残量をCカテに加算する値に設定
                        addValue = remainValue
                        # のびしろ残量を0に設定
                        remainValue = 0
                    # Cカテにのびしろを加算
                    categoryValue[_NOW_][sub.Const._CTGRY_C_] += addValue
                    # Cカテ合計がLv99時のスピード値+51に到達していない場合、Bカテの余剰分を減算
                    if categoryValue[_NOW_][sub.Const._CTGRY_C_] < (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51):
                        # 不足分を計算
                        redValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                        # Cカテに不足分を加算
                        categoryValue[_NOW_][sub.Const._CTGRY_C_] = targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51
                        # AカテからCカテへの加算分を減算
                        categoryValue[_NOW_][sub.Const._CTGRY_B_] -= redValue
                    # のびしろ残量がある場合、Aカテにのびしろを付与
                    if 0 < remainValue:
                        categoryValue[_NOW_][sub.Const._CTGRY_A_] += remainValue
                        # のびしろ残量を0に設定
                        remainValue = 0
        # FW以外のバランス型育成の場合または、
        # 育成ポジションがMFまたはDFかつ、B特化型の場合
        # Bカテ＞Cカテ＞Aカテの優先順にのびしろを付与
        # Bカテは特化育成計算用処理で調整済みのため、ここでは割り振らない
        elif ( trainingPosition in [sub.Const._POS_MF_, sub.Const._POS_DF_, sub.Const._POS_GK_] and priorities[0] in [sub.Const._NORMAL_] ) or \
             ( trainingPosition in [sub.Const._POS_MF_, sub.Const._POS_DF_] and priorities[0] in [sub.Const._BDY_GRD_AND_GUT_] ):
            # Cカテ合計がLv99時のスピード値+51に到達していない場合
            if categoryValue[_NOW_][sub.Const._CTGRY_C_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51:
                # Cカテにのびしろを加算
                addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                # のびしろ残量がCカテに加算する値より大きい場合
                if remainValue > addValue:
                    # のびしろ残量からCカテに加算する値を減算
                    remainValue -= addValue 
                else:
                    # のびしろ残量をCカテに加算する値に設定
                    addValue = remainValue
                    # のびしろ残量を0に設定
                    remainValue = 0
                # Cカテにのびしろを加算
                categoryValue[_NOW_][sub.Const._CTGRY_C_] += addValue
                # Cカテ合計がLv99時のスピード値+51に到達していない場合、Bカテの余剰分を減算
                if categoryValue[_NOW_][sub.Const._CTGRY_C_] < (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51):
                    # 不足分を計算
                    redValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                    # Cカテに不足分を加算
                    categoryValue[_NOW_][sub.Const._CTGRY_C_] = targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51
                    # AカテからCカテへの加算分を減算
                    categoryValue[_NOW_][sub.Const._CTGRY_B_] -= redValue
                # のびしろ残量がある場合、Bカテにのびしろを付与
                if 0 < remainValue:
                    # Bカテ合計がLv99時のボディ+ガード+101に到達していない場合
                    if categoryValue[_NOW_][sub.Const._CTGRY_C_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_BDY_] + \
                                                                   targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_BDY_] + 101:
                        # Bカテにのびしろを加算
                        addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                        # のびしろ残量がBカテに加算する値より大きい場合
                        if remainValue > addValue:
                            # のびしろ残量からCカテに加算する値を減算
                            remainValue -= addValue 
                        else:
                            # のびしろ残量をCカテに加算する値に設定
                            addValue = remainValue
                            # のびしろ残量を0に設定
                            remainValue = 0
                        # Bカテにのびしろを加算
                        categoryValue[_NOW_][sub.Const._CTGRY_B_] += addValue
                        # のびしろ残量がある場合、Aカテにのびしろを付与
                        if 0 < remainValue:
                            categoryValue[_NOW_][sub.Const._CTGRY_A_] += remainValue
                            # のびしろ残量を0に設定
                            remainValue = 0
        # 育成ポジションがFWかつ、Aカテ特化(競り合い)型の場合
        # Aカテ＞Cカテ＞Bカテの優先順にのびしろを付与
        # Aカテは特化育成計算用処理で調整済みのため、ここでは割り振らない
        elif ( trainingPosition in [sub.Const._POS_FW_] and priorities[0] in [sub.Const._KCK_AND_CNT_] ):
            # Cカテ合計がLv99時のスピード値+51に到達していない場合
            if categoryValue[_NOW_][sub.Const._CTGRY_C_] < targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51:
                # Cカテにのびしろを加算
                addValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                # のびしろ残量がCカテに加算する値より大きい場合
                if remainValue > addValue:
                    # のびしろ残量からCカテに加算する値を減算
                    remainValue -= addValue 
                else:
                    # のびしろ残量をCカテに加算する値に設定
                    addValue = remainValue
                    # のびしろ残量を0に設定
                    remainValue = 0
                # Cカテにのびしろを加算
                categoryValue[_NOW_][sub.Const._CTGRY_C_] += addValue
                # Cカテ合計がLv99時のスピード値+51に到達していない場合、Aカテの余剰分を減算
                if categoryValue[_NOW_][sub.Const._CTGRY_C_] < (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51):
                    # 不足分を計算
                    redValue = (targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51) - categoryValue[_NOW_][sub.Const._CTGRY_C_]
                    # Cカテに不足分を加算
                    categoryValue[_NOW_][sub.Const._CTGRY_C_] = targetStatus[sub.Const._LV_MAX_ROW_][sub.Const._STATUS_ROW_SPD_] + 51
                    # AカテからCカテへの加算分を減算
                    categoryValue[_NOW_][sub.Const._CTGRY_A_] -= redValue
                # のびしろ残量がある場合、Bカテにのびしろを付与
                if 0 < remainValue:
                    categoryValue[_NOW_][sub.Const._CTGRY_B_] += remainValue
                    # のびしろ残量を0に設定
                    remainValue = 0
    # ステータス振り分け結果配列(戻り値用)
    # 育成開始Lv,KCK,BDY,CNT,GRD,SPD,STM,GUT
    retStatus = [lvUpCnt,1,1,1,1,1,1,1]
    categoryValue[_NOW_][sub.Const._CTGRY_A_] -= 2
    categoryValue[_NOW_][sub.Const._CTGRY_B_] -= 3
    categoryValue[_NOW_][sub.Const._CTGRY_C_] -= 2
    # 各カテゴリ内での優先順位を取得
    categoryInfo = sub.CsvControl.getCtgryPriority(priorities)
    # カテゴリごとに繰り返す
    for cateCnt, ctgry in enumerate(categoryInfo):
        # 優先順位が高いものから順に最大値を設定する
        for priorityCnt, priority in enumerate(ctgry):
            # 対象の列番号を取得
            calcRow = sub.CsvControl.getCsvRowToStatusRowAndCtgry(priority)
            # カテゴリ内の合計値が最大値 + sub.Const._CLC_TRAINING_VAL_以上の場合、最大値であるLv99時のステータス+50を設定
            if categoryValue[_NOW_][calcRow[1]] > ( targetStatus[sub.Const._LV_MAX_ROW_][calcRow[0]] + sub.Const._CLC_TRAINING_VAL_ ):
                # 戻り値にLv99時のステータス+50を設定
                retStatus[calcRow[0]] = targetStatus[sub.Const._LV_MAX_ROW_][calcRow[0]] + sub.Const._CLC_TRAINING_VAL_
                # カテゴリ内の合計値から加算した分の値を減算
                categoryValue[_NOW_][calcRow[1]] -= (retStatus[calcRow[0]] - 1)
            # カテゴリ内の合計値が最大値 + sub.Const._CLC_TRAINING_VAL_を超過していない場合
            else:
                # 余りを全て加算
                retStatus[calcRow[0]] += categoryValue[_NOW_][calcRow[1]]
                # ステータス合計値を0に設定
                categoryValue[_NOW_][calcRow[1]] = 0
    # ステータスを返す
    return retStatus


