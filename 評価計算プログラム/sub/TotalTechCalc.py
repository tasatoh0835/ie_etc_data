import sub.Const
import sub.GlobalList
import copy

#--------------------------------------------------------------------------
# 育成ポジションと必殺技種別からトータルテクニック計算結果のストック先を返す
#
# 引数
# trainingPosition : 育成ポジション
# command          : 計算するコマンド
# 戻り値
# calcDataList : 計算するコマンド(calcData[])のリスト
#                シュートブロック技の場合、通常時とシュートブロック時の2パターンを格納
# calcData[0]  : 特訓後のステータス
#         [1]  : トータルテクニック計算結果配列の格納先
#--------------------------------------------------------------------------
def getTotalTechStockRow(trainingPosition, command):
    # 初期値として計算対象外を設定
    calcData = [sub.Const._CMD_PASS_, 0]
    # 戻り値作成
    calcDataList = []
    # 必殺シュートの場合
    if command in [sub.Const._MV_NS_, sub.Const._MV_LS_, sub.Const._MV_BS_, sub.Const._MV_SC_]:
        # FWまたはMFの場合
        if trainingPosition in [sub.Const._POS_FW_, sub.Const._POS_MF_]:
            # シュート
            calcData[0] = sub.Const._CMD_SP_SHOT_
            calcData[1] = sub.Const._RET_SHOT_
        # DFかつシュートブロック(シュート)の場合
        elif trainingPosition in [sub.Const._POS_FW_, sub.Const._POS_MF_] and command in [sub.Const._MV_BS_]:
            # シュートブロック(シュート)
            calcData[0] = sub.Const._CMD_SP_SHBL_
            calcData[1] = sub.Const._RET_SHBL_
    # 必殺ドリブルの場合
    if command in [sub.Const._MV_DR_]:
        # 必殺ドリブルとして処理
        calcData[0] = sub.Const._CMD_SP_DRBL_
        calcData[1] = sub.Const._RET_DRBL_
    # 必殺ブロック
    if command in [sub.Const._MV_BL_, sub.Const._MV_BB_]:
        # DFかつ、シュートブロック技の場合
        if trainingPosition in [sub.Const._POS_DF_] and command in [sub.Const._MV_BB_]:
            # シュートブロックも計算対象とする
            calcDataList.append([sub.Const._CMD_SP_BLBL_, sub.Const._RET_BLBL_])
        # ブロック
        calcData[0] = sub.Const._CMD_SP_BLCK_
        calcData[1] = sub.Const._RET_BLCK_
    # GKの場合かつ必殺キャッチの場合
    if trainingPosition in [sub.Const._POS_GK_] and command in [sub.Const._MV_CA_, sub.Const._MV_P1_, sub.Const._MV_P2_]:
        calcData[0] = sub.Const._CMD_SP_CTCH_
        calcData[1] = sub.Const._RET_CTCH_
    
    # 結果をリストに格納
    calcDataList.append(calcData)
    
    # 戻り値としてリストを返す
    return calcDataList


