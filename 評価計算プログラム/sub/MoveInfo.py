import sub.Const
import re

#--------------------------------------------------------------------------
# 技の習得有無チェック
# 引数    moveList     : 習得技リスト
#         moveName     : チェック対象技名
# 戻り値
#         True         : 習得
#         False        : 未習得
#--------------------------------------------------------------------------
def srchMoveName(moveList, moveName):
    # 習得技の数だけ繰り返す
    for moveCnt, chkData in enumerate(moveList):
        # 習得技名がリストに含まれている場合
        if 0 < len(re.findall(moveName, chkData[sub.Const._MOVE_NAM_])):
            # Trueを返す
            return True
    # 習得技に技名が含まれていない場合、Falseを返す
    return False


#--------------------------------------------------------------------------
# 技の習得有無チェック
# 引数    moveList     : 習得技リスト
#         moveType     : チェック対象技種
#                      : 例) sub.Const._MV_NS_ … シュート
# 戻り値
#         True         : 習得
#         False        : 未習得
#--------------------------------------------------------------------------
def srchMoveType(moveList, moveType):
    # 習得技の数だけ繰り返す
    for moveCnt, chkData in enumerate(moveList):
        # チェック対象技種がリストに含まれている場合
        if 0 < len(re.findall(moveType, chkData[sub.Const._MOVE_TYP_])):
            # Trueを返す
            return True
    # 習得技に技名が含まれていない場合、Falseを返す
    return False


#--------------------------------------------------------------------------
# スキル情報を返す
# 引数
# skillName  : スキル名
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getSkillData(skillName):
    # 引数名のスキルを技データの形にして返す
    return [skillName, sub.Const._MV_SKL_, 0, 0, '']


#--------------------------------------------------------------------------
# シグマゾーンを返す
# 引数
# element  : 選手の属性
# 戻り値
# moveData : 必殺技情報(お色気UP！)
#--------------------------------------------------------------------------
def getSigmaZone(element):
    # シグマゾーン
    moveData = ['シグマゾーン','BL', 104, 32, '']
    # 林属性の場合
    if element in [sub.Const._ELE_WO_]:
        # 一致を付与
        moveData[sub.Const._MOVE_ELE_] = '一致'
    # 必殺技情報を返す
    return moveData


#--------------------------------------------------------------------------
# 性別に合致するデバフスキルを返す
# 引数    gender     : 性別
# 戻り値  moveData   : デバフスキル
# 性別がない選手の場合、Noneを返す
#--------------------------------------------------------------------------
def getDebuffSkill(gender):
    moveData = None
    #女性選手の場合
    if gender in [sub.Const._GND_FEMALE_]:
        # 女性選手の場合、お色気ＵＰ！を習得
        moveData = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_CHRM_)
    elif gender in [sub.Const._GND_MALE_]:
        # 男性選手の場合、イケメンＵＰ！を習得
        moveData = sub.MoveInfo.getSkillData(sub.Const._SKL_NM_COOL_)
    # 引数名のスキルを技データの形にして返す
    return moveData


#--------------------------------------------------------------------------
# 巨体用必殺技の習得可否チェック
# 引数    playerName   : 対象者名
# 戻り値
#         True         : 習得可能
#         False        : 習得不可
#--------------------------------------------------------------------------
def chkLargeMove(playerName):
    # 習得技の数だけ繰り返す
    for moveCnt, chkName in enumerate(sub.Const._LARGE_PLAYERS_LIST_):
        # 対象者名がリストに含まれている場合
        if 0 < len(re.findall(playerName, chkName)):
            # Trueを返す
            return True
    # 習得技に習得者名が含まれていない場合、Falseを返す
    return False


