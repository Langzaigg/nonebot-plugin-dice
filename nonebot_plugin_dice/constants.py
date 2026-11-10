# -*- coding: utf-8 -*-
"""Dice! 复刻版常量：消息文本、帮助文档、技能表、版本号。"""

from ._msgdata import PLAIN_MSG, HELP_DOC
from ._tables import (
    BASIC_COC7,
    EXPRESSION_COC7,
    LONG_INSANITY,
    SKILL_DEFAULT_VAL,
    SKILL_NAME_REPLACE,
    STR_FEAR,
    STR_PANIC,
    TEMP_INSANITY,
    VARIABLE_COC7,
)

__all__ = [
    "PLAIN_MSG",
    "HELP_DOC",
    "GLOBAL_MSG",
    "GLOBAL_HELP",
    "get_msg_text",
    "get_help_text",
    "BASIC_COC7",
    "EXPRESSION_COC7",
    "LONG_INSANITY",
    "SKILL_DEFAULT_VAL",
    "SKILL_NAME_REPLACE",
    "STR_FEAR",
    "STR_PANIC",
    "TEMP_INSANITY",
    "VARIABLE_COC7",
    "DICE_VER",
    "DICE_SHORT_VER",
    "DICE_FULL_VER",
    "CHAT_CONF",
    "PLAYER_ERRORS",
]

# 与 GlobalVar.h 保持一致
DICE_BUILD = 668
DICE_VER_WITHOUT_BUILD = "2.7.1beta1"
DICE_VER = "%s(%d)" % (DICE_VER_WITHOUT_BUILD, DICE_BUILD)
DICE_SHORT_VER = "Dice! by 溯洄 & Shiki Ver " + DICE_VER


def _ci(d):
    """dict_ci：大小写不敏感，后出现的同键值覆盖先出现的值。"""
    out = {}
    for k, v in d.items():
        out[(k or "").lower()] = v
    return out


GLOBAL_MSG = _ci(PLAIN_MSG)
GLOBAL_HELP = _ci(HELP_DOC)

# 群管词条：词条名 -> 所需信任级别（DiceConsole mChatConf）
CHAT_CONF = {
    "停用指令": 1,
    "禁用回复": 1,
    "禁用jrrp": 1,
    "禁用draw": 1,
    "禁用me": 1,
    "禁用help": 1,
    "许可使用": 3,
    "免清": 3,
    "免黑": 4,
    "忽略": 5,
    "协议无效": 5,
}

# PlayerErrors 的取值在 CharacterCard.cpp 中大小写不一致，按其字面量对照到 _msgdata 中的键
PLAYER_ERRORS = {
    -1: "strPcCardFull",
    -3: "strPCNameEmpty",
    -4: "strPCNameExist",
    -5: "strPcNameNotExist",
    -6: "strPCNameInvalid",
    -7: "strPcInitDelErr",
    -21: "strPcLockedKill",
    -22: "strPcLockedName",
    -23: "strPcLockedWrite",
    -24: "strPcLockedRead",
}


def get_msg_text(key: str) -> str:
    return GLOBAL_MSG.get((key or "").lower(), "")


def get_help_text(key: str) -> str:
    return GLOBAL_HELP.get((key or "").lower(), "")
