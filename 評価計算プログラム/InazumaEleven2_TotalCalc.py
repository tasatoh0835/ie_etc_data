# _*_ coding: utf-8 _*_
#import io,sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import re
import configparser as ConfigParser
import copy
import csv
import sub

#--------------------------------------------------------------------------
# ステータス振り分け結果取得
#
# 引数
# playerStatus     : 計算対象選手ステータス
# trainingPosition : トレーニング方針(FW、MF、DF、GK)
# 戻り値
# retRowData:計算結果ステータス
#--------------------------------------------------------------------------
def getWriteData(playerStatus, trainingPosition):

    # 初期値設定
    retRowData = []
    
    # 計算に用いる列は読み取った値をそのまま設定
    for cnt in range(0, sub.Const._CLC_GP_):
        retRowData.append(playerStatus[cnt])
    # 計算結果を出力する列は0を設定
    for cnt in range(sub.Const._CLC_GP_, sub.Const._CLC_MAX_ROW_):
        retRowData.append(0)
    
    # GP,TP特訓
    retRowData[sub.Const._CLC_GP_] = int(playerStatus[sub.Const._GP_MAX_]) + sub.Const._CLC_GP_TP_VAL_
    retRowData[sub.Const._CLC_TP_] = int(playerStatus[sub.Const._TP_MAX_]) + sub.Const._CLC_GP_TP_VAL_
    
    # LvUP処理に必要な情報を取得
    # Lv1時のステータス,Lv99時のステータス,ステータスの成長タイプ,現在Lv時のステータス
    # ステータスは[トレーニング開始上限Lv,Kic,Bod,Con,Grd,Spe,Sta,Gut]の順
    targetStatus = [
                 # 最小Lvでのステータス用配列
                 [0,
                 int(playerStatus[sub.Const._KCK_MIN_]),
                 int(playerStatus[sub.Const._BDY_MIN_]),
                 int(playerStatus[sub.Const._CNT_MIN_]),
                 int(playerStatus[sub.Const._GRD_MIN_]),
                 int(playerStatus[sub.Const._SPD_MIN_]),
                 int(playerStatus[sub.Const._STM_MIN_]),
                 int(playerStatus[sub.Const._GUT_MIN_])],
                 # 最大Lvでのステータス用配列
                 [0,
                 int(playerStatus[sub.Const._KCK_MAX_]),
                 int(playerStatus[sub.Const._BDY_MAX_]),
                 int(playerStatus[sub.Const._CNT_MAX_]),
                 int(playerStatus[sub.Const._GRD_MAX_]),
                 int(playerStatus[sub.Const._SPD_MAX_]),
                 int(playerStatus[sub.Const._STM_MAX_]),
                 int(playerStatus[sub.Const._GUT_MAX_])],
                 # ステータスごとの成長タイプ用配列
                 [0,
                 int(playerStatus[sub.Const._KCK_TYP_]),
                 int(playerStatus[sub.Const._BDY_TYP_]),
                 int(playerStatus[sub.Const._CNT_TYP_]),
                 int(playerStatus[sub.Const._GRD_TYP_]),
                 int(playerStatus[sub.Const._SPD_TYP_]),
                 int(playerStatus[sub.Const._STM_TYP_]),
                 int(playerStatus[sub.Const._GUT_TYP_])],
                 # 現在ステータス格納用配列
                 [0,0,0,0,0,0,0,0]]
    # 必殺技リスト作成
    specialMoveList = []
    for moveCnt in range(4):
        # 技名、技種、威力、TP、属性
        # 技威力、消費TPはint型で格納
        specialMoveList.append( \
            [playerStatus[sub.Const._MV1_NAM_ + ( sub.Const._NEXT_MV_ * moveCnt )],
             playerStatus[sub.Const._MV1_TYP_ + ( sub.Const._NEXT_MV_ * moveCnt )],
             int(playerStatus[sub.Const._MV1_POW_ + ( sub.Const._NEXT_MV_ * moveCnt )]),
             int(playerStatus[sub.Const._MV1_CST_ + ( sub.Const._NEXT_MV_ * moveCnt )]),
             playerStatus[sub.Const._MV1_ELM_ + ( sub.Const._NEXT_MV_ * moveCnt )] ] )
    
    # 無印3版も作るかもしれないので
    # ノート使用有無を反映したステータスMAX値を取得
    potentialValue  = int(retRowData[sub.Const._TOT_VAL_])
    if bool(sub.Const._NOTE_USE_FLG_):
        # 使用済みの場合、のびしろにのびしろ加算値を加算
        potentialValue += sub.Const._NOTE_ADD_LIST_
    
    # ステータス配分リストのパターンだけ繰り返す
    for calcCnt, priorities in enumerate(sub.GlobalList.calcPriorities):
        # ステータス振り分け結果を現在ステータスとして取得
        targetStatus[sub.Const._CRNT_ROW_] = sub.StatusCalc.getTrainingResults(targetStatus, potentialValue, priorities, trainingPosition)
        # 振り分け結果を戻り値に格納
        for statusCnt, getStatus in enumerate(targetStatus[sub.Const._CRNT_ROW_]):
            retRowData[sub.Const._CLC1_TRAINING_LV_ + ( sub.Const._NEXT_CLC_ * calcCnt) + statusCnt] = getStatus
        # 装備上昇量を反映
        addStatus = getAddEquipStatus(retRowData[sub.Const._CLC_GP_], retRowData[sub.Const._CLC_TP_], targetStatus, trainingPosition)
        # GP,TP
        retRowData[sub.Const._CLC1_EQUIP_GP_ + ( sub.Const._NEXT_CLC_ * calcCnt)] = addStatus[0]
        retRowData[sub.Const._CLC1_EQUIP_TP_ + ( sub.Const._NEXT_CLC_ * calcCnt)] = addStatus[1]
        # キックからガッツ
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_KCK_] = addStatus[2]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_BDY_] = addStatus[3]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_CNT_] = addStatus[4]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_GRD_] = addStatus[5]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_SPD_] = addStatus[6]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_STM_] = addStatus[7]
        targetStatus[sub.Const._CRNT_ROW_][sub.Const._STATUS_ROW_GUT_] = addStatus[8]
        
        # 装備後ステータスを戻り値に格納
        for statusCnt, getStatus in enumerate(targetStatus[sub.Const._CRNT_ROW_]):
            if 0 == statusCnt:
                continue
            retRowData[sub.Const._CLC1_EQUIP_KCK_ + ( sub.Const._NEXT_CLC_ * calcCnt) + statusCnt - 1] = getStatus
        # ステータス、自力習得技、選手情報から 習得推奨必殺技とトータルテクニックの期待値を計算
        # 習得推奨必殺技1、習得推奨必殺技2、シュート、ドリブル、ブロック、キャッチ、競り合い1、競り合い2
        techData = getTotalTech(targetStatus[sub.Const._CRNT_ROW_], specialMoveList, \
                                playerStatus, trainingPosition, addStatus[1])
        # トータルテクニックを戻り値に格納
        for dataCnt, getData in enumerate(techData):
            retRowData[sub.Const._TT_MOVE1_ + ( sub.Const._NEXT_CLC_ * calcCnt) + dataCnt] = getData
    # 完了
    return retRowData