#--------------------------------------------------------------------------
# 引数とした属性に見合う最強シュートを取得
# 引数    element      : 習得したい属性
#         maxTP        : 最大TP
#         flgBGMV      : ちょうわざ！習得フラグ
#         flgECO       : セツヤク！習得フラグ
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getStrongestShot(element, maxTP, flgBGMV, flgECO):
    moveData = []
    # 風属性の場合
    if element in [sub.Const._ELE_WI_]:
        # クロスファイア（風）を習得
        moveData = ['クロスファイア（風）',sub.Const._MV_NS_, 130, 70, '一致']
    # 火属性の場合
    elif element in [sub.Const._ELE_FI_]:
        # ネオ・ギャラクシーを習得
        # クロスファイア（火）でも問題ないが、パートナー指定がゆるいネオ・ギャラクシーを返す
        moveData = ['ネオ・ギャラクシー',sub.Const._MV_NS_, 130, 70, '一致']
    # 林属性の場合
    elif element in [sub.Const._ELE_WO_]:
        # 皇帝ペンギン１号を習得
        moveData = ['こうていペンギン１ごう',sub.Const._MV_NS_, 127, 62, '一致']
    # 山属性の場合
    elif element in [sub.Const._ELE_MO_]:
        # ネオ・ギャラクシーを習得
        # 秘伝書が存在する山属性最強シュート技はイーグルバスターだが、不一致技を与えた方が期待値が高くなる
        moveData = ['ネオ・ギャラクシー',sub.Const._MV_NS_, 130, 70, '']
    # 必殺技情報を返す
    return moveData

#--------------------------------------------------------------------------
# 引数とした属性に見合う最強キャッチを取得
# 引数    element      : 習得したい属性
#         maxTP        : 最大TP
#         flgBGMV      : ちょうわざ！習得フラグ
#         flgECO       : セツヤク！習得フラグ
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getStrongestCatch(element, maxTP, flgBGMV, flgECO):
    moveData = []
    # 風属性の場合
    if element in [sub.Const._ELE_WI_]:
        # ビーストファングを習得
        # 秘伝書が存在する風属性最強キャッチ技はセーフティプロテクトだが、不一致技を与えた方が期待値が高くなる
        moveData = ['ビーストファング',sub.Const._MV_CA_, 130, 57, '']
    # 火属性の場合
    elif element in [sub.Const._ELE_FI_]:
        # ビーストファングを習得
        moveData = ['ビーストファング',sub.Const._MV_CA_, 130, 57, '一致']
    # 林属性の場合
    elif element in [sub.Const._ELE_WO_]:
        # ビーストファングを習得
        # 秘伝書が存在する林属性最強キャッチ技はデュアルスマッシュだが、不一致技を与えた方が期待値が高くなる
        moveData = ['ビーストファング',sub.Const._MV_CA_, 130, 57, '']
    # 山属性の場合
    elif element in [sub.Const._ELE_MO_]:
        # 無限の壁を習得
        # 秘伝書が存在する山属性最強シュート技はイーグルバスターだが、不一致技を与えた方が期待値が高くなる
        moveData = ['むげんのかべ',sub.Const._MV_CA_, 125, 57, '一致']
    # 必殺技情報を返す
    return moveData


#--------------------------------------------------------------------------
# 引数とした属性に見合う最強ドリブルを取得
# 引数    element      : 習得したい属性
#         maxTP        : 最大TP
#         flgBGMV      : ちょうわざ！習得フラグ
#         flgECO       : セツヤク！習得フラグ
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getStrongestDribble(element, maxTP, flgBGMV, flgECO):
    moveData = []
    # 風属性の場合
    if element in [sub.Const._ELE_WI_]:
        # ブーストグライダーを習得
        # 秘伝書が存在する風属性最強ドリブル技はヘブンズタイムだが、不一致技を与えた方が期待値が高くなる
        moveData = ['ブーストグライダー',sub.Const._MV_DR_, 117, 50, '']
    # 火属性の場合
    elif element in [sub.Const._ELE_FI_]:
        # ブーストグライダーを習得
        moveData = ['ブーストグライダー',sub.Const._MV_DR_, 117, 50, '一致']
    # 林属性の場合
    elif element in [sub.Const._ELE_WO_]:
        # ビーストファングを習得
        # 秘伝書が存在する林属性最強ドリブル技はデュアルパスだが、不一致技を与えた方が期待値が高くなる
        moveData = ['ブーストグライダー',sub.Const._MV_DR_, 117, 50, '']
    # 山属性の場合
    elif element in [sub.Const._ELE_MO_]:
        # トリプルダッシュを習得
        moveData = ['トリプルダッシュ',sub.Const._MV_DR_, 113, 50, '一致']
    # 必殺技情報を返す
    return moveData


