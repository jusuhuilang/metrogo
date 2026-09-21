"""
三维融合路径评分模型
MetroGo - 基于云边协同的地铁出行AI消费平台
"""


def calculate_score(path, weights=None):
    """
    计算路径综合得分

    参数:
        path: dict，包含 total_time, merchants, carbon_emission 等字段
        weights: dict，三维权重，默认 {'efficiency': 0.4, 'consumption': 0.3, 'green': 0.3}

    返回:
        float: 综合得分（0-100）
    """
    if weights is None:
        weights = {'efficiency': 0.4, 'consumption': 0.3, 'green': 0.3}

    s_eff = calculate_efficiency(path)
    s_con = calculate_consumption(path)
    s_green = calculate_green(path)

    score = (weights['efficiency'] * s_eff +
             weights['consumption'] * s_con +
             weights['green'] * s_green)

    return round(score, 2)


def calculate_efficiency(path):
    """
    效率维度：综合通行耗时
    T_total = T_gaode + T_detour
    """
    t_gaode = path['gaode_time']
    walking_distance = path.get('detour_distance', 500)  # 米
    walking_speed = 4000 / 60  # 4km/h 转换为 米/分钟
    t_walk = walking_distance / walking_speed
    t_stay = 3  # 商户停留基础时间（分钟）
    t_detour = t_walk + t_stay
    t_total = t_gaode + t_detour

    # 归一化（假设最小耗时基准为30分钟）
    min_t = 30
    return min(min_t / t_total * 100, 100)


def calculate_consumption(path):
    """
    消费维度：基于距离衰减函数的商户匹配度
    S_con = 1/max(M) * Σ e^(-θ·ω_s)
    """
    import math
    theta = 0.01  # 衰减系数
    merchants = path.get('merchants', [])
    if not merchants:
        return 0

    score = 0
    for m in merchants:
        distance = m.get('distance', 500)  # 米
        score += math.exp(-theta * distance)

    max_m = 10  # 假设最大商户数
    return min(score / max_m * 100, 100)


def calculate_green(path):
    """
    绿色维度：碳排放量
    E = L * ε，ε = 0.015 kg/公里
    """
    length_km = path.get('length_km', 10)
    epsilon = 0.015
    e_i = length_km * epsilon

    min_e = 0.1  # 假设最小碳排放基准
    return min(min_e / e_i * 100, 100) if e_i > 0 else 100


# 示例
if __name__ == '__main__':
    sample_path = {
        'gaode_time': 25,
        'detour_distance': 500,
        'merchants': [
            {'name': '咖啡店A', 'distance': 200},
            {'name': '面包店B', 'distance': 350},
        ],
        'length_km': 12
    }
    print(f"综合得分: {calculate_score(sample_path)}")