#--------------------------------------------------------------------------
# ステータスと自力習得技から 習得推奨必殺技とトータルテクニックの期待値を計算
# トータルテクニックは実数値ではなく期待値を返す
#
# 引数
# targetStatus      : 現在Lv時のステータス
# specialMoveList   : 自力習得必殺技リスト
# playerStatus      : 計算対象選手ステータス
# trainingPosition  : 育成ポジション
# maxTP             : 最大TP(必殺技習得判定に用いる)
# 戻り値
# retData:習得推奨必殺技1、習得推奨必殺技2、コマンド名、重要コマンド、ドリブル名、ドリブル、ブロック名、ブロック、ボールキープ、重要コマンドの消費TP
# 重要コマンドにはFW:シュート、MF:シュート、DF:シュートブロック(ブロック技)、GK:キャッチを返す
#--------------------------------------------------------------------------
def getTotalTech(targetStatus, specialMoveList, playerStatus, trainingPosition, maxTP):
    # 変数の初期化
    retData = ['','','',0,'',0,'',0,'',0,0]
    moveCnt = 0
    
    # 性別
    gender = playerStatus[sub.Const._PLY_GND_]
    # ポジション
    position = playerStatus[sub.Const._PLY_POS_]
    # 属性
    element = playerStatus[sub.Const._PLY_ELM_]
    
    # 保存済みの必殺技を反映
    for moveCnt in range(len(specialMoveList) - sub.Const._MOVE_CNT_):
        retData[moveCnt] = specialMoveList[sub.Const._MOVE_CNT_ + moveCnt][sub.Const._MOVE_NAM_]
    
    #----------------------------------------------------------------------------------------------
    # 秘伝書枠
    # 計算対象選手の秘伝書枠に余裕がある限り、習得技を追加する
    #----------------------------------------------------------------------------------------------
    #-共通処理(最優先)-----------------------------------------------------------------------------
    # 1.ちょうわざ！未習得の場合、ちょうわざ！を追加
    #----------------------------------------------------------------------------------------------
    if not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_BGMV_):
        # ちょうわざ！を秘伝書枠に追加
        specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_BGMV_))
        retData[sub.Const._MV1_NM_] = sub.Const._SKL_NM_BGMV_

    # ちょうわざ！習得有無チェック
    flgBGMV = sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_BGMV_)
    
    # セツヤク！習得有無チェック
    flgECO = sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_ECO_)
    
    # 選手情報に合致するデバフスキル取得
    debuffSkill = sub.MoveInfo.getDebuffSkill(gender)
    
    #----------------------------------------------------------------------------------------------
    # FWの習得優先順は以下の通り
    # 1.秘伝書枠に空きがある場合、「ボーダーライン判定」を行う
    # ●ボーダーライン判定
    # 「バランス型ネロのちょうわざ！＋キーパープラス＋時空の壁の期待値(430)」を「ボーダーライン」と定め、
    # スキルで自力習得技を補強するか、最強シュートを習得させるかの基準とする
    # ・秘伝書枠に空きがある場合、以下を行う
    #    ・シュートの期待値がBカテ特化ネロのちょうわざ！＋キーパープラス＋時空の壁の期待値(444)未満となっている場合に
    #    ・スキルで自力習得技を補強するか、最強シュートを習得させるかを判定する
    #      ・現在の習得必殺技でシュート期待値を下回る場合、以下を行う
    #        ・正規ポジションがFWかつSHP未習得の場合、以下を行う
    #          ・秘伝書枠にSHPを追加した場合のシュート期待値がボーダーライン以上の場合、SHPを習得
    #          ・秘伝書枠にSHPを追加した場合のシュート期待値がボーダーライン未満の場合、以下を行う
    #            ・秘伝書枠の空きが2つの場合、以下を行う
    #              ・デバフスキル習得許可フラグがTrueかつ、デバフスキル未習得の場合、以下を行う
    #                ・女性選手の場合、デバフスキルを追加する
    #                  ・スキルを追加した場合のシュート期待値がボーダーライン以上の場合、追加したスキルを習得
    #        ・正規ポジションがMF、DF、GK(SHP習得不可ポジション)の場合、以下を行う
    #          ・デバフスキル習得許可フラグがTrueかつ、デバフスキル未習得の場合、以下を行う
    #            ・女性選手の場合、デバフスキルを追加する
    #              ・スキルを追加した場合のシュート期待値がボーダーライン以上の場合、追加したスキルを習得
    #              ・秘伝書枠にデバフスキルを追加した場合のシュート期待値がボーダーライン未満の場合、以下を行う
    #                ・秘伝書枠の空きが2つの場合、以下を行う
    #                  ・デバフスキルとSHFを追加した場合のシュート期待値がボーダーライン以上の場合、デバフスキルとSHFを習得
    #            ・女性選手でない場合、以下を行う
    #              ・チェック対象の技にSHFを設定
    #          ・秘伝書枠の空きが1以上存在し、かつ、SHF未習得の場合、以下を行う
    #            ・SHFを追加した場合のシュート期待値がボーダーライン以上の場合、SHFを習得
    #      ・上記処理を経てもSHP、SHF、デバフスキルのいずれも付与できておらず、秘伝書枠に空きがある場合、最強シュート技を習得
    # 2.「秘伝書枠利用判定」を行う
    # ●秘伝書枠利用判定
    # 秘伝書枠に空きが存在する場合、FWとして有用な技を習得する
    # ・ブロック技習得判定
    #   ブロック技習得フラグがTrueかつ、自力習得ブロック技が0個かつ、秘伝書枠に空きがある場合、属性とTPに見合った最強ブロック技を習得
    # ・ドリブル技習得判定
    #   ドリブル技習得フラグがTrueかつ、自力習得ドリブル技が0個かつ、秘伝書枠に空きがある場合、属性とTPに見合った最強ドリブル技を習得
    # ・チーム強化スキル習得判定(SHP)
    #   FWかつSHP未習得かつ秘伝書枠に空きがある場合、SHPを習得
    # ・デバフスキル習得判定
    #   デバフスキル習得フラグがTrueかつ、デバフスキル未習得かつ、女性選手かつ、秘伝書枠に空きがある場合、デバフスキルを習得
    # ・チーム強化スキル習得判定(SHF)
    #   SHF未習得かつ秘伝書枠に空きがある場合、SHFを習得
    #----------------------------------------------------------------------------------------------
    if trainingPosition in [sub.Const._POS_FW_]:
        # ●ボーダーライン判定 start
        beforeMoveCnt = len(specialMoveList)
        # 秘伝書枠に空きがある場合
        if sub.Const._MOVE_CNT_ > beforeMoveCnt:
            # シュートの期待値がBカテ特化ネロのちょうわざ！＋キーパープラス＋時空の壁の期待値(444)未満となっている場合に
            # スキルで自力習得技を補強するか、最強シュートを習得させるかを判定する
            chkMoveList = []
            # ・現在の習得必殺技でシュート期待値を下回る場合、以下を行う
            if not sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                        chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                # ・正規ポジションがFWかつSHP未習得の場合、以下を行う
                if position in [sub.Const._POS_FW_] and not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHP_):
                    # チェック対象の技にSHPを設定
                    chkMoveList = [sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHP_)]
                    # ・秘伝書枠にSHPを追加した場合のシュート期待値がボーダーライン以上の場合、SHPを習得
                    if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                               chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                        # SHPを習得
                        for moveCnt, addMove in enumerate(chkMoveList):
                            specialMoveList.append(addMove)
                    # ・秘伝書枠にSHPを追加した場合のシュート期待値がボーダーライン未満の場合、以下を行う
                    #   ・秘伝書枠の空きが2つの場合、以下を行う
                    elif 2 == ( sub.Const._MOVE_CNT_ - len(specialMoveList) ):
                        # ・デバフスキル習得許可フラグがTrueかつ、デバフスキル未習得の場合、以下を行う
                        if sub.Const._USE_HIDEN_CHARM_UP_ and not sub.MoveInfo.srchMoveName(specialMoveList, debuffSkill[sub.Const._MOVE_NAM_]):
                            # ・女性選手の場合、デバフスキルを追加する
                            if gender in [sub.Const._GND_FEMALE_]:
                                # デバフスキルを追加
                                chkMoveList.append(debuffSkill)
                                # ・スキルを追加した場合のシュート期待値がボーダーライン以上の場合、追加したスキルを習得
                                if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                                           chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                                    # SHPとデバフスキルを習得
                                    for moveCnt, addMove in enumerate(chkMoveList):
                                        specialMoveList.append(addMove)
                # ・正規ポジションがMF、DF、GK(SHP習得不可ポジション)の場合、以下を行う
                elif position in [sub.Const._POS_MF_, sub.Const._POS_DF_, sub.Const._POS_GK_]:
                    # ・デバフスキル習得許可フラグがTrueかつ、デバフスキル未習得の場合、以下を行う
                    if sub.Const._USE_HIDEN_CHARM_UP_ and not sub.MoveInfo.srchMoveName(specialMoveList, debuffSkill[sub.Const._MOVE_NAM_]):
                        # ・女性選手の場合、デバフスキルを追加する
                        if gender in [sub.Const._GND_FEMALE_]:
                            # デバフスキルを追加
                            chkMoveList.append(debuffSkill)
                            # ・スキルを追加した場合のシュート期待値がボーダーライン以上の場合、追加したスキルを習得
                            if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                                       chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                                # 追加したスキルを習得
                                for moveCnt, addMove in enumerate(chkMoveList):
                                    specialMoveList.append(addMove)
                            # ・秘伝書枠にデバフスキルを追加した場合のシュート期待値がボーダーライン未満の場合、以下を行う
                            #   ・秘伝書枠の空きが2つの場合、以下を行う
                            elif 2 == ( sub.Const._MOVE_CNT_ - len(specialMoveList) ):
                                if not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHF_):
                                    # チェック対象の技にSHFを設定
                                    chkMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHF_))
                                    # ・デバフスキルとSHFを追加した場合のシュート期待値がボーダーライン以上の場合、デバフスキルとSHFを習得
                                    if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                                               chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                                        # デバフスキル、SHFを習得
                                        for moveCnt, addMove in enumerate(chkMoveList):
                                            specialMoveList.append(addMove)
                        # ・女性選手でない場合、以下を行う
                        else:
                            # チェック対象の技にSHFを設定
                            chkMoveList = [sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHF_)]
                            # ・SHFを追加した場合のシュート期待値がボーダーライン以上の場合、SHFを習得
                            if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                                       chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                                # SHFを習得
                                for moveCnt, addMove in enumerate(chkMoveList):
                                    specialMoveList.append(addMove)
                        # チェック対象とした技をクリア
                        chkMoveList = []
                    # ・秘伝書枠の空きが1以上存在し、かつ、SHF未習得の場合、以下を行う
                    if sub.Const._MOVE_CNT_ > len(specialMoveList) and not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHF_):
                        # チェック対象の技にSHFを設定
                        chkMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHF_))
                        # ・SHFを追加した場合のシュート期待値がボーダーライン以上の場合、SHFを習得
                        if sub.TotalTechCalc.compBorderTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_SHOT_, specialMoveList, \
                                                                   chkMoveList, sub.Const._RET_SHOT_LOWER_LIMIT_):
                                # SHFを習得
                                for moveCnt, addMove in enumerate(chkMoveList):
                                    specialMoveList.append(addMove)
                # ・上記処理を経てもSHP、SHF、デバフスキルのいずれも付与できておらず、秘伝書枠に空きがある場合、最強シュート技を習得
                if sub.Const._MOVE_CNT_ > len(specialMoveList) and beforeMoveCnt == len(specialMoveList):
                    specialMoveList.append(sub.MoveInfo.getStrongestShot(element, maxTP, flgBGMV, flgECO))
        # ボーダーライン判定 end
        
        # 秘伝書枠利用判定 start
        # ・ブロック技習得判定
        #   ブロック技習得フラグがTrueかつ、自力習得ブロック技が0個かつ、秘伝書枠に空きがある場合、属性とTPに見合った最強ブロック技を習得
        if sub.Const._USE_HIDEN_BLOCK_ and (not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_BL_) and not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_BB_)) and \
           sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 属性とTPに見合った最強ブロック技を習得
            specialMoveList.append(sub.MoveInfo.getStrongestBlock(element, gender, maxTP, flgBGMV, flgECO))
        # ・ドリブル技習得判定
        #   ドリブル技習得フラグがTrueかつ、自力習得ドリブル技が0個かつ、秘伝書枠に空きがある場合、属性とTPに見合った最強ドリブル技を習得
        if sub.Const._USE_HIDEN_DRIBBLE_ and not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_DR_) and \
           sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 属性とTPに見合った最強ブロック技を習得
            specialMoveList.append(sub.MoveInfo.getStrongestDribble(element, maxTP, flgBGMV, flgECO))
        # ・チーム強化スキル習得判定(SHP)
        #   FWかつSHP未習得かつ秘伝書枠に空きがある場合、SHPを習得
        if position in [sub.Const._POS_FW_] and not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHP_) and \
           sub.Const._MOVE_CNT_ > len(specialMoveList):
            # SHPを習得
            specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHP_))
        # ・デバフスキル習得判定
        #   デバフスキル習得フラグがTrueかつ、デバフスキル未習得かつ、女性選手かつ、秘伝書枠に空きがある場合、デバフスキルを習得
        if sub.Const._USE_HIDEN_CHARM_UP_ and not sub.MoveInfo.srchMoveName(specialMoveList, debuffSkill[sub.Const._MOVE_NAM_]) and \
           gender in [sub.Const._GND_FEMALE_] and sub.Const._MOVE_CNT_ > len(specialMoveList):
            specialMoveList.append(debuffSkill)
        # ・チーム強化スキル習得判定(SHF)
        #   SHF未習得かつ秘伝書枠に空きがある場合、SHFを習得
        if not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_SHF_) and \
           sub.Const._MOVE_CNT_ > len(specialMoveList):
            # SHFを習得
            specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_SHF_))
        # 秘伝書枠利用判定 end
    #----------------------------------------------------------------------------------------------
    # MFの習得優先順は以下の通り
    # 1.秘伝書枠に空きがある場合、以下を行う
    #   1-1.ドリブル技未習得の場合、または習得するドリブル技がジャッジスルー系のみの場合、条件に合致する最強ドリブル技を習得する
    # 2.秘伝書枠に空きがある場合、以下を行う
    #   2-1.ブロック技未習得の場合、条件に合致する最強ブロック技を習得する
    # 3.秘伝書枠に空きがある場合、以下を行う
    #   3-1.OFF未習得かつ、秘伝書枠に空きがある場合、OFFを追加
    # 4.秘伝書枠に空きがある場合、以下を行う
    #   4-1.DFF未習得かつ、秘伝書枠に空きがある場合、DFFを追加
    #----------------------------------------------------------------------------------------------
    if trainingPosition in [sub.Const._POS_MF_]:
        # 習得枠に空きがある場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 習得技にドリブル技が存在しない場合、またはジャッジスルー系の技のみ習得している場合
            if not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_DR_) or \
               not sub.MoveInfo.srchJudgeThrough(specialMoveList):
                # 条件に合致する最強ドリブル技を秘伝書枠に追加
                specialMoveList.append(sub.MoveInfo.getStrongestDribble(element, maxTP, flgBGMV, flgECO))
        # 習得枠に空きがある場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 習得技にブロック技が存在しない場合、
            if not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_BL_) and not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._MV_BB_):
                # 条件に合致する最強ブロック技を秘伝書枠に追加
                specialMoveList.append(sub.MoveInfo.getStrongestBlock(element, gender, maxTP, flgBGMV, flgECO))
        # 習得枠に空きがある場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # OFF習得フラグがTrueかつ、習得技にOFFが存在しない場合、
            if sub.Const._USE_HIDEN_OFF_ and not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._SKL_NM_OFF_):
                # OFFを習得
                specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_OFF_))
        # 習得枠に空きがある場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # DFF習得フラグがTrueかつ、習得技にDFFが存在しない場合、
            if sub.Const._USE_HIDEN_DFF_ and not sub.MoveInfo.srchMoveType(specialMoveList, sub.Const._SKL_NM_DFF_):
                # DFFを習得
                specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_DFF_))
    
    #----------------------------------------------------------------------------------------------
    # DFの習得優先順は以下の通り
    # 1.秘伝書枠に空きがある場合、以下を行う
    #   1-1.デバフスキルを付与した場合と条件に合致する最強シュートブロックを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    # 2.秘伝書枠に空きがあり、デバフスキルを未習得の場合、以下を行う
    #   2-1.デバフスキルを付与した場合と条件に合致する最強シュートブロックを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    #----------------------------------------------------------------------------------------------
    if trainingPosition in [sub.Const._POS_DF_]:
        # 秘伝書枠に空きが存在する場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 条件に合致する最強シュートブロックを取得
            strongestMove = sub.MoveInfo.getStrongestShotBlock(element, playerStatus[sub.Const._PLY_NNM_], maxTP, flgBGMV, flgECO)
            # デバフスキルを取得
            if not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CHRM_) and gender in [sub.Const._GND_FEMALE_]:
                # 女性選手の場合、お色気ＵＰ！を習得
                debuffSkill = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CHRM_)
            else:
                # イケメンＵＰ！を習得
                debuffSkill = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_COOL_)
            
            # 最強シュートブロックとデバフスキルのシュートブロック期待値が高くなる方を秘伝書枠に追加
            specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_BLBL_, specialMoveList, \
                                                                     debuffSkill, strongestMove))
        # 秘伝書枠に空きが存在し、デバフスキルを未習得の場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList) and \
           not (sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CHRM_) or sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_COOL_)):
            # 条件に合致する最強シュートブロックを取得
            strongestMove = sub.MoveInfo.getStrongestShotBlock(element, playerStatus[sub.Const._PLY_NNM_], maxTP, flgBGMV, flgECO)
            # デバフスキルを取得
            if not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CHRM_) and gender in [sub.Const._GND_FEMALE_]:
                # 女性選手の場合、お色気ＵＰ！を習得
                debuffSkill = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CHRM_)
            else:
                # イケメンＵＰ！を習得
                debuffSkill = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_COOL_)
            
            # 最強シュートブロックとデバフスキルのシュートブロック期待値が高くなる方を秘伝書枠に追加
            specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_BLBL_, specialMoveList, \
                                                                     debuffSkill, strongestMove))
    
    #----------------------------------------------------------------------------------------------
    # GKの習得優先順は以下の通り
    # 1.秘伝書枠に空きがある場合、以下を行う
    #   1-1.GKP未習得かつ、正規ポジションがGKの場合
    #       GKPを付与した場合と条件に合致する最強キャッチを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    #   1-2.上記以外の場合
    #       クリティカル！を付与した場合と条件に合致する最強キャッチを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    # 2.秘伝書枠に空きがある場合、以下を行う
    #   2-1.GKP未習得かつ、正規ポジションがGKの場合
    #       GKPを付与した場合と条件に合致する最強キャッチを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    #   2-2.上記以外の場合
    #       クリティカル！を付与した場合と条件に合致する最強キャッチを習得させた場合のトータルテクニックを比較し、期待値が高くなる方を習得する
    #----------------------------------------------------------------------------------------------
    if trainingPosition in [sub.Const._POS_GK_]:
        # スキルで自力習得技を強化すべきか、必殺技を習得するべきかの判定
        # GKP追加フラグがTrueかつ、秘伝書枠に空きが存在する場合
        if sub.Const._USE_HIDEN_GKP_ and sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 正規ポジションがGKかつ、GKP未習得の場合
            if position in [sub.Const._POS_GK_] and not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_GKP_):
                # 条件に合致する最強キャッチを取得
                strongestMove = sub.MoveInfo.getStrongestCatch(element, maxTP, flgBGMV, flgECO)
                # 最強キャッチとGKPのキャッチの期待値が高くなる方を秘伝書枠に追加
                specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_CTCH_, specialMoveList, \
                                                                         sub.MoveInfo.getSkillData(sub.Const._SKL_NM_GKP_), strongestMove))
            # 上記以外の場合
            else:
                # 条件に合致する最強キャッチを取得
                strongestMove = sub.MoveInfo.getStrongestCatch(element, maxTP, flgBGMV, flgECO)
                # 最強キャッチとクリティカル！のキャッチの期待値が高くなる方を秘伝書枠に追加
                specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_CTCH_, specialMoveList, \
                                                                         sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CRTC_), strongestMove))
        # 秘伝書枠に空きが存在する場合
        if sub.Const._MOVE_CNT_ > len(specialMoveList):
            # 正規ポジションがGKかつ、GKP未習得の場合
            if position in [sub.Const._POS_GK_] and not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_GKP_):
                # 条件に合致する最強キャッチを取得
                strongestMove = sub.MoveInfo.getStrongestCatch(element, maxTP, flgBGMV, flgECO)
                # 最強キャッチとGKPのキャッチの期待値が高くなる方を秘伝書枠に追加
                specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_CTCH_, specialMoveList, \
                                                                         sub.MoveInfo.getSkillData(sub.Const._SKL_NM_GKP_), strongestMove))
            # 上記以外の場合
            elif position not in [sub.Const._POS_GK_]:
                # 条件に合致する最強キャッチを取得
                strongestMove = sub.MoveInfo.getStrongestCatch(element, maxTP, flgBGMV, flgECO)
                # 最強キャッチとクリティカル！のキャッチの期待値が高くなる方を秘伝書枠に追加
                specialMoveList.append(sub.TotalTechCalc.compTotalTechEx(targetStatus, trainingPosition, sub.Const._CMD_SP_CTCH_, specialMoveList, \
                                                                         sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CRTC_), strongestMove))
    
    #-共通処理-------------------------------------------------------------------------------------
    # 1.クリティカル！未習得かつ、秘伝書枠に空きがある場合、クリティカル！を追加
    # 2.ラッキー！未習得かつ、秘伝書枠に空きがある場合、ラッキー！を追加
    #----------------------------------------------------------------------------------------------
    # 秘伝書枠にまだ空きが存在し、クリティカル！習得フラグがTrueかつ、クリティカル未習得の場合
    if sub.Const._USE_HIDEN_CRTC_ and sub.Const._MOVE_CNT_ > len(specialMoveList) and \
       not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_CRTC_):
        # クリティカル！を習得
        specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CRTC_))
    
    # 秘伝書枠にまだ空きが存在し、ラッキー！習得フラグがTrueかつ、ラッキー！未習得の場合
    if sub.Const._USE_HIDEN_LCKY_ and sub.Const._MOVE_CNT_ > len(specialMoveList) and \
       not sub.MoveInfo.srchMoveName(specialMoveList, sub.Const._SKL_NM_LCKY_):
        # ラッキー！を習得
        specialMoveList.append(sub.MoveInfo.getSkillData(sub.Const._SKL_NM_LCKY_))
    
    #----------------------------------------------------------------------------------------------
    # 戻り値設定
    #----------------------------------------------------------------------------------------------
    # 秘伝書技名設定
    retData[0] = specialMoveList[len(specialMoveList) - 2][sub.Const._MOVE_NAM_]
    retData[1] = specialMoveList[len(specialMoveList) - 1][sub.Const._MOVE_NAM_]
    
    #----------------------------------------------------------------------------------------------
    # 通常コマンドバトル
    #----------------------------------------------------------------------------------------------
    # 育成ポジションがFWの場合、シュート、ドリブル、ブロック、ボールキープを計算
    if trainingPosition in [sub.Const._POS_FW_]:
        commandList = sub.Const._FW_COMMAND_LIST_
    # 育成ポジションがMFの場合、シュート、ドリブル、ブロック、ボールキープを計算
    elif trainingPosition in [sub.Const._POS_MF_]:
        commandList = sub.Const._MF_COMMAND_LIST_
    # 育成ポジションがDFの場合、シュートブロック、ドリブル、ブロック、ボールキープを計算
    # シュートブロックは通常コマンドバトルでは選択できないため、計算除外対象
    elif trainingPosition in [sub.Const._POS_DF_]:
        commandList = sub.Const._DF_COMMAND_LIST_
    # 育成ポジションがGKの場合、キャッチ、ドリブル、ブロック、ボールキープを計算
    else:
        commandList = sub.Const._GK_COMMAND_LIST_
    # 通常コマンドの期待値計算
    for commandCnt, command in enumerate(commandList):
        retData[commandCnt * 2 + 2] = '-'
        retData[commandCnt * 2 + 3] = \
            sub.TotalTechCalc.calcTotalTechEx(targetStatus, trainingPosition, command, specialMoveList, None)
    
    #----------------------------------------------------------------------------------------------
    # 必殺技使用時のコマンドバトル
    #----------------------------------------------------------------------------------------------
    for commandCnt, moveData in enumerate(specialMoveList):
        # トータルテクニック計算結果のストック先取得
        calcDataList = sub.TotalTechCalc.getTotalTechStockRow(trainingPosition, moveData[sub.Const._MOVE_TYP_])
        # ストック先の数だけ計算を実施
        for calcCnt, calcData in enumerate(calcDataList):
            # 計算対象外の場合、処理を行わない
            if calcData[0] in [sub.Const._CMD_PASS_]:
                continue
            # 必殺技の期待値を取得
            calcForm = sub.TotalTechCalc.calcTotalTechEx(targetStatus, trainingPosition, calcData[0], specialMoveList, moveData)
            # 期待値が既存の保持値を上回っている場合
            if retData[calcData[1]] <= calcForm:
                # 技名、取得した期待値を該当コマンドの戻り値に設定
                retData[calcData[1] - 1] = moveData[sub.Const._MOVE_NAM_]
                retData[calcData[1]] = calcForm
                # 育成タイプがFW、MF、GKかつ、格納先が重要コマンドの場合、
                # または、育成タイプがMFの場合のみ、ドリブル技の場合に消費TPを更新
                if ( trainingPosition in [sub.Const._POS_FW_] and sub.Const._RET_SHOT_ == calcData[1] ) or \
                   ( trainingPosition in [sub.Const._POS_MF_] and sub.Const._RET_DRBL_ == calcData[1] ) or \
                   ( trainingPosition in [sub.Const._POS_DF_] and sub.Const._RET_BLCK_ == calcData[1] ) or \
                   ( trainingPosition in [sub.Const._POS_GK_] and sub.Const._RET_CTCH_ == calcData[1] ):
                    retData[sub.Const._RET_COST_] = int(int(moveData[sub.Const._MOVE_CST_] * sub.Const._SKL_BGMV_COST_ / 100) * \
                                                           ((sub.Const._SKL_ECO_ if flgECO else 100) / 100 ) )
    # 戻り値を返す
    return retData