#--------------------------------------------------------------------------
# 引数とした属性に見合う最強ブロックを取得
# 引数    element      : 習得したい属性
#         gender       : 習得者の性別
#         maxTP        : 習得者の最大TP。低すぎる場合、シグマゾーンで妥協する
#         flgBGMV      : ちょうわざ！習得フラグ
#         flgECO       : セツヤク！習得フラグ
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getStrongestBlock(element, gender, maxTP, flgBGMV, flgECO):
    moveData = []
    # TP最大値が下限値を下回る場合
    if maxTP < sub.Const._TP_LIMIT_:
        # シグマゾーンを習得
        moveData = getSigmaZone(element)
    # 風属性の場合
    elif element in [sub.Const._ELE_WI_]:
        # 女性選手の場合
        if gender in [sub.Const._GND_FEMALE_]:
            # パーフェクト・タワーを習得
            moveData = ['パーフェクト・タワー',sub.Const._MV_BL_, 115, 50, '一致']
        else:
            # ハリケーンアローを習得
            moveData = ['ハリケーンアロー',sub.Const._MV_BL_, 117, 50, '一致']
    # 火属性の場合
    elif element in [sub.Const._ELE_FI_]:
        # マッドエクスプレスを習得
        moveData = ['マッドエクスプレス',sub.Const._MV_BL_, 113, 50, '一致']
    # 林属性の場合
    elif element in [sub.Const._ELE_WO_]:
        # ボディシールドを習得
        # 秘伝書が存在する林属性最強ブロック技はシグマゾーン。不一致技を与えた方が威力は上
        moveData = ['ボディシールド',sub.Const._MV_BL_, 115, 50, '一致']
    # 山属性の場合
    elif element in [sub.Const._ELE_MO_]:
        # ボディシールドを習得
        # 秘伝書が存在する山属性最強ブロック技かごめかごめだが、ファウル率が低いボディシールドを与える
        moveData = ['ボディシールド',sub.Const._MV_BL_, 115, 50, '一致']
    # 必殺技情報を返す
    return moveData


#--------------------------------------------------------------------------
# 引数とした属性に見合う最強シュートブロックを取得
# 引数    element      : 習得したい属性
#         name         : 習得選手名
#         maxTP        : 最大TP
#         flgBGMV      : ちょうわざ！習得フラグ
#         flgECO       : セツヤク！習得フラグ
# 戻り値
# moveData : 必殺技情報
#--------------------------------------------------------------------------
def getStrongestShotBlock(element, name, maxTP, flgBGMV, flgECO):
    moveData = []
    # 初期値として体格をMサイズで設定
    size = sub.Const._MIDDLE_SIZE_
    # 習得技の数だけ繰り返す
    for sizeCnt, sizeData in enumerate(sub.Const._LARGE_PLAYERS_LIST_):
        # Lサイズ選手リストに名前が含まれている場合、Lサイズを設定
        if name in [sizeData]:
            size = sub.Const._LARGE_SIZE_
            break
    # Lサイズの場合、どの属性でもロックウォールダムでいい。
    if size in [sub.Const._LARGE_SIZE_]:
        # ロックウォールダムを習得
        moveData = ['ロックウォールダム',sub.Const._MV_BB_, 106, 46, '']
        # 林属性の場合
        if element in [sub.Const._ELE_WO_]:
            # 一致を付与
            moveData[sub.Const._MOVE_ELE_] = '一致'
    # 風属性の場合
    elif element in [sub.Const._ELE_WI_]:
        # 旋風陣を習得
        moveData = ['せんぷうじん',sub.Const._MV_BB_, 90, 33, '一致']
    # 火属性の場合
    elif element in [sub.Const._ELE_FI_]:
        # シューティングスターを習得
        moveData = ['シューティングスター',sub.Const._MV_BB_, 84, 40, '一致']
    # 林属性の場合
    elif element in [sub.Const._ELE_WO_]:
        # 旋風陣を習得
        # 秘伝書が存在し、Lサイズ以外でも扱える林属性最強シュートブロック技はダブルトルネード。シュート技はパワーダウンできない。
        moveData = ['せんぷうじん',sub.Const._MV_BB_, 90, 33, '']
    # 山属性の場合
    elif element in [sub.Const._ELE_MO_]:
        # 旋風陣を習得
        # 秘伝書が存在する山属性最強シュートブロック技はメガトンヘッド。シュート技はパワーダウンできない。
        moveData = ['せんぷうじん',sub.Const._MV_BB_, 90, 33, '']
    # 必殺技情報を返す
    return moveData