#--------------------------------------------------------------------------
# ステータスと必殺技種別でのトータルテクニック期待値を計算する
#
# 引数
# targetStatus[0] : Lv1時のステータス
#             [1] : Lv99時のステータス,
#             [2] : 成長タイプ
#             [3] : 現在Lv時のステータス
# position        : 計算対象のポジション
# command         : 計算対象となる必殺技種別
# specialMoveList : 習得済必殺技リスト
# moveData        : 計算対象必殺技(通常コマンドの場合、None)
# 戻り値
# retStatus:特訓後のステータス
#--------------------------------------------------------------------------
def calcTotalTechEx(targetStatus, position, command, specialMoveList, moveData):
    calcForm = 0
    # コマンドが計算対象外の場合、0を返す
    if command in [sub.Const._CMD_PASS_]:
        return calcForm
    # キーマンDFでのトータルテクニック取得
    unitCalc = sub.UnitCalcData.getUnitCalcList(targetStatus)
    # 技情報がNoneの場合、通常コマンドバトル用の情報を設定
    if moveData is None:
        # 技名なし、技種なし、威力0、TP0、一致補正なし
        moveData = ['-' ,'-', 0, 0, '']
    # 技威力 x POWER
    calcForm = int(moveData[sub.Const._MOVE_POW_]) * unitCalc[command][sub.Const._CLC_POW_]
    # ステータス x 補正値
    for statusCnt, status in enumerate(targetStatus):
        if 0 == statusCnt:
            continue
        calcForm += ( status * unitCalc[command][sub.Const._CLC_POW_ + statusCnt])
    calcForm = int(calcForm * 41 / 4096)
    # magnification
    calcForm = calcForm + unitCalc[command][sub.Const._CLC_MAG_]
    # random
    randamWidth = unitCalc[command][sub.Const._CLC_RND_]
    # ランダム範囲分の下限から上限まで格納するリストを作成
    calcFormList = []
    for randamCnt in range(randamWidth):
        calcFormList.append(int(calcForm + randamCnt))
    # シュート補正
    scale = 0
    # 通常シュートはメモリ最大
    if command in [sub.Const._CMD_SHOT_]:
        scale = 3
    # 必殺シュートはメモリ1倍
    elif command in [sub.Const._CMD_SP_SHOT_]:
        scale = 1
    for calcCnt in range(len(calcFormList)):
        calcFormList[calcCnt] += (scale * unitCalc[command][sub.Const._CLC_SHT_])
    # 属性相性(有利)、属性相性(属性強化)
    # 無印2環境では突出したGKがいないので、優劣は特に計算しないこととする
    # 必殺技の属性一致補正
    if moveData[sub.Const._MOVE_ELE_] in '一致':
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] += sub.Const._TYPE_MATCH_BONUS_
    # スキル処理
    # イケメンＵＰ！、お色気ＵＰ！は相手のトータルテクニックを0.9倍するデバフスキルだが、
    # 評価しないわけにもいかない有用スキルなので、自身のトータルテクニックに重みをつける形で対応
    # 相手を選びやすい攻撃のポジション(FW、MF)では1.1倍の補正とし、相手をえり好みできない守備のポジション(DF、GK)での評価対象外とする
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CHRM_) and position in [sub.Const._POS_FW_, sub.Const._POS_MF_]:
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] += int(calcFormList[calcCnt] * ( sub.Const._SKL_CHRM_ - 100 ) / 100)
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_COOL_) and position in [sub.Const._POS_FW_, sub.Const._POS_MF_]:
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] += int(calcFormList[calcCnt] * ( sub.Const._SKL_COOL_ - 100 ) / 100)
    # キーパープラス以外のプラス系スキルは育成ポジションが合致する場合にのみ補正を与えることとする
    # キーパープラス習得者かつポジションGKかつキャッチ系コマンドの場合、キーパープラス補正を付与
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_GKP_) and position in [sub.Const._POS_GK_] and \
        command in [sub.Const._CMD_CTCH_, sub.Const._CMD_SP_CTCH_]:
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_PLUS_) / 100)
    # 習得者以外もスキル適用対象とする場合、またはシュートプラス習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHP_):
        # 必殺シュートかつ、ポジションFWの場合
        if command in [sub.Const._CMD_SP_SHOT_] and position in [ sub.Const._POS_FW_]:
            # シュートプラス補正を付与
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_PLUS_) / 100)
    # 習得者以外もスキル適用対象とする場合、またはディフェンスプラス習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_DFP_):
        # ブロック、必殺ブロックかつ、ポジションMFの場合
        if command in [sub.Const._CMD_BLCK_, sub.Const._CMD_SP_BLCK_] and sub.Const._POS_MF_ == position:
            # ディフェンスプラス補正を付与
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_PLUS_) / 100)
    # 習得者以外もスキル適用対象とする場合、またはオフェンスプラス習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_OFP_):
        # ドリブル、必殺ドリブルかつポジションMFの場合
        if command in [sub.Const._CMD_DRBL_, sub.Const._CMD_SP_DRBL_] and  sub.Const._POS_MF_ == position:
            # ディフェンスプラス補正を付与
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_PLUS_) / 100)
    # ちょうわざ！を習得している場合
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_BGMV_):
        # ちょうわざ！補正を付与
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_BGMV_) / 100)
    # 上振れ/下振れ
    # やくびょうがみ
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_JINX_):
        # やくびょうがみの期待値を反映
        for calcCnt in range(len(calcFormList)):
            # やくびょうがみの効果 = 1/5で無効、1%減衰、2%減衰、3%減衰、4%減衰のいずれかが発生
            calcFormList[calcCnt] = int(
                ( calcFormList[calcCnt] / 5 ) + 
                ( calcFormList[calcCnt] * (99 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (98 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (97 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (96 / 100 ) / 5 ) )
    # クリティカル！
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CRTC_):
        # クリティカルの期待値を反映
        for calcCnt in range(len(calcFormList)):
            # クリティカルの効果 = 11%で1.5倍
            calcFormList[calcCnt] = int(
                ( calcFormList[calcCnt] *  89 / 100 ) + 
                ( ( calcFormList[calcCnt] * sub.Const._SKL_CRTC_ / 100 ) * 11 / 100 ) )
    # ラッキー！
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_LCKY_):
        # ラッキーの期待値を反映
        for calcCnt in range(len(calcFormList)):
            # ラッキーの効果 = 1/5で無効、1%上昇、2%上昇、3%上昇、4%上昇のいずれかが発生
            calcFormList[calcCnt] = int( 
                ( calcFormList[calcCnt] / 5 ) + 
                ( calcFormList[calcCnt] * (101 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (102 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (103 / 100 ) / 5 ) + 
                ( calcFormList[calcCnt] * (104 / 100 ) / 5 ) )
    # 習得者以外もスキル適用対象とする場合、またはシュートフォース習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHF_):
        # 必殺シュートの場合、シュートフォース補正を付与
        if command in [sub.Const._CMD_SP_SHOT_]:
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_FORC_) / 100)
    # 習得者以外もスキル適用対象とする場合、またはディフェンスフォース習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_DFF_):
        # ブロック、必殺ブロックの場合、ディフェンスフォース補正を付与
        if command in [sub.Const._CMD_BLCK_, sub.Const._CMD_SP_BLCK_]:
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_FORC_) / 100)
    # 習得者以外もスキル適用対象とする場合、またはオフェンスフォース習得者の場合
    if sub.Const._ALL_PLAYERS_ or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_OFF_):
        # ドリブル、必殺ドリブルの場合、オフェンスフォース補正を付与
        if command in [sub.Const._CMD_DRBL_, sub.Const._CMD_SP_DRBL_]:
            for calcCnt in range(len(calcFormList)):
                calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_FORC_) / 100)
    # こんしん！を習得している場合
    # 無印2にこんしん！は存在しないため、実施せず
    # シュートブロック(パワーダウン判定)補正
    if command in [sub.Const._CMD_SP_BLBL_]:
        # 相手のシュートのトータルテクニックがシュートブロックの1.25倍を下回る場合、パワーダウン成功
        # 期待値を1.25倍することで表現
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._POWER_DOWN_) / 100)
    # 期待値計算
    retValue = int(sum(calcFormList) / len(calcFormList))
    # ファウル率計算
    foulRateVal = ['0']
    # ドリブル、ブロックの通常コマンドは1%で計算
    if command in [sub.Const._CMD_DRBL_, sub.Const._CMD_BLCK_]:
        foulRateVal = ['1']
    # 必殺技の場合は必殺技詳細データを技名で検索し、ファウル率を取得
    if moveData[sub.Const._MOVE_TYP_] in [sub.Const._MV_NS_, sub.Const._MV_LS_, sub.Const._MV_BS_, sub.Const._MV_DR_, sub.Const._MV_SC_, \
                                          sub.Const._MV_BL_,sub.Const._MV_BB_, sub.Const._MV_CA_, sub.Const._MV_P1_, sub.Const._MV_P2_, sub.Const._MV_BL_]:
        foulRateVal = [list[sub.Const._MOVE_LIST_F_RATE_ROW_] for list in sub.GlobalList.moveList \
                        if list[sub.Const._MOVE_LIST_NAME_ROW_] == moveData[sub.Const._MOVE_NAM_]]
    # 期待値 = 期待値 x (1 - ファウル発生率(%))
    retValue = int(retValue * (100 - int(foulRateVal[0])) / 100)
    # イカサマ！は相手のファウル率を+10％するスキル
    # 自身のトータルテクニックに重みをつけることで対応
    # イカサマ！を習得しており、コマンドバトルがドリブルまたはブロックの場合
    if sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CHEA_) and \
       command in [sub.Const._CMD_DRBL_, sub.Const._CMD_SP_DRBL_, sub.Const._CMD_BLCK_, sub.Const._CMD_SP_BLCK_]:
        # イカサマ！補正を付与
        for calcCnt in range(len(calcFormList)):
            calcFormList[calcCnt] = int(calcFormList[calcCnt] * (sub.Const._SKL_CHEA_) / 100)
    # 戻り値が0以上1200以下となるよう丸める
    retValue = min(1200, max(0, retValue))
    # 計算結果を戻り値として返す
    return retValue