#--------------------------------------------------------------------------
# 取得したステータスに装備品での上昇分を付与
# 引数
# GP              : 装備反映前のGP
# TP              : 装備反映前のTP
# targetStatus[0] : Lv1時のステータス
#             [1] : Lv99時のステータス,
#             [2] : 成長タイプ
#             [3] : 現在Lv時のステータス
# trainingPosition: 育成方針(ポジション)
# 戻り値
# retStatus : 装備反映後のGP、TP、ステータス
#--------------------------------------------------------------------------
def getAddEquipStatus(GP, TP, targetStatus, trainingPosition):
    # 装備反映前ステータスを取得
    retStatus = copy.deepcopy(targetStatus[sub.Const._CRNT_ROW_])
    # 不要な部分(レベル)を除去
    del retStatus[0]
    # 配列先頭にGP、TPを追加
    retStatus.insert(0, GP)
    retStatus.insert(1, TP)
    
    # ポジションに合致する装備品名を取得
    if trainingPosition in [sub.Const._POS_FW_]:
        spikeName   = sub.Const._FW_SPIKE_
        misangaName = sub.Const._FW_MISANGA_
        pendantName = sub.Const._FW_PENDANT_
        groveName   = sub.Const._FW_GROVE_
    elif trainingPosition in [sub.Const._POS_MF_]:
        spikeName   = sub.Const._MF_SPIKE_
        misangaName = sub.Const._MF_MISANGA_
        pendantName = sub.Const._MF_PENDANT_
        groveName   = sub.Const._MF_GROVE_
    elif trainingPosition in [sub.Const._POS_DF_]:
        spikeName   = sub.Const._DF_SPIKE_
        misangaName = sub.Const._DF_MISANGA_
        pendantName = sub.Const._DF_PENDANT_
        groveName   = sub.Const._DF_GROVE_
    elif trainingPosition in [sub.Const._POS_GK_]:
        spikeName   = sub.Const._GK_SPIKE_
        misangaName = sub.Const._GK_MISANGA_
        pendantName = sub.Const._GK_PENDANT_
        groveName   = sub.Const._GK_GROVE_

    # ADD_VALUE
    addValueList = [0,0,0,0,0,0,0,0,0]
    
    # スパイク
    equipAddStatus = [0,0,0,0,0,0,0,0,0]
    # 装備品名に合致する情報を取得
    for cnt in range(len(sub.Const._SPIKE_LIST_)):
        if sub.Const._SPIKE_LIST_[cnt][sub.Const._EQUIP_NAME_] in [spikeName]:
            equipAddStatus = sub.Const._SPIKE_LIST_[cnt][sub.Const._EQUIP_STATUS_]
            break
    # 装備品の上昇値反映
    for cnt, equipVal in enumerate(equipAddStatus):
        addValueList[cnt] += equipVal
    
    # ミサンガ
    equipAddStatus = [0,0,0,0,0,0,0,0,0]
    # 装備品名に合致する情報を取得
    for cnt in range(len(sub.Const._MISANGA_LIST_)):
        if sub.Const._MISANGA_LIST_[cnt][sub.Const._EQUIP_NAME_] in [misangaName]:
            equipAddStatus = sub.Const._MISANGA_LIST_[cnt][sub.Const._EQUIP_STATUS_]
            break
    # 装備品の上昇値取得
    for cnt, equipVal in enumerate(equipAddStatus):
        addValueList[cnt] += equipVal
    
    # ペンダント
    equipAddStatus = [0,0,0,0,0,0,0,0,0]
    # 装備品名に合致する情報を取得
    for cnt in range(len(sub.Const._PENDANT_LIST_)):
        if sub.Const._PENDANT_LIST_[cnt][sub.Const._EQUIP_NAME_] in [pendantName]:
            equipAddStatus = sub.Const._PENDANT_LIST_[cnt][sub.Const._EQUIP_STATUS_]
            break
    # 装備品の上昇値取得
    for cnt, equipVal in enumerate(equipAddStatus):
        addValueList[cnt] += equipVal
    
    # グローブ
    equipAddStatus = [0,0,0,0,0,0,0,0,0]
    # 装備品名に合致する情報を取得
    for cnt in range(len(sub.Const._GROVE_LIST_)):
        if sub.Const._GROVE_LIST_[cnt][sub.Const._EQUIP_NAME_] in [groveName]:
            equipAddStatus = sub.Const._GROVE_LIST_[cnt][sub.Const._EQUIP_STATUS_]
            break
    # 装備品の上昇値取得
    for cnt, equipVal in enumerate(equipAddStatus):
        addValueList[cnt] += equipVal
    
    # 上昇値をステータスに反映
    for cnt, addValue in enumerate(addValueList):
        retStatus[cnt] += addValue
    
    # ステータスを返す
    return retStatus


