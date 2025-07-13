import sub.Const

#--------------------------------------------------------------------------
# ステータス振り分け順設定
# priorityに格納した順を優先順とする
# 先頭部分のSTATUS_TYPEは振り分け方針
#   _NORMAL_          : バランス型。スタミナとガッツを軽視する
#   _KCK_AND_CNT_     : Aカテ最優先
#   _BDY_GRD_AND_GUT_ : Bカテ最優先
#   _SPD_AND_STM_     : Cカテ最優先
#   _BDY_121_         : ボディ121調整(キーマンGK特化育成用)
#   _GRD_121_         : ガード121調整(キーマンDF特化育成用)
# 計算優先順位取得
# 引数    position    : ポジション(sub.Const._POS_FW_、sub.Const._POS_GK_)
# 戻り値  priorityList : 配分優先順位のリスト
#--------------------------------------------------------------------------
def getCalcPriorityList(position):
    retPriorities = []
    if position in [sub.Const._POS_FW_]:
        # キーマンDFの標準的なFW
        priority = []
        priority.append(sub.Const._NORMAL_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
        # 競り合い重視FW
        priority = []
        priority.append(sub.Const._KCK_AND_CNT_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
    elif position in [sub.Const._POS_MF_]:
        # キーマンDFバランス型
        priority = []
        priority.append(sub.Const._NORMAL_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
        # Bカテ特化
        priority = []
        priority.append(sub.Const._BDY_GRD_AND_GUT_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
    elif position in [sub.Const._POS_DF_]:
        # キーマンDFバランス型
        priority = []
        priority.append(sub.Const._NORMAL_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
        # Bカテ特化
        priority = []
        priority.append(sub.Const._BDY_GRD_AND_GUT_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
    elif position in [sub.Const._POS_GK_]:
        # キーマンDFバランス型
        priority = []
        priority.append(sub.Const._NORMAL_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
        # Bカテ特化
        priority = []
        priority.append(sub.Const._BDY_GRD_AND_GUT_)
        priority.append(sub.Const._GRD_MAX_)
        priority.append(sub.Const._BDY_MAX_)
        priority.append(sub.Const._GUT_MAX_)
        priority.append(sub.Const._CNT_MAX_)
        priority.append(sub.Const._SPD_MAX_)
        priority.append(sub.Const._KCK_MAX_)
        priority.append(sub.Const._STM_MAX_)
        retPriorities.append(priority)
    
    return retPriorities
