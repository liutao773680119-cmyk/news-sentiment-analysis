from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks


def test_map_themes_to_stocks_returns_weighted_candidates() -> None:
    rows = map_themes_to_stocks(["算力"])
    assert rows[0].stock_code
    assert rows[0].weight > 0


def test_match_historical_events_returns_theme_related_samples() -> None:
    matches = match_historical_events(["算力"])
    assert matches
    assert "算力" in matches[0]["themes"]


def test_map_themes_to_stocks_supports_extended_seed_themes() -> None:
    rows = map_themes_to_stocks(["AI应用", "充电桩", "数据安全"])
    assert {row.theme_name for row in rows} >= {"AI应用", "充电桩", "数据安全"}


def test_match_historical_events_supports_extended_seed_themes() -> None:
    matches = match_historical_events(["AI应用", "充电桩", "数据安全"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"AI应用", "充电桩", "数据安全"} <= matched_themes


def test_map_themes_to_stocks_supports_commodity_seed_themes() -> None:
    rows = map_themes_to_stocks(["黄金", "油气"])
    assert {row.theme_name for row in rows} >= {"黄金", "油气"}


def test_match_historical_events_supports_commodity_seed_themes() -> None:
    matches = match_historical_events(["黄金", "油气"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"黄金", "油气"} <= matched_themes


def test_map_themes_to_stocks_supports_company_theme_seed_themes() -> None:
    rows = map_themes_to_stocks(["户外经济", "锂电池"])
    assert {row.theme_name for row in rows} >= {"户外经济", "锂电池"}


def test_match_historical_events_supports_company_theme_seed_themes() -> None:
    matches = match_historical_events(["户外经济", "锂电池"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"户外经济", "锂电池"} <= matched_themes


def test_map_themes_to_stocks_supports_tire_and_home_seed_themes() -> None:
    rows = map_themes_to_stocks(["轮胎", "家居"])
    assert {row.theme_name for row in rows} >= {"轮胎", "家居"}


def test_match_historical_events_supports_tire_and_home_seed_themes() -> None:
    matches = match_historical_events(["轮胎", "家居"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"轮胎", "家居"} <= matched_themes


def test_map_themes_to_stocks_supports_semiconductor_theme() -> None:
    rows = map_themes_to_stocks(["半导体"])
    assert {row.theme_name for row in rows} >= {"半导体"}


def test_match_historical_events_supports_semiconductor_theme() -> None:
    matches = match_historical_events(["半导体"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"半导体"} <= matched_themes


def test_map_themes_to_stocks_supports_integrated_circuit_edge_stocks() -> None:
    rows = map_themes_to_stocks(["半导体"])
    assert {"301269", "600584"} <= {row.stock_code for row in rows}


def test_match_historical_events_supports_integrated_circuit_edge_keywords() -> None:
    matches = match_historical_events(["半导体"])
    semiconductor_matches = [row for row in matches if "半导体" in row["themes"]]
    assert any(
        {"EDA", "先进封装"} <= set(row["keywords"])
        for row in semiconductor_matches
    )


def test_map_themes_to_stocks_supports_cultural_tourism_theme() -> None:
    rows = map_themes_to_stocks(["文旅"])
    assert {row.theme_name for row in rows} >= {"文旅"}


def test_match_historical_events_supports_cultural_tourism_theme() -> None:
    matches = match_historical_events(["文旅"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"文旅"} <= matched_themes


def test_map_themes_to_stocks_supports_new_energy_vehicle_theme() -> None:
    rows = map_themes_to_stocks(["新能源车"])
    assert {row.theme_name for row in rows} >= {"新能源车"}


def test_match_historical_events_supports_new_energy_vehicle_theme() -> None:
    matches = match_historical_events(["新能源车"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"新能源车"} <= matched_themes


def test_map_themes_to_stocks_supports_power_resource_theme() -> None:
    rows = map_themes_to_stocks(["电力资源"])
    assert {row.theme_name for row in rows} >= {"电力资源"}


def test_match_historical_events_supports_power_resource_theme() -> None:
    matches = match_historical_events(["电力资源"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"电力资源"} <= matched_themes


def test_map_themes_to_stocks_supports_engineering_machinery_theme() -> None:
    rows = map_themes_to_stocks(["工程机械"])
    assert {row.theme_name for row in rows} >= {"工程机械"}


def test_match_historical_events_supports_engineering_machinery_theme() -> None:
    matches = match_historical_events(["工程机械"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"工程机械"} <= matched_themes


def test_map_themes_to_stocks_supports_energy_saving_equipment_theme() -> None:
    rows = map_themes_to_stocks(["节能装备"])
    assert {row.theme_name for row in rows} >= {"节能装备"}
    assert {"600481", "002158"} <= {row.stock_code for row in rows}


def test_match_historical_events_supports_energy_saving_equipment_theme() -> None:
    matches = match_historical_events(["节能装备"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"节能装备"} <= matched_themes


def test_map_themes_to_stocks_supports_xinchuang_theme() -> None:
    rows = map_themes_to_stocks(["信创"])
    assert {row.theme_name for row in rows} >= {"信创"}
    assert {"600536", "002368"} <= {row.stock_code for row in rows}


def test_match_historical_events_supports_xinchuang_theme() -> None:
    matches = match_historical_events(["信创"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"信创"} <= matched_themes


def test_map_themes_to_stocks_supports_new_material_theme() -> None:
    rows = map_themes_to_stocks(["新材料"])
    assert {row.theme_name for row in rows} >= {"新材料"}


def test_match_historical_events_supports_new_material_theme() -> None:
    matches = match_historical_events(["新材料"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"新材料"} <= matched_themes


def test_map_themes_to_stocks_supports_apple_supply_chain_theme() -> None:
    rows = map_themes_to_stocks(["苹果链"])
    assert {row.theme_name for row in rows} >= {"苹果链"}


def test_match_historical_events_supports_apple_supply_chain_theme() -> None:
    matches = match_historical_events(["苹果链"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"苹果链"} <= matched_themes


def test_map_themes_to_stocks_supports_insurance_theme() -> None:
    rows = map_themes_to_stocks(["保险"])
    assert {row.theme_name for row in rows} >= {"保险"}


def test_match_historical_events_supports_insurance_theme() -> None:
    matches = match_historical_events(["保险"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"保险"} <= matched_themes


def test_map_themes_to_stocks_supports_aviation_theme() -> None:
    rows = map_themes_to_stocks(["航空"])
    assert {row.theme_name for row in rows} >= {"航空"}


def test_match_historical_events_supports_aviation_theme() -> None:
    matches = match_historical_events(["航空"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"航空"} <= matched_themes


def test_map_themes_to_stocks_supports_pcb_theme() -> None:
    rows = map_themes_to_stocks(["PCB"])
    assert {row.theme_name for row in rows} >= {"PCB"}


def test_match_historical_events_supports_pcb_theme() -> None:
    matches = match_historical_events(["PCB"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"PCB"} <= matched_themes


def test_map_themes_to_stocks_supports_real_estate_theme() -> None:
    rows = map_themes_to_stocks(["房地产"])
    assert {row.theme_name for row in rows} >= {"房地产"}


def test_match_historical_events_supports_real_estate_theme() -> None:
    matches = match_historical_events(["房地产"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"房地产"} <= matched_themes


def test_map_themes_to_stocks_supports_rare_earth_magnet_theme() -> None:
    rows = map_themes_to_stocks(["稀土永磁"])
    assert {row.theme_name for row in rows} >= {"稀土永磁"}


def test_match_historical_events_supports_rare_earth_magnet_theme() -> None:
    matches = match_historical_events(["稀土永磁"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"稀土永磁"} <= matched_themes


def test_match_historical_events_supports_port_machinery_theme() -> None:
    matches = match_historical_events(["港口机械"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"港口机械"} <= matched_themes