#--------------------------------------------------------------------------
# メイン処理
#--------------------------------------------------------------------------
# 選手ステータス情報読み込み
playersList = sub.CsvControl.getFileDataList(".\\data\\status_list.csv")
# 成長補正データ読み込み
sub.GlobalList.typeList = sub.CsvControl.getFileDataList(".\\data\\type_list.csv")
# 必殺技データ読み込み
sub.GlobalList.moveList = sub.CsvControl.getFileDataList(".\\data\\move_list.csv")
# LvUP時上昇ステータスの優先順をカテゴリ化した優先順リスト
# 上昇ステータスの優先順はスタミナ→ガッツ→スピード→コントロール→ガード→ボディ→キック
sub.GlobalList.lvUpStatusList = [
                   sub.Const._STATUS_ROW_STM_, 
                   sub.Const._STATUS_ROW_GUT_, 
                   sub.Const._STATUS_ROW_SPD_, 
                   sub.Const._STATUS_ROW_CNT_, 
                   sub.Const._STATUS_ROW_GRD_, 
                   sub.Const._STATUS_ROW_BDY_, 
                   sub.Const._STATUS_ROW_KCK_]

print("===== STATUS CALC START    ======")

# FW計算
# ステータス配分の優先順リストをFW用に設定
sub.GlobalList.calcPriorities = sub.CalcPriority.getCalcPriorityList(sub.Const._POS_FW_)

