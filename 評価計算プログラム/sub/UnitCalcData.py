import sub.Const

#--------------------------------------------------------------------------
# ヘッダ部
# 引数    targetStatus : 計算対象ステータス(targetStatus[sub.Const._CRNT_ROW_])
# 戻り値  unitcalcList : トータルテクニック計算に用いる基本的な補正値のリストを返す
#--------------------------------------------------------------------------
def getUnitCalcList(targetStatus):
    # 基本補正値
    # 補正倍率, 乱数幅, バーニングフェーズ時補正, シュート補正, 必殺技威力補正,キック～ガッツ補正
    # キック、ボディ、コントロール、ガード、スピード、ガッツ、スタミナ
    unitcalcList = [[ 20, 25, 20, 10,100, 80,  0,  0,  0,  0,  0, 20], # シュート
                    [-40, 60, 20,  0,100,  0, 75, 25,  0,  0,  0,  0], # ドリブル
                    [-10, 30, 20,  0,100,  0, 25,  0, 75,  0,  0,  0], # ブロック
                    [ 40, 10, 20,  0,100,  0, 20,  0, 80,  0,  0,  0], # キャッチ
                    [ 50,100,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # 競り合い1[OF]
                    [  0,  0,  0,  0,  0,  0, 20,  0, 50,  0,  0, 20], # 競り合い2[DF]
                    [ 50,100,  0,  0,  0,  0,  0, 50,  0, 20,  0, 30], # ボールキープ
                    [ 40,100, 20, 10,100, 80,  0,  0,  0,  0,  0, 20], # 必殺シュート
                    [-25,100, 20,  0,100,  0, 70, 20,  0,  0,  0, 20], # 必殺ドリブル
                    [ 15, 20, 20,  0,100,  0, 20,  0, 70,  0,  0, 20], # 必殺ブロック
                    [ 70, 40, 20,  0,100,  0,  0,  0, 80,  0,  0, 20], # 必殺キャッチ
                    [ 80, 80, 20,  0,100,  0,  0,  0, 80,  0,  0, 20], # シュートブロック(ブロック)
                    [ 80, 80, 20,  0,100, 80,  0, 20,  0,  0,  0,  0]] # シュートブロック(シュート)
    # キーマンのタイプに従い、unitcalcListの値に補正を加える
    # FWの場合
    if sub.Const._KEYMAN_ in [sub.Const._POS_FW_]:
        addValue = int( targetStatus[sub.Const._STATUS_ROW_KCK_] / 10)
        if targetStatus[sub.Const._STATUS_ROW_KCK_] > 120:
            addValue = 13
        for cnt, unitcalc in enumerate(unitcalcList):
            # 無印2では元が0の場合はキーマン補正加算の対象外
            if unitcalc[sub.Const._CLC_KCK_] > 0:
                unitcalc[sub.Const._CLC_KCK_] += addValue
    # MFの場合
    elif sub.Const._KEYMAN_ in [sub.Const._POS_MF_]:
        addValue = int( targetStatus[sub.Const._STATUS_ROW_CNT_] / 10)
        if targetStatus[sub.Const._STATUS_ROW_CNT_] > 120:
            addValue = 13
        for cnt, unitcalc in enumerate(unitcalcList):
            # 無印2では元が0の場合はキーマン補正加算の対象外
            if unitcalc[sub.Const._CLC_CNT_] > 0:
                unitcalc[sub.Const._CLC_CNT_] += addValue
    # DFの場合
    elif sub.Const._KEYMAN_ in [sub.Const._POS_DF_]:
        addValue = int( targetStatus[sub.Const._STATUS_ROW_GRD_] / 10)
        if targetStatus[sub.Const._STATUS_ROW_GRD_] > 120:
            addValue = 13
        for cnt, unitcalc in enumerate(unitcalcList):
            # 無印2では元が0の場合はキーマン補正加算の対象外
            if unitcalc[sub.Const._CLC_BDY_] > 0:
                unitcalc[sub.Const._CLC_BDY_] += addValue
    # GKの場合
    elif sub.Const._KEYMAN_ in [sub.Const._POS_GK_]:
        addValue = int( targetStatus[sub.Const._STATUS_ROW_BDY_] / 10)
        if targetStatus[sub.Const._STATUS_ROW_BDY_] > 120:
            addValue = 13
        for cnt, unitcalc in enumerate(unitcalcList):
            # 無印2では元が0の場合はキーマン補正加算の対象外
            if unitcalc[sub.Const._CLC_POW_] > 0:
                unitcalc[sub.Const._CLC_POW_] += addValue
    return unitcalcList
