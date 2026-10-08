from src.investigation.detection_engine import (
    detect_demand_supply_imbalance,
)
from src.simulation.persistence_adapter import (
    SimulationPersistenceAdapter,
)
from src.simulation.scenario_library import list_scenarios
from src.simulation.simulation_engine import build_simulated_state


BASELINE_ORDERS = 5954
BASELINE_DAILY_ORDERS = 270.6363636363636
BASELINE_DAILY_REVENUE = 36308.45
BASELINE_AOV = 134.16
BASELINE_INVENTORY_UNITS = 74269.28
BASELINE_INVENTORY_COVER_DAYS = 14.0
BASELINE_REVIEW_SCORE = 4.25
BASELINE_SELLER_RISK = 0.38


def run_scenario(scenario, persistence_adapter):
    state = build_simulated_state(
        baseline_orders=BASELINE_ORDERS,
        baseline_daily_orders=BASELINE_DAILY_ORDERS,
        baseline_daily_revenue=BASELINE_DAILY_REVENUE,
        baseline_aov=BASELINE_AOV,
        baseline_inventory_units=BASELINE_INVENTORY_UNITS,
        baseline_inventory_cover_days=BASELINE_INVENTORY_COVER_DAYS,
        baseline_review_score=BASELINE_REVIEW_SCORE,
        baseline_seller_risk=BASELINE_SELLER_RISK,
        demand_change_pct=scenario.demand_change_pct,
        inventory_change_pct=scenario.inventory_change_pct,
        supplier_pressure_pct=scenario.supplier_pressure_pct,
        customer_score_change=scenario.customer_score_change,
    )

    triggered, evidence = detect_demand_supply_imbalance(state)

    persistence_result = persistence_adapter.save_scenario(
        scenario,
        state,
    )

    state["snapshot_id"] = persistence_result["snapshot_id"]

    incident_id = None

    if triggered:
        incident_id = persistence_adapter.save_incident(
            state,
            evidence,
        )

    return {
        "scenario_id": scenario.scenario_id,
        "scenario": scenario.name,
        "demand_change_pct": evidence["demand_change_pct"],
        "inventory_cover_decline_pct": (
            evidence["inventory_cover_decline_pct"]
        ),
        "inventory_cover_days": (
            evidence["simulated_inventory_cover_days"]
        ),
        "incident_triggered": triggered,
        "event_id": persistence_result["event_id"],
        "snapshot_id": persistence_result["snapshot_id"],
        "incident_id": incident_id,
    }


def main():
    scenarios = list_scenarios()
    persistence_adapter = SimulationPersistenceAdapter()

    results = []

    for scenario in scenarios:
        result = run_scenario(
            scenario,
            persistence_adapter,
        )

        results.append(result)

        print(
            f"{result['scenario_id']}  "
            f"{result['scenario']:<35} "
            f"{result['demand_change_pct']:>6.1f}% "
            f"{result['inventory_cover_decline_pct']:>14.1f}% "
            f"{result['inventory_cover_days']:>11.2f} "
            f"{str(result['incident_triggered']):>12} "
            f"event={result['event_id']} "
            f"snapshot={result['snapshot_id']} "
            f"incident={result['incident_id']}"
        )

    print()
    print(f"Total scenarios: {len(results)}")
    print(
        "Incidents triggered: "
        f"{sum(result['incident_triggered'] for result in results)}"
    )
    print(
        "No-incident scenarios: "
        f"{sum(not result['incident_triggered'] for result in results)}"
    )
    print(
        "Incidents persisted: "
        f"{sum(result['incident_id'] is not None for result in results)}"
    )
    print("Database writes: YES")
    print(
        "Persistence: "
        "simulation_events + current_simulated_state + incidents"
    )


if __name__ == "__main__":
    main()