keyman = "キーマン指定なし"
# キーマン取得
if sub.Const._KEYMAN_ in [sub.Const._KEYMAN_FW_]:
    keyman = "キーマン FW"
elif sub.Const._KEYMAN_ in [sub.Const._KEYMAN_MF_]:
    keyman = "キーマン MF"
elif sub.Const._KEYMAN_ in [sub.Const._KEYMAN_DF_]:
    keyman = "キーマン DF"
elif sub.Const._KEYMAN_ in [sub.Const._KEYMAN_GK_]:
    keyman = "キーマン GK"

print("===== STATUS CALC FW START ======")
with open(sub.Const._OutputFilePathFW_, "w", encoding="shift_jis", newline="") as file:
    writer = csv.writer(file)
    
    # ヘッダ部取得
    headerList = sub.CsvControl.getHeader()
    # ヘッダ部変換(FW用に一部項目の文字列を変換)
    headerList[0] = [s.replace('キーマン', keyman) for s in headerList[0]]
    headerList[1] = [s.replace('育成タイプ1', 'バランス型FW') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ2', '競り合い型FW') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ3', 'シュート特化FW') for s in headerList[1]]
    headerList[2] = [s.replace('最重要コマンド', 'シュート') for s in headerList[2]]
    # ヘッダ部書き込み
    for cnt, header in enumerate(headerList):
        writer.writerow(header)
    
    # playerListの数だけ繰り返し
    for playerCnt, playerStatus in enumerate(playersList): 
        # No列が数値でないデータは処理対象外
        if bool(re.match('^[^0-9]{1}', playerStatus[sub.Const._PLY_NUM_])):
            continue
        # 選手データから計算結果を取得
        rowData = getWriteData(playerStatus, sub.Const._POS_FW_)
        for rowCnt, data in enumerate(rowData):
            rowData[rowCnt] = data
        # 計算結果をcsvに書き込み
        writer.writerow(rowData)
    
