# -*- coding: utf-8 -*-
"""种子规则数据

TabletopMentor MVP 的初始规则数据集，包含：
- 万智牌（Magic: The Gathering）核心规则
- D&D 5e 核心规则
- 阿卡姆惊悚（Arkham Horror LCG）FAQ

参照原 seed_products.py 结构，但数据内容为桌游规则。
"""
from __future__ import annotations

from app.domain.rules.rule import Rule, RuleVariant


def build_seed_rules() -> list[Rule]:
    """构建初始规则数据集（MVP: 50条核心规则）"""

    rules = []

    # ========== 万智牌（Magic: The Gathering）核心规则 ==========

    # 1. 优先权与堆叠
    rules.append(Rule(
        rule_id="mtg-cr-117",
        game="Magic: The Gathering",
        version="CR 2024-03-08",
        section="117",
        rule_text="优先权是指玩家可以施放咒语、起动异能或采取特殊动作的权利。游戏中，主动玩家首先获得优先权。",
        keywords=["优先权", "主动玩家", "priority"],
        complexity="intermediate",
        source_language="zh-CN",
        translations={
            "en": "Priority is the right to cast spells, activate abilities, or take special actions. The active player receives priority first."
        },
        related_rules=["117.1", "117.3", "608.2"],
        common_mistakes=["误以为非主动玩家回合不能做任何事"],
        examples=["对手回合结束步骤，你仍可以施放瞬间咒语"],
        variants=[
            RuleVariant(
                variant_id="mtg-cr-117-2024",
                version="CR 2024-03-08",
                rule_text="优先权是指玩家可以施放咒语、起动异能或采取特殊动作的权利。",
                effective_date="2024-03-08"
            )
        ],
        source_url="https://magic.wizards.com/en/rules",
        updated_at="2024-03-08"
    ))

    rules.append(Rule(
        rule_id="mtg-cr-608",
        game="Magic: The Gathering",
        version="CR 2024-03-08",
        section="608.2",
        rule_text="堆叠中的咒语或异能结算时，按照其上文字从上到下执行。结算过程中不能被打断。",
        keywords=["堆叠", "结算", "stack", "resolve"],
        complexity="intermediate",
        source_language="zh-CN",
        translations={
            "en": "When a spell or ability resolves from the stack, its text is followed from top to bottom. The resolution cannot be interrupted."
        },
        related_rules=["608.2a", "608.2g", "117.3"],
        common_mistakes=["误以为结算过程中可以响应"],
        examples=["闪电击结算时，对手不能在伤害分配前施放反击咒语"],
        variants=[
            RuleVariant(
                variant_id="mtg-cr-608-2024",
                version="CR 2024-03-08",
                rule_text="堆叠中的咒语或异能结算时，按照其上文字从上到下执行。",
                effective_date="2024-03-08"
            )
        ],
        source_url="https://magic.wizards.com/en/rules",
        updated_at="2024-03-08"
    ))

    # 2. 战斗阶段
    rules.append(Rule(
        rule_id="mtg-cr-506",
        game="Magic: The Gathering",
        version="CR 2024-03-08",
        section="506",
        rule_text="战斗阶段分为五个步骤：战斗开始、宣告攻击者、宣告阻挡者、战斗伤害、战斗结束。每个步骤中玩家都会获得优先权。",
        keywords=["战斗阶段", "攻击", "阻挡", "combat"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["506.1", "506.4", "510"],
        common_mistakes=["忘记战斗开始步骤可以响应"],
        examples=["战斗开始步骤时可以横置对手生物使其无法攻击"],
        variants=[
            RuleVariant(
                variant_id="mtg-cr-506-2024",
                version="CR 2024-03-08",
                rule_text="战斗阶段分为五个步骤：战斗开始、宣告攻击者、宣告阻挡者、战斗伤害、战斗结束。",
                effective_date="2024-03-08"
            )
        ],
        updated_at="2024-03-08"
    ))

    # 3. 生命总量与失败
    rules.append(Rule(
        rule_id="mtg-cr-104",
        game="Magic: The Gathering",
        version="CR 2024-03-08",
        section="104.3",
        rule_text="玩家的生命总量降至0或更少时，该玩家在下次状态动作检查时输掉游戏。",
        keywords=["生命总量", "失败", "life total", "lose"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["104.3a", "704.5a"],
        common_mistakes=["误以为生命归0立即失败"],
        examples=["生命归0后，仍可以施放瞬间救回生命"],
        variants=[
            RuleVariant(
                variant_id="mtg-cr-104-2024",
                version="CR 2024-03-08",
                rule_text="玩家的生命总量降至0或更少时，该玩家在下次状态动作检查时输掉游戏。",
                effective_date="2024-03-08"
            )
        ],
        updated_at="2024-03-08"
    ))

    # 4. 瞬间时机
    rules.append(Rule(
        rule_id="mtg-cr-307",
        game="Magic: The Gathering",
        version="CR 2024-03-08",
        section="307.1",
        rule_text="瞬间咒语可以在任何玩家获得优先权的时候施放，包括对手的回合。",
        keywords=["瞬间", "instant", "时机"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["117", "608"],
        common_mistakes=["忘记对手回合也能施放瞬间"],
        examples=["对手攻击时，你可以施放瞬间移除攻击生物"],
        variants=[
            RuleVariant(
                variant_id="mtg-cr-307-2024",
                version="CR 2024-03-08",
                rule_text="瞬间咒语可以在任何玩家获得优先权的时候施放。",
                effective_date="2024-03-08"
            )
        ],
        updated_at="2024-03-08"
    ))

    # ========== D&D 5e 核心规则 ==========

    # 5. 先攻
    rules.append(Rule(
        rule_id="dnd5e-phb-189",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 9: Combat",
        rule_text="先攻决定战斗中的行动顺序。战斗开始时，每个参与者进行一次先攻检定：d20 + 敏捷调整值。",
        keywords=["先攻", "initiative", "战斗顺序"],
        complexity="basic",
        source_language="zh-CN",
        translations={
            "en": "Initiative determines the order of turns during combat. At the start of combat, every participant makes a Dexterity check: d20 + Dexterity modifier."
        },
        related_rules=["phb-189", "phb-177"],
        common_mistakes=["忘记加敏捷调整值"],
        examples=["敏捷+3的角色投出17，先攻总计20"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-189-2014",
                version="5e PHB 2014",
                rule_text="先攻决定战斗中的行动顺序。",
                effective_date="2014-08-19"
            )
        ],
        source_url="https://www.dndbeyond.com/sources/phb",
        updated_at="2014-08-19"
    ))

    # 6. 动作经济
    rules.append(Rule(
        rule_id="dnd5e-phb-192",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 9: Actions in Combat",
        rule_text="在你的回合中，你可以进行一个动作（Action）、一次移动（Move）和一个附赠动作（Bonus Action）。",
        keywords=["动作", "附赠动作", "移动", "action economy"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["phb-192", "phb-189"],
        common_mistakes=["混淆动作和附赠动作"],
        examples=["使用双武器战斗时，主手攻击是动作，副手攻击是附赠动作"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-192-2014",
                version="5e PHB 2014",
                rule_text="在你的回合中，你可以进行一个动作、一次移动和一个附赠动作。",
                effective_date="2014-08-19"
            )
        ],
        updated_at="2014-08-19"
    ))

    # 7. 反应动作
    rules.append(Rule(
        rule_id="dnd5e-phb-190",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 9: Reactions",
        rule_text="反应动作是对某个触发事件的即时回应。每轮你只能使用一次反应动作。",
        keywords=["反应", "reaction", "借机攻击"],
        complexity="intermediate",
        source_language="zh-CN",
        related_rules=["phb-195", "phb-190"],
        common_mistakes=["在同一轮尝试多次反应"],
        examples=["敌人离开你的触及范围时，你可以进行借机攻击"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-190-2014",
                version="5e PHB 2014",
                rule_text="反应动作是对某个触发事件的即时回应。",
                effective_date="2014-08-19"
            )
        ],
        updated_at="2014-08-19"
    ))

    # 8. 优势与劣势
    rules.append(Rule(
        rule_id="dnd5e-phb-173",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 7: Advantage and Disadvantage",
        rule_text="具有优势时，投两次d20取较高值。具有劣势时，投两次d20取较低值。优势和劣势不叠加。",
        keywords=["优势", "劣势", "advantage", "disadvantage"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["phb-173", "phb-176"],
        common_mistakes=["错误叠加多重优势"],
        examples=["隐身攻击获得优势，但目标看不见你也不会叠加第二次优势"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-173-2014",
                version="5e PHB 2014",
                rule_text="具有优势时，投两次d20取较高值。",
                effective_date="2014-08-19"
            )
        ],
        updated_at="2014-08-19"
    ))

    # 9. 豁免检定
    rules.append(Rule(
        rule_id="dnd5e-phb-179",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 7: Saving Throws",
        rule_text="豁免检定用于抵抗法术、陷阱或其他效果。投d20加上相应的属性调整值和熟练加值（如果适用）。",
        keywords=["豁免", "saving throw", "DC"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["phb-179", "phb-204"],
        common_mistakes=["忘记检查是否具有该豁免的熟练项"],
        examples=["面对火球术（DC 15敏捷豁免），你投d20+敏捷调整值+熟练加值（如有）"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-179-2014",
                version="5e PHB 2014",
                rule_text="豁免检定用于抵抗法术、陷阱或其他效果。",
                effective_date="2014-08-19"
            )
        ],
        updated_at="2014-08-19"
    ))

    # 10. 专注
    rules.append(Rule(
        rule_id="dnd5e-phb-203",
        game="D&D 5e",
        version="Player's Handbook",
        section="Chapter 10: Concentration",
        rule_text="某些法术需要专注才能维持其魔法效果。你一次只能专注于一个法术。受到伤害时需要通过专注检定（DC为10或伤害值的一半，取较高者）。",
        keywords=["专注", "concentration", "法术维持"],
        complexity="intermediate",
        source_language="zh-CN",
        related_rules=["phb-203", "phb-204"],
        common_mistakes=["同时维持多个需要专注的法术"],
        examples=["施放祝福术后，如果再施放法师护甲，祝福术立即结束"],
        variants=[
            RuleVariant(
                variant_id="dnd5e-phb-203-2014",
                version="5e PHB 2014",
                rule_text="某些法术需要专注才能维持其魔法效果。",
                effective_date="2014-08-19"
            )
        ],
        updated_at="2014-08-19"
    ))

    # ========== 阿卡姆惊悚（Arkham Horror LCG）FAQ ==========

    # 11. 快速反应窗口
    rules.append(Rule(
        rule_id="ah-faq-react",
        game="Arkham Horror LCG",
        version="FAQ v2.2",
        section="Timing",
        rule_text="快速反应窗口（Reaction Window）是指触发条件满足后，玩家可以打出快速卡牌或触发快速能力的时机。",
        keywords=["快速", "反应", "reaction", "timing"],
        complexity="intermediate",
        source_language="zh-CN",
        related_rules=["ah-rrg-timing", "ah-faq-windows"],
        common_mistakes=["在非快速窗口尝试打出快速卡"],
        examples=["敌人攻击时，你可以打出闪避卡"],
        variants=[
            RuleVariant(
                variant_id="ah-faq-react-2023",
                version="FAQ v2.2 2023",
                rule_text="快速反应窗口是指触发条件满足后的时机。",
                effective_date="2023-05-15"
            )
        ],
        source_url="https://arkhamdb.com/rules",
        updated_at="2023-05-15"
    ))

    # 12. 技能检定
    rules.append(Rule(
        rule_id="ah-rrg-skill-test",
        game="Arkham Horror LCG",
        version="RRG v1.6",
        section="Skill Test",
        rule_text="技能检定包含：确定难度→决定技能值→揭示混乱标记→应用修正→确定成功或失败。成功需要总技能值大于等于难度。",
        keywords=["技能检定", "skill test", "难度", "混乱袋"],
        complexity="basic",
        source_language="zh-CN",
        related_rules=["ah-rrg-chaos", "ah-rrg-commit"],
        common_mistakes=["忘记等于难度也算成功"],
        examples=["难度3的调查，你的智力4，抽到-2，总计2失败"],
        variants=[
            RuleVariant(
                variant_id="ah-rrg-skill-test-2022",
                version="RRG v1.6 2022",
                rule_text="技能检定包含多个步骤。",
                effective_date="2022-08-01"
            )
        ],
        updated_at="2022-08-01"
    ))

    # 更多规则可以继续添加...
    # 为了MVP，这里先提供12条核心规则作为种子数据

    return rules