#--------------------------------------------------------------------------
# 引数に指定したコマンドにおいて、技1と技2を与えた場合のトータルテクニックを比較し、期待値が大きい方の技を返す
# 同値となる場合、技1を優先する
# 引数
# targetStatus[0] : Lv1時のステータス
#             [1] : Lv99時のステータス,
#             [2] : 成長タイプ
#             [3] : 現在Lv時のステータス
# position        : 計算対象のポジション
# command         : 計算対象となるコマンド
# specialMoveList : 習得済必殺技リスト
# moveData1       : 計算対象必殺技1
# moveData1       : 計算対象必殺技2
# 戻り値
# moveData :必殺技データ
#--------------------------------------------------------------------------
def compTotalTechEx(targetStatus, position, command, specialMoveList, moveData1, moveData2):

    # 必殺技1計算用必殺技リストを作成
    moveList1 = copy.deepcopy(specialMoveList)
    moveList1.append(moveData1)
    # 必殺技1のトータルテクニック計算
    move1TotalTech = 0
    for moveCnt, move in enumerate(moveList1):
        # 比較対象コマンドの用途と合致する技のみ計算する
        # commandが_CMD_SP_SHOT_かつシュート必殺技
        # commandが_CMD_SP_DRBL_かつドリブル必殺技
        # commandが_CMD_SP_BLCK_かつシュート必殺技
        # commandが_CMD_SP_CTCH_かつシュート必殺技
        # commandが_CMD_SP_SHBL_かつシュートブロック必殺技
        # commandが_CMD_SP_BLBL_かつシュートブロック必殺技
        if ( command in [sub.Const._CMD_SP_SHOT_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_NS_, sub.Const._MV_LS_, sub.Const._MV_BS_, sub.Const._MV_SC_] ) or \
           ( command in [sub.Const._CMD_SP_DRBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_DR_] ) or \
           ( command in [sub.Const._CMD_SP_BLCK_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BL_, sub.Const._MV_BB_] ) or \
           ( command in [sub.Const._CMD_SP_CTCH_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_CA_, sub.Const._MV_P1_, sub.Const._MV_P2_] ) or \
           ( command in [sub.Const._CMD_SP_SHBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BS_] ) or \
           ( command in [sub.Const._CMD_SP_BLBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BB_] ):
            # 計算実行
            calcValue = calcTotalTechEx(targetStatus, position, command, moveList1, move)
            # 計算結果が既存の値を超過する場合、
            if move1TotalTech < calcValue:
                # トータルテクニックを保持
                move1TotalTech = calcTotalTechEx(targetStatus, position, command, moveList1, move)

    # 必殺技2計算用必殺技リストを作成
    moveList2 = copy.deepcopy(specialMoveList)
    moveList2.append(moveData2)
    # 必殺技2のトータルテクニック計算
    move2TotalTech = 0
    for moveCnt, move in enumerate(moveList2):
        # 比較対象コマンドの用途と合致する技のみ計算する
        # commandが_CMD_SP_SHOT_かつシュート必殺技
        # commandが_CMD_SP_DRBL_かつドリブル必殺技
        # commandが_CMD_SP_BLCK_かつシュート必殺技
        # commandが_CMD_SP_CTCH_かつシュート必殺技
        # commandが_CMD_SP_SHBL_かつシュートブロック必殺技
        # commandが_CMD_SP_BLBL_かつシュートブロック必殺技
        if ( command in [sub.Const._CMD_SP_SHOT_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_NS_, sub.Const._MV_LS_, sub.Const._MV_BS_, sub.Const._MV_SC_] ) or \
           ( command in [sub.Const._CMD_SP_DRBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_DR_] ) or \
           ( command in [sub.Const._CMD_SP_BLCK_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BL_, sub.Const._MV_BB_] ) or \
           ( command in [sub.Const._CMD_SP_CTCH_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_CA_, sub.Const._MV_P1_, sub.Const._MV_P2_] ) or \
           ( command in [sub.Const._CMD_SP_SHBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BS_] ) or \
           ( command in [sub.Const._CMD_SP_BLBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BB_] ):
            # 計算実行
            calcValue = calcTotalTechEx(targetStatus, position, command, moveList2, move)
            # 計算結果が既存の値を超過する場合、
            if move2TotalTech < calcValue:
                # トータルテクニックを保持
                move2TotalTech = calcValue
    # 必殺技1の戻り値が必殺技2より大きい値の場合
    if move1TotalTech >= move2TotalTech:
        return moveData1
    else:
        return moveData2