print("===== STATUS CALC FW END   ======")

# MF計算
# ステータス配分の優先順リストをMF用に設定
sub.GlobalList.calcPriorities = sub.CalcPriority.getCalcPriorityList(sub.Const._POS_MF_)

print("===== STATUS CALC MF START ======")
with open(sub.Const._OutputFilePathMF_, "w", encoding="shift_jis", newline="") as file:
    writer = csv.writer(file)
    
    # ヘッダ部取得
    headerList = sub.CsvControl.getHeader()
    # ヘッダ部変換(FW用に一部項目の文字列を変換)
    headerList[0] = [s.replace('キーマン', keyman) for s in headerList[0]]
    headerList[1] = [s.replace('育成タイプ1', 'バランス型MF') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ2', 'Bカテ特化型MF') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ3', 'ドリブル特化型MF') for s in headerList[1]]
    headerList[2] = [s.replace('最重要コマンド', 'シュート') for s in headerList[2]]
    headerList[2] = [s.replace('シュート消費TP量', 'ドリブル消費TP量') for s in headerList[2]]
    
    # ヘッダ部書き込み
    for cnt, header in enumerate(headerList):
        writer.writerow(header)
    
    # playerListの数だけ繰り返し
    for playerCnt, playerStatus in enumerate(playersList): 
        # No列が数値でないデータは処理対象外
        if bool(re.match('^[^0-9]{1}', playerStatus[sub.Const._PLY_NUM_])):
            continue
        # 選手データから計算結果を取得
        rowData = getWriteData(playerStatus, sub.Const._POS_MF_)
        for rowCnt, data in enumerate(rowData):
            rowData[rowCnt] = data
        # 計算結果をcsvに書き込み
        writer.writerow(rowData)
    
