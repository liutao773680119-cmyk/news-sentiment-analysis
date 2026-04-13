from news_sentiment.analysis.rules import detect_event_themes, detect_themes
from news_sentiment.models import Event


def test_detect_themes_matches_ai_application_aliases() -> None:
    text = "Sora退出后，可灵AI周度活跃用户环比增长，Qwen新版本继续发布。"
    assert "AI应用" in detect_themes(text)


def test_detect_themes_matches_ai_marketing_as_ai_application() -> None:
    text = "AI营销概念走强，蓝色光标、粤传媒等涨幅居前。"
    assert "AI应用" in detect_themes(text)


def test_detect_themes_matches_zhipu_ai_as_ai_application() -> None:
    text = "智谱AI概念走高，平治信息、首都在线等涨幅居前。"
    assert "AI应用" in detect_themes(text)


def test_detect_themes_matches_charging_infra_aliases() -> None:
    text = "四川提出到2027年底建成205万个充电设施，提升公共充电容量。"
    assert "充电桩" in detect_themes(text)


def test_detect_themes_matches_data_security_aliases() -> None:
    text = "科学家实现DNA安全加密实景测试，为敏感领域通信加密开辟新途径。"
    assert "数据安全" in detect_themes(text)


def test_detect_themes_matches_innovative_drug_aliases() -> None:
    text = "礼来口服GLP-1减肥药获批上市，曲妥珠单抗销售目标仍保持增长。"
    themes = detect_themes(text)
    assert "创新药" in themes


def test_detect_themes_matches_gold_aliases() -> None:
    text = "现货黄金日内跌幅扩大至3%，现货白银日内跌幅扩大至6%。"
    assert "黄金" in detect_themes(text)


def test_detect_themes_matches_oil_gas_aliases() -> None:
    text = "燃气分布式发电系统支撑页岩油示范区生产，并推进气代油工程。"
    assert "油气" in detect_themes(text)


def test_detect_themes_matches_semiconductor_aliases() -> None:
    text = "广州提出加快粤芯、增芯等重大项目建设，打造国家集成电路产业发展第三极。"
    assert "半导体" in detect_themes(text)


def test_detect_themes_matches_cpo_as_compute_infra_signal() -> None:
    text = "CPO概念走强，光模块方向盘中拉升。"
    assert "算力" in detect_themes(text)


def test_detect_themes_matches_optical_communication_as_compute_infra_signal() -> None:
    text = "光通信概念反复活跃，特发信息、太辰光等涨幅居前。"
    assert "算力" in detect_themes(text)


def test_detect_themes_matches_liquid_cooled_server_as_compute_infra_signal() -> None:
    text = "液冷服务器概念走强，网宿科技、依米康等涨幅居前。"
    assert "算力" in detect_themes(text)


def test_detect_themes_matches_data_center_storage_project_as_compute_infra_signal() -> None:
    text = "中标某银行数据中心存储更替项目，项目金额超千万元。"
    assert "算力" in detect_themes(text)


def test_detect_themes_does_not_treat_advanced_storage_equipment_as_compute_infra() -> None:
    text = "华海清科面向先进存储的新型12英寸晶圆减薄装备首台出机。"
    assert "算力" not in detect_themes(text)


def test_detect_themes_matches_integrated_circuit_edge_aliases() -> None:
    text = "国产EDA工具链和先进封装产线建设提速，带动封测环节景气度回升。"
    assert "半导体" in detect_themes(text)


def test_detect_themes_matches_cultural_tourism_aliases() -> None:
    text = "2026清明档电影片单发布，院线和出游消费预期同步升温。"
    assert "文旅" in detect_themes(text)


def test_detect_themes_matches_new_energy_vehicle_aliases() -> None:
    text = "乘联分会：3月全国乘用车厂商新能源批发预估112万辆。"
    assert "新能源车" in detect_themes(text)


def test_detect_themes_matches_power_resource_aliases() -> None:
    text = "中国能建与华北电力大学签署战略合作协议，双方将围绕构建新型能源体系和新型电力系统深化合作。"
    assert "电力资源" in detect_themes(text)


def test_detect_themes_matches_power_plant_epc_aliases() -> None:
    text = "中国能建浙江院以联合体形式中标浙能长兴电厂迁建EPC总承包项目。"
    assert "电力资源" in detect_themes(text)


def test_detect_themes_matches_engineering_machinery_theme_name() -> None:
    text = "工程机械板块走强，建设机械、徐工机械、中联重科等涨幅居前。"
    assert "工程机械" in detect_themes(text)


def test_detect_themes_matches_energy_saving_equipment_aliases() -> None:
    text = "工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会。"
    assert "节能装备" in detect_themes(text)


def test_detect_themes_matches_insurance_theme_name() -> None:
    text = "保险板块集体走强，中国太保、新华保险、中国人保涨幅居前。"
    assert "保险" in detect_themes(text)


def test_detect_themes_matches_aviation_theme_name() -> None:
    text = "航空板块走强，广联航空、航发动力、爱乐达等涨幅居前。"
    assert "航空" in detect_themes(text)


def test_detect_themes_does_not_treat_air_cargo_agency_scope_as_aviation_theme() -> None:
    text = "经营范围包含航空国际货物运输代理、海上国际货物运输代理、陆路国际货物运输代理等。"
    assert "航空" not in detect_themes(text)


def test_detect_themes_matches_port_machinery_aliases() -> None:
    text = "GENMA获海外两台装船机订单，该设备将用于客户码头散料装船作业。"
    assert "港口机械" in detect_themes(text)


