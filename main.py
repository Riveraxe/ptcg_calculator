import re
import random
import sys
from typing import List


# 定义结构体类
class Card:
    def __init__(self, index: int, name: str, type: str, basic: bool = False, supporter: bool = False,
                 search: bool = False):
        self.index = index  # 顺序编号
        self.name = name  # 卡牌名称
        self.type = type  # 卡牌类型：pokemon, trainer, energy
        self.basic = basic  # 是否是 basic 卡牌
        self.supporter = supporter  # 是否是 supporter 卡牌
        self.search = search  # 是否是 search 卡牌

    def __repr__(self):
        # 格式化输出：02 Lugia V Pokemon, Basic
        attributes = []
        if self.basic:
            attributes.append("Basic")
        if self.supporter:
            attributes.append("Supporter")
        if self.search:
            attributes.append("Search")

        # 按格式输出附加属性
        attribute_str = ", ".join(attributes)
        return f"{self.index:02d} {self.name} {self.type.capitalize()}" + (
            f", {attribute_str}" if attribute_str else "")


# 将文件内容解析为卡牌数据
def parse_deck_data_from_file(filename: str) -> List[Card]:
    # 从文件中读取数据
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()

    # 分离出各类数据段
    deck_list = []
    sections = re.split(r'Pokémon:\s|Trainer:\s|Energy:\s', data)

    # 定义类型名称和对应的section索引
    types = ["pokemon", "trainer", "energy"]

    # 当前卡牌的索引值
    current_index = 1

    # 遍历每个部分并解析卡牌
    for type_index, section in enumerate(sections[1:], start=0):
        type_name = types[type_index]

        # 将每行数据解析为卡牌结构体
        for line in section.splitlines():
            if line.strip():
                # 匹配卡牌信息和可选的属性（如 basic、supporter、search）
                card_info = re.match(r'(\d+)\s([\w\s\'\-]+)\s([A-Z]{3})\s(\d+)\s?(basic|supporter|search)?',
                                     line.strip())
                if card_info:
                    num, name, _, _, attribute = card_info.groups()

                    # 根据num（数量）将卡牌添加到列表中，并赋予连续编号
                    for _ in range(int(num)):
                        # 解析是否包含特定属性
                        is_basic = attribute == 'basic'
                        is_supporter = attribute == 'supporter'
                        is_search = attribute == 'search'

                        # 添加到卡牌列表
                        deck_list.append(Card(index=current_index, name=name.strip(), type=type_name,
                                              basic=is_basic, supporter=is_supporter, search=is_search))
                        current_index += 1

    return deck_list


# 从文件中读取并解析数据
filename = "data.txt"  # 你的txt文件名
all_cards = parse_deck_data_from_file(filename)
if len(all_cards) != 60:
    print("卡组数量错误，为" + str(len(all_cards)))
    sys.exit(1)


def draw_initial_hand(cards: List) -> tuple[List, List]:
    while True:
        # 1. 随机抽取起手7张卡牌
        initial_hand = random.sample(cards, 7)

        # 2. 检查是否存在 basic 为 True 的 pokemon
        if any(card.type == 'pokemon' and card.basic for card in initial_hand):
            # 3. 剩余卡牌池（移除7张已抽出的卡牌）
            remaining_cards = [card for card in cards if card not in initial_hand]

            # 4. 随机去除6张卡牌作为奖励卡
            reward_cards = random.sample(remaining_cards, 6)

            # 5. 更新剩余卡牌池（移除奖励卡）
            remaining_cards = [card for card in remaining_cards if card not in reward_cards]

            # 6. 从剩余卡牌池中抽取2张，加入到起手卡牌中
            additional_draw = random.sample(remaining_cards, 1)
            initial_hand.extend(additional_draw)

            # 7. 返回包含9张卡牌的起手手牌和奖励卡牌
            return initial_hand, reward_cards


def print_list_per_line(items) -> None:
    if isinstance(items, (list, tuple, set)):
        for item in items:
            print(str(item))
    else:
        print(str(items))


def simulate_draws(cards: list, num_simulations: int = 10000) -> list[int]:
    count = [0,0,0,0]
    for _ in range(num_simulations):
        # 抽取起手7张卡牌
        initial_hand, reward_cards = draw_initial_hand(cards)
        # print("--------------------------------------------------")
        # print_list_per_line(initial_hand)
        # print("---------reward---------------")
        # print_list_per_line(reward_cards)
        # 计算起手中 "Archeops" 和 "Evolution Incense" 的数量
        initial_count01 = sum(1 for card in initial_hand if card.name in ["Quick Ball"])
        initial_count02 = sum(1 for card in initial_hand if card.name in ["Archeops"])
        initial_count03 = sum(1 for card in initial_hand if card.name in ["Lumineon"])
        initial_count04 = sum(1 for card in initial_hand if card.name in ["Professor Burnet"])
        initial_count05 = sum(1 for card in initial_hand if card.name in ["Evolution Incense"])
        initial_count_basic_pokemon = sum(1 for card in initial_hand if card.type == "pokemon" and card.basic)
        reward_count = sum(1 for card in reward_cards if card.name in ["Archeops"])
        reward_count01 = sum(1 for card in reward_cards if card.name in ["Lumineon"])
        # 起手2基础宝可梦，保证2鱼不都卡奖即可
        condition01 = (
            initial_count_basic_pokemon > 1 and
            initial_count01 + initial_count03 > 0 and
            reward_count01 < 2 and
            reward_count < 2
        )
        # 起手1基础宝可梦且为鱼，保证1基础宝可梦不卡奖并有其他方法搜索即可
        condition02 = (
            initial_count_basic_pokemon == 1 and
            initial_count03 == 1 and
            initial_count01 > 0 and
            reward_count01 < 1 and
            reward_count < 2
        )
        # 起手1基础宝可梦不为鱼，保证不卡奖2鱼且可搜索即可
        condition03 = (
            initial_count_basic_pokemon == 1 and
            initial_count03 == 0 and
            initial_count01 > 0 and
            reward_count01 < 2 and
            reward_count < 2
        )
        # 起手有博士即可
        condition04 = (
            initial_count04 == 1 and
            reward_count < 2
        )
        # 起手有大鸟或熏香
        condition05 = (
            initial_count05 + initial_count02 > 2 and
            reward_count < 2
        )
        # 如果数量大于等于2，则计数一次
        if condition01 or condition02 or condition03 or condition04 or condition05:
            count[0] += 1
    return count


result = simulate_draws(all_cards, 1000000)
print_list_per_line(result)