print("===== STATUS CALC MF END   ======")

# DF計算
# ステータス配分の優先順リストをDF用に設定
sub.GlobalList.calcPriorities = sub.CalcPriority.getCalcPriorityList(sub.Const._POS_DF_)

print("===== STATUS CALC DF START ======")
with open(sub.Const._OutputFilePathDF_, "w", encoding="shift_jis", newline="") as file:
    writer = csv.writer(file)
    
    # ヘッダ部取得
    headerList = sub.CsvControl.getHeader()
    # ヘッダ部変換(FW用に一部項目の文字列を変換)
    headerList[0] = [s.replace('キーマン', keyman) for s in headerList[0]]
    headerList[1] = [s.replace('育成タイプ1', 'バランス型DF') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ2', 'Bカテ特化型DF') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ3', 'シュートブロック特化型DF') for s in headerList[1]]
    headerList[2] = [s.replace('最重要コマンド', 'シュートブロック') for s in headerList[2]]
    # ヘッダ部書き込み
    for cnt, header in enumerate(headerList):
        writer.writerow(header)
    
    # playerListの数だけ繰り返し
    for playerCnt, playerStatus in enumerate(playersList): 
        # No列が数値でないデータは処理対象外
        if bool(re.match('^[^0-9]{1}', playerStatus[sub.Const._PLY_NUM_])):
            continue
        # 選手データから計算結果を取得
        rowData = getWriteData(playerStatus, sub.Const._POS_DF_)
        for rowCnt, data in enumerate(rowData):
            rowData[rowCnt] = data
        # 計算結果をcsvに書き込み
        writer.writerow(rowData)
    
