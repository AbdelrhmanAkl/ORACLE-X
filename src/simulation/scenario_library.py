from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    event_type: str
    demand_change_pct: float
    inventory_change_pct: float
    supplier_pressure_pct: float
    customer_score_change: float
    description: str


SCENARIOS = (
    Scenario(
        scenario_id="SCN-01",
        name="Baseline Stable",
        event_type="CONTROLLED_BUSINESS_SCENARIO",
        demand_change_pct=0.0,
        inventory_change_pct=0.0,
        supplier_pressure_pct=0.0,
        customer_score_change=0.0,
        description="Stable business conditions with no material simulated shock.",
    ),
    Scenario(
        scenario_id="SCN-02",
        name="Mild Demand Growth",
        event_type="CONTROLLED_BUSINESS_SCENARIO",
        demand_change_pct=8.0,
        inventory_change_pct=-5.0,
        supplier_pressure_pct=2.0,
        customer_score_change=-0.05,
        description="Mild increase in demand with limited inventory pressure.",
    ),
    Scenario(
        scenario_id="SCN-03",
        name="Moderate Demand Increase",
        event_type="CONTROLLED_BUSINESS_SCENARIO",
        demand_change_pct=15.0,
        inventory_change_pct=-10.0,
        supplier_pressure_pct=4.0,
        customer_score_change=-0.10,
        description="Demand reaches the detection threshold but inventory cover remains above the incident threshold.",
    ),
    Scenario(
        scenario_id="SCN-04",
        name="Inventory Pressure",
        event_type="CONTROLLED_BUSINESS_SCENARIO",
        demand_change_pct=5.0,
        inventory_change_pct=-25.0,
        supplier_pressure_pct=3.0,
        customer_score_change=-0.10,
        description="Inventory pressure without sufficient demand increase to trigger the imbalance rule.",
    ),
    Scenario(
        scenario_id="SCN-05",
        name="Low Cover Only",
        event_type="CONTROLLED_BUSINESS_SCENARIO",
        demand_change_pct=5.0,
        inventory_change_pct=-30.0,
        supplier_pressure_pct=5.0,
        customer_score_change=-0.20,
        description="Inventory coverage falls below the safety threshold while demand remains below the detection threshold.",
    ),
    Scenario(
        scenario_id="SCN-06",
        name="Demand-Supply Imbalance",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=25.0,
        inventory_change_pct=-18.0,
        supplier_pressure_pct=12.0,
        customer_score_change=-0.30,
        description="Default demand-supply imbalance scenario used by the current engine.",
    ),
    Scenario(
        scenario_id="SCN-07",
        name="Strong Demand Shock",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=35.0,
        inventory_change_pct=-20.0,
        supplier_pressure_pct=15.0,
        customer_score_change=-0.40,
        description="Strong demand increase combined with meaningful inventory pressure.",
    ),
    Scenario(
        scenario_id="SCN-08",
        name="Severe Supply Shock",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=20.0,
        inventory_change_pct=-30.0,
        supplier_pressure_pct=20.0,
        customer_score_change=-0.50,
        description="Demand increases while inventory and supplier conditions deteriorate materially.",
    ),
    Scenario(
        scenario_id="SCN-09",
        name="Extreme Demand Shock",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=50.0,
        inventory_change_pct=-35.0,
        supplier_pressure_pct=25.0,
        customer_score_change=-0.80,
        description="Extreme simulated demand surge with severe inventory and supplier pressure.",
    ),
    Scenario(
        scenario_id="SCN-10",
        name="Detection Boundary",
        event_type="CONTROLLED_BUSINESS_BOUNDARY",
        demand_change_pct=15.0,
        inventory_change_pct=-18.0,
        supplier_pressure_pct=8.0,
        customer_score_change=-0.15,
        description="Boundary-oriented scenario testing the minimum demand threshold with low inventory coverage.",
    ),
    Scenario(
        scenario_id="SCN-11",
        name="Recovery",
        event_type="CONTROLLED_BUSINESS_RECOVERY",
        demand_change_pct=-5.0,
        inventory_change_pct=10.0,
        supplier_pressure_pct=-5.0,
        customer_score_change=0.10,
        description="Business recovery with declining demand pressure and improving inventory conditions.",
    ),
    Scenario(
        scenario_id="SCN-12",
        name="Inventory Recovery",
        event_type="CONTROLLED_BUSINESS_RECOVERY",
        demand_change_pct=0.0,
        inventory_change_pct=15.0,
        supplier_pressure_pct=-3.0,
        customer_score_change=0.05,
        description="Inventory recovery under stable demand.",
    ),
    Scenario(
        scenario_id="SCN-13",
        name="Customer Experience Decline",
        event_type="CONTROLLED_CUSTOMER_SCENARIO",
        demand_change_pct=10.0,
        inventory_change_pct=-10.0,
        supplier_pressure_pct=5.0,
        customer_score_change=-1.20,
        description="Customer experience deteriorates without enough demand and inventory pressure to trigger the imbalance rule.",
    ),
    Scenario(
        scenario_id="SCN-14",
        name="Full Business Stress",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=40.0,
        inventory_change_pct=-40.0,
        supplier_pressure_pct=30.0,
        customer_score_change=-1.50,
        description="Broad business stress affecting demand, inventory, suppliers, and customer experience.",
    ),
    Scenario(
        scenario_id="SCN-15",
        name="Critical Inventory",
        event_type="CONTROLLED_INVENTORY_SHOCK",
        demand_change_pct=10.0,
        inventory_change_pct=-80.0,
        supplier_pressure_pct=15.0,
        customer_score_change=-0.80,
        description="Extreme inventory depletion designed to test critical inventory classification independently of the imbalance rule.",
    ),
    Scenario(
        scenario_id="SCN-16",
        name="Supplier and Customer Risk",
        event_type="CONTROLLED_BUSINESS_SHOCK",
        demand_change_pct=25.0,
        inventory_change_pct=-18.0,
        supplier_pressure_pct=25.0,
        customer_score_change=-1.50,
        description="Demand-supply imbalance combined with high supplier pressure and critical customer experience risk.",
    ),
    Scenario(
        scenario_id="SCN-17",
        name="Demand-Only Surge",
        event_type="CONTROLLED_DEMAND_SCENARIO",
        demand_change_pct=30.0,
        inventory_change_pct=0.0,
        supplier_pressure_pct=5.0,
        customer_score_change=-0.20,
        description="Strong demand surge without inventory depletion to test rule selectivity.",
    ),
    Scenario(
        scenario_id="SCN-18",
        name="Inventory-Only Critical",
        event_type="CONTROLLED_INVENTORY_SCENARIO",
        demand_change_pct=0.0,
        inventory_change_pct=-80.0,
        supplier_pressure_pct=20.0,
        customer_score_change=-0.50,
        description="Critical inventory condition without demand growth to test independent inventory classification.",
    ),
)


def list_scenarios() -> tuple[Scenario, ...]:
    return SCENARIOS


def get_scenario(scenario_id: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.scenario_id == scenario_id:
            return scenario

    raise ValueError(f"Unknown scenario_id: {scenario_id}")