#--------------------------------------------------------------------------
# 引数に指定したコマンドにおいて、技1を与えた場合のトータルテクニックと
# 引数に指定したボーダーラインを比較し、期待値がボーダーライン以上の場合、trueを返す
# 同値となる場合、技1を優先する
# 引数
# targetStatus[0] : Lv1時のステータス
#             [1] : Lv99時のステータス,
#             [2] : 成長タイプ
#             [3] : 現在Lv時のステータス
# position        : 計算対象のポジション
# command         : 計算対象となるコマンド
# specialMoveList : 習得済必殺技リスト
# addMoveList     : 追加必殺技リスト
# borderValue       : トータルテクニックのボーダーライン
# 戻り値
# True  : 期待値がボーダーライン以上
# False : 期待値がボーダーライン未満
#--------------------------------------------------------------------------
def compBorderTotalTechEx(targetStatus, position, command, specialMoveList, addMoveList, borderValue):

    # 必殺技1計算用必殺技リストを作成
    calcMoveList = copy.deepcopy(specialMoveList)
    for moveCnt, move in enumerate(addMoveList):
        calcMoveList.append(move)
    # トータルテクニック計算
    totalTech = 0
    for moveCnt, move in enumerate(calcMoveList):
        # 比較対象コマンドの用途と合致する技のみ計算する
        # commandが_CMD_SP_SHOT_かつシュート必殺技
        # commandが_CMD_SP_DRBL_かつドリブル必殺技
        # commandが_CMD_SP_BLCK_かつシュート必殺技
        # commandが_CMD_SP_CTCH_かつシュート必殺技
        # commandが_CMD_SP_SHBL_かつシュートブロック必殺技
        # commandが_CMD_SP_BLBL_かつシュートブロック必殺技
        if ( command in [sub.Const._CMD_SP_SHOT_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_NS_, sub.Const._MV_LS_, sub.Const._MV_BS_, sub.Const._MV_SC_] ) or \
           ( command in [sub.Const._CMD_SP_DRBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_DR_] ) or \
           ( command in [sub.Const._CMD_SP_BLCK_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BL_, sub.Const._MV_BB_] ) or \
           ( command in [sub.Const._CMD_SP_CTCH_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_CA_, sub.Const._MV_P1_, sub.Const._MV_P2_] ) or \
           ( command in [sub.Const._CMD_SP_SHBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BS_] ) or \
           ( command in [sub.Const._CMD_SP_BLBL_] and move[sub.Const._MOVE_TYP_] in [sub.Const._MV_BB_] ):
            calcValue = calcTotalTechEx(targetStatus, position, command, calcMoveList, move)
            # 計算結果が既存の値を超過する場合、
            if totalTech < calcValue:
                # トータルテクニックを保持
                totalTech = calcTotalTechEx(targetStatus, position, command, calcMoveList, move)

    # トータルテクニック最大値がボーダーライン以上の場合
    if borderValue <= totalTech:
        return True
    else:
        return False