print("===== STATUS CALC DF END   ======")

# GK計算
# ステータス配分の優先順リストをGK用に設定
sub.GlobalList.calcPriorities = sub.CalcPriority.getCalcPriorityList(sub.Const._POS_GK_)

print("===== STATUS CALC GK START ======")
with open(sub.Const._OutputFilePathGK_, "w", encoding="shift_jis", newline="") as file:
    writer = csv.writer(file)
    
    # ヘッダ部取得
    headerList = sub.CsvControl.getHeader()
    # ヘッダ部変換(FW用に一部項目の文字列を変換)
    headerList[0] = [s.replace('キーマン', keyman) for s in headerList[0]]
    headerList[1] = [s.replace('育成タイプ1', 'バランス型GK') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ2', 'Bカテ特化型GK') for s in headerList[1]]
    headerList[1] = [s.replace('育成タイプ3', 'キャッチ特化型GK') for s in headerList[1]]
    headerList[2] = [s.replace('最重要コマンド', 'キャッチ') for s in headerList[2]]
    # ヘッダ部書き込み
    for cnt, header in enumerate(headerList):
        writer.writerow(header)
    
    # playerListの数だけ繰り返し
    for playerCnt, playerStatus in enumerate(playersList): 
        # No列が数値でないデータは処理対象外
        if bool(re.match('^[^0-9]{1}', playerStatus[sub.Const._PLY_NUM_])):
            continue
        # 選手データから計算結果を取得
        rowData = getWriteData(playerStatus, sub.Const._POS_GK_)
        for rowCnt, data in enumerate(rowData):
            rowData[rowCnt] = data
        # 計算結果をcsvに書き込み
        writer.writerow(rowData)
    
print("===== STATUS CALC GK END   ======")

print("===== STATUS CALC END      ======")