def test_detect_themes_matches_pcb_theme_name() -> None:
    text = "PCB概念震荡走强，沪电股份、生益科技、奥士康等涨幅居前。"
    assert "PCB" in detect_themes(text)


def test_detect_themes_matches_real_estate_theme_name() -> None:
    text = "房地产板块震荡走高，中天服务、保利发展、万科A等涨幅居前。"
    assert "房地产" in detect_themes(text)


def test_detect_themes_matches_rare_earth_magnet_theme_name() -> None:
    text = "稀土永磁概念走高，英洛华、华宏科技、中科磁业等涨幅居前。"
    assert "稀土永磁" in detect_themes(text)


def test_detect_themes_matches_commercial_space_theme_name() -> None:
    text = "起帆电缆与宇迹航天达成战略合作，将拓展商业航天各领域合作空间。"
    assert "商业航天" in detect_themes(text)


def test_detect_themes_matches_copper_cable_high_speed_connection_theme() -> None:
    text = "铜缆高速连接概念拉升，航天电器涨停。"
    assert "铜缆高速连接" in detect_themes(text)


def test_detect_themes_matches_apple_supply_chain_theme() -> None:
    text = "苹果概念走强，博杰股份涨停。"
    assert "苹果链" in detect_themes(text)


def test_detect_themes_matches_xinchuang_aliases() -> None:
    text = "李乐成调研信息技术创新应用和未来产业发展研究工作。"
    assert "信创" in detect_themes(text)


def test_detect_themes_matches_data_security_app_sdk_notice_aliases() -> None:
    text = "关于侵害用户权益行为的APP（SDK）通报（2026年第2批，总第55批）"
    assert "数据安全" in detect_themes(text)


def test_detect_themes_matches_new_material_narrow_policy_aliases() -> None:
    text = "以先进基础材料、关键战略材料、前沿新材料、人工智能+材料为主攻方向，强化新材料创新发展。"
    assert "新材料" in detect_themes(text)


def test_detect_themes_does_not_treat_generic_passenger_car_data_as_new_energy_vehicle() -> None:
    text = "乘联分会预计3月全国乘用车厂商批发销量保持增长。"
    assert "新能源车" not in detect_themes(text)


def test_detect_event_themes_does_not_expand_regional_industry_data_into_multiple_themes() -> None:
    event = Event(
        event_id="event-1",
        first_seen_at="2026-04-13T22:11:54+08:00",
        last_seen_at="2026-04-13T22:11:54+08:00",
        canonical_title="上海：今年前两个月三大先导产业制造业产值增长13.8%",
        summary="人民财讯4月13日电，记者从13日在上海举行的国新办中外记者见面会上了解到，上海新产业、新业态、新动能加快成长，新质生产力培育壮大，今年前两个月，人工智能、集成电路、生物医药三大先导产业制造业产值增长13.8%。",
        source="stcn",
        published_at="2026-04-13T22:11:54+08:00",
        url="https://www.stcn.com/article/detail/3745834.html",
        event_type="fast_news",
        event_subtype="industry_data",
    )

    assert detect_event_themes(event) == []


def test_detect_themes_does_not_treat_generic_energy_saving_policy_as_energy_saving_equipment() -> None:
    text = "工业节能降碳工作推进会召开，研究重点行业节能改造安排。"
    assert "节能装备" not in detect_themes(text)


def test_detect_themes_does_not_treat_generic_information_technology_policy_as_xinchuang() -> None:
    text = "信息技术服务业发展座谈会召开，研究软件和信息服务业运行情况。"
    assert "信创" not in detect_themes(text)


def test_detect_themes_does_not_treat_generic_sdk_conference_as_data_security() -> None:
    text = "移动应用开发者大会发布新SDK和应用生态合作计划。"
    assert "数据安全" not in detect_themes(text)


def test_detect_themes_does_not_treat_generic_new_material_roundtable_as_new_material_theme() -> None:
    text = "工业和信息化部召开新材料领域中小企业圆桌会。"
    assert "新材料" not in detect_themes(text)


def test_detect_themes_does_not_treat_breeding_chip_as_semiconductor() -> None:
    text = "育种场应用京芯一号育种芯片，提升白羽肉鸡育种效率。"
    assert "半导体" not in detect_themes(text)


def test_detect_themes_matches_lithium_battery_aliases() -> None:
    text = "电解液和其他电池材料需求回升，带动锂电产业链景气度修复。"
    assert "锂电池" in detect_themes(text)


def test_detect_themes_does_not_treat_generic_listing_application_as_innovative_drug() -> None:
    text = "公司公告称已向港交所递交上市申请，拟发行H股并在主板挂牌。"
    assert "创新药" not in detect_themes(text)


def test_detect_themes_does_not_treat_h_share_listing_as_lithium_battery() -> None:
    text = "企业正筹划H股发行并申请在联交所主板上市，以补充国际化运营资金。"
    assert "锂电池" not in detect_themes(text)


def test_detect_themes_does_not_treat_generic_distributed_generation_as_oil_gas() -> None:
    text = "园区将建设分布式发电系统并升级配套电网，以提升供电稳定性。"
    assert "油气" not in detect_themes(text)


def test_detect_themes_does_not_treat_gas_turbine_as_oil_gas() -> None:
    text = "在燃气轮机领域，公司已进入中国航发燃机等主机厂商供应商体系。"
    assert "油气" not in detect_themes(text)
