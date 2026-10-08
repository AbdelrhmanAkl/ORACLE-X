import json
import sqlite3
from datetime import datetime, timezone

from config.settings import DATABASE_PATH

from src.investigation.root_cause_analysis import RootCauseAnalyzer
from src.investigation.evidence_synthesis import EvidenceSynthesizer

from src.debate.debate_engine import DebateEngine

from src.agents.finance_agent import FinanceAgent
from src.agents.operations_agent import OperationsAgent
from src.agents.risk_agent import RiskAgent
from src.agents.customer_agent import CustomerAgent

from src.decision.decision_engine import DecisionEngine
from src.validation.decision_validator import DecisionValidator

from src.data.decision_memory import save_decision_memory

from src.learning.learning_engine import LearningEngine
from src.learning.decision_quality import DecisionQualityEvaluator
from src.learning.adaptive_intelligence import (
    AdaptiveIntelligenceEngine,
)

from src.intelligence.llm_interpreter import (
    LLMInterpreter,
)


class InvestigationEngine:
    """
    ORACLE-X incident investigation engine.

    Responsibilities:
    - Load an existing incident.
    - Load its linked simulation snapshot.
    - Build an evidence package from stored database values.
    - Run deterministic agents.
    - Run deterministic RCA and evidence synthesis.
    - Run deterministic debate and decision.
    - Validate and remember valid decisions.
    - Learn from observed outcomes.
    - Evaluate decision quality.
    - Run read-only adaptive intelligence.
    - Optionally interpret deterministic results with an LLM.

    The engine never:
    - invents business facts,
    - invents observed outcomes,
    - modifies rules,
    - modifies thresholds,
    - uses an LLM as a source of business facts,
    - treats simulation as historical observation,
    - allows the LLM to modify deterministic decisions.
    """

    VERSION = "1.1"

    def __init__(
        self,
        db_path=DATABASE_PATH,
        enable_llm_interpretation=True,
    ):
        self.db_path = db_path
        self.enable_llm_interpretation = (
            enable_llm_interpretation
        )

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _investigation_memory_id(
        self,
        incident_id,
        snapshot_id,
    ):
        return (
            f"INC-{incident_id}-SNAP-{snapshot_id}"
        )

    def _run_llm_interpretation(
        self,
        evidence_package,
    ):
        """
        Run the optional LLM interpretation layer.

        The LLM receives only deterministic ORACLE-X
        investigation results.

        LLM failure must never invalidate or stop
        the deterministic investigation.
        """

        if not self.enable_llm_interpretation:
            return {
                "interpretation_status": (
                    "INTERPRETATION_DISABLED"
                ),
                "constraints": {
                    "deterministic_business_facts": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "decision_modified": False,
                    "rules_modified": False,
                    "thresholds_modified": False,
                    "causal_claims_generated": False,
                },
                "provenance": {
                    "source": (
                        "DETERMINISTIC_INVESTIGATION_RESULTS"
                    ),
                    "interpretation_method": (
                        "LLM_INTERPRETATION_DISABLED"
                    ),
                },
                "version": LLMInterpreter.VERSION,
            }

        try:
            interpretation = (
                LLMInterpreter().interpret(
                    evidence_package
                )
            )

            return interpretation

        except Exception as exc:
            return {
                "interpretation_status": (
                    "INTERPRETATION_UNAVAILABLE"
                ),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "constraints": {
                    "deterministic_business_facts": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "decision_modified": False,
                    "rules_modified": False,
                    "thresholds_modified": False,
                    "causal_claims_generated": False,
                },
                "provenance": {
                    "source": (
                        "DETERMINISTIC_INVESTIGATION_RESULTS"
                    ),
                    "interpretation_method": (
                        "LLM_INTERPRETATION_FAILED"
                    ),
                },
                "version": LLMInterpreter.VERSION,
            }

    def investigate(self, incident_id):
        connection = self._connect()

        try:
            incident = connection.execute(
                """
                SELECT *
                FROM incidents
                WHERE incident_id = ?
                """,
                (incident_id,),
            ).fetchone()

            if incident is None:
                raise ValueError(
                    f"Incident {incident_id} was not found."
                )

            snapshot = connection.execute(
                """
                SELECT *
                FROM current_simulated_state
                WHERE snapshot_id = ?
                """,
                (incident["snapshot_id"],),
            ).fetchone()

            if snapshot is None:
                raise ValueError(
                    f"Simulation snapshot "
                    f"{incident['snapshot_id']} "
                    f"for incident {incident_id} "
                    f"was not found."
                )

            detection_evidence = json.loads(
                incident["evidence_json"]
            )

            investigation_id = (
                f"INV-{incident['incident_id']}-"
                f"{incident['snapshot_id']}"
            )

            memory_investigation_id = (
                self._investigation_memory_id(
                    incident_id=incident_id,
                    snapshot_id=incident["snapshot_id"],
                )
            )

            evidence_package = {
                "investigation_id": investigation_id,
                "investigated_at": datetime.now(
                    timezone.utc
                ).isoformat(),

                "incident": {
                    "incident_id": incident["incident_id"],
                    "incident_type": incident["incident_type"],
                    "severity": incident["severity"],
                    "status": incident["status"],
                    "title": incident["title"],
                    "summary": incident["summary"],
                    "affected_dimension": (
                        incident["affected_dimension"]
                    ),
                    "rule_name": incident["rule_name"],
                    "rule_version": incident["rule_version"],
                    "source_type": incident["source_type"],
                },

                "detection_evidence": detection_evidence,

                "evidence": {
                    "demand": {
                        "baseline_daily_orders": (
                            snapshot[
                                "baseline_daily_orders"
                            ]
                        ),
                        "current_daily_orders": (
                            snapshot[
                                "simulated_daily_orders"
                            ]
                        ),
                        "demand_change_pct": (
                            detection_evidence[
                                "demand_change_pct"
                            ]
                        ),
                        "demand_state": (
                            snapshot["demand_state"]
                        ),
                    },

                    "inventory": {
                        "baseline_inventory_units": (
                            snapshot[
                                "baseline_inventory_units"
                            ]
                        ),
                        "current_inventory_units": (
                            snapshot[
                                "simulated_inventory_units"
                            ]
                        ),
                        "baseline_cover_days": (
                            snapshot[
                                "baseline_inventory_cover_days"
                            ]
                        ),
                        "current_cover_days": (
                            snapshot[
                                "simulated_inventory_cover_days"
                            ]
                        ),
                        "inventory_cover_decline_pct": (
                            detection_evidence[
                                "inventory_cover_decline_pct"
                            ]
                        ),
                        "inventory_state": (
                            snapshot["inventory_state"]
                        ),
                    },

                    "supplier": {
                        "baseline_seller_risk": (
                            snapshot[
                                "baseline_seller_risk"
                            ]
                        ),
                        "current_seller_risk": (
                            snapshot[
                                "simulated_seller_risk"
                            ]
                        ),
                        "supplier_pressure_change": (
                            snapshot[
                                "simulated_seller_risk"
                            ]
                            - snapshot[
                                "baseline_seller_risk"
                            ]
                        ),
                        "supplier_state": (
                            snapshot["supplier_state"]
                        ),
                    },

                    "customer": {
                        "baseline_review_score": (
                            snapshot[
                                "baseline_review_score"
                            ]
                        ),
                        "current_review_score": (
                            snapshot[
                                "simulated_review_score"
                            ]
                        ),
                        "review_score_change": (
                            snapshot[
                                "simulated_review_score"
                            ]
                            - snapshot[
                                "baseline_review_score"
                            ]
                        ),
                        "customer_state": (
                            snapshot["customer_state"]
                        ),
                    },

                    "financial": {
                        "baseline_daily_revenue": (
                            snapshot[
                                "baseline_daily_revenue"
                            ]
                        ),
                        "current_daily_revenue": (
                            snapshot[
                                "simulated_daily_revenue"
                            ]
                        ),
                        "baseline_aov": (
                            snapshot["baseline_aov"]
                        ),
                        "current_aov": (
                            snapshot["simulated_aov"]
                        ),
                        "revenue_change_pct": (
                            (
                                snapshot[
                                    "simulated_daily_revenue"
                                ]
                                / snapshot[
                                    "baseline_daily_revenue"
                                ]
                            )
                            - 1
                        )
                        * 100
                        if snapshot[
                            "baseline_daily_revenue"
                        ]
                        else None,
                    },

                    "operational": {
                        "baseline_orders": (
                            snapshot["baseline_orders"]
                        ),
                        "current_orders": (
                            snapshot["simulated_orders"]
                        ),
                        "simulation_status": (
                            snapshot["simulation_status"]
                        ),
                        "event_id": snapshot["event_id"],
                        "snapshot_id": (
                            snapshot["snapshot_id"]
                        ),
                    },
                },

                "investigation_constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "root_cause_inferred": False,
                    "recommendation_generated": False,
                },
            }

            # Agent analysis
            finance_analysis = FinanceAgent().analyze(
                evidence_package
            )

            operations_analysis = (
                OperationsAgent().analyze(
                    evidence_package
                )
            )

            risk_analysis = RiskAgent().analyze(
                evidence_package
            )

            customer_analysis = CustomerAgent().analyze(
                evidence_package
            )

            evidence_package["agent_analysis"] = {
                "finance": finance_analysis,
                "operations": operations_analysis,
                "risk": risk_analysis,
                "customer": customer_analysis,
            }

            # Root cause analysis
            root_cause_analysis = RootCauseAnalyzer(
                self.db_path
            ).analyze(incident_id)

            evidence_package["root_cause_analysis"] = (
                root_cause_analysis
            )

            # Evidence synthesis
            evidence_package["evidence_synthesis"] = (
                EvidenceSynthesizer().synthesize(
                    evidence_package=evidence_package,
                    agent_analysis=(
                        evidence_package[
                            "agent_analysis"
                        ]
                    ),
                    root_cause_analysis=(
                        root_cause_analysis
                    ),
                )
            )

            # Debate
            debate = DebateEngine().debate(
                agent_analysis=(
                    evidence_package[
                        "agent_analysis"
                    ]
                ),
                root_cause_analysis=(
                    root_cause_analysis
                ),
                evidence_synthesis=(
                    evidence_package[
                        "evidence_synthesis"
                    ]
                ),
            )

            evidence_package["debate"] = debate

            # Decision
            decision = DecisionEngine().decide(
                evidence_synthesis=(
                    evidence_package[
                        "evidence_synthesis"
                    ]
                ),
                debate=evidence_package["debate"],
            )

            evidence_package["decision"] = decision

            # Decision validation
            decision_validation = (
                DecisionValidator().validate(
                    decision
                )
            )

            evidence_package[
                "decision_validation"
            ] = decision_validation

            # Remember → Learn → Quality → Adaptive
            if (
                decision_validation[
                    "validation_status"
                ]
                == "VALID"
            ):
                memory_id = save_decision_memory(
                    incident_id=incident_id,
                    snapshot_id=incident[
                        "snapshot_id"
                    ],
                    investigation_id=(
                        memory_investigation_id
                    ),
                    decision=decision,
                    decision_validation=(
                        decision_validation
                    ),
                )

                evidence_package[
                    "decision_memory_id"
                ] = memory_id

                learning = LearningEngine().learn(
                    investigation_id=(
                        memory_investigation_id
                    )
                )

                evidence_package["learning"] = (
                    learning
                )

                decision_quality = (
                    DecisionQualityEvaluator()
                    .evaluate(
                        investigation_id=(
                            memory_investigation_id
                        )
                    )
                )

                evidence_package[
                    "decision_quality"
                ] = decision_quality

                adaptive_intelligence = (
                    AdaptiveIntelligenceEngine()
                    .analyze(
                        db_path=self.db_path
                    )
                )

                evidence_package[
                    "adaptive_intelligence"
                ] = adaptive_intelligence

            else:
                evidence_package[
                    "adaptive_intelligence"
                ] = {
                    "adaptive_status": (
                        "DECISION_NOT_VALID"
                    ),
                    "observation_count": 0,
                    "insights": [],
                    "proposals": [],
                    "constraints": {
                        "deterministic": True,
                        "read_only": True,
                        "llm_used": False,
                        "business_facts_generated": (
                            False
                        ),
                        "rules_modified": False,
                        "thresholds_modified": (
                            False
                        ),
                    },
                    "provenance": {
                        "source": (
                            "DECISION_VALIDATION"
                        ),
                        "analysis_method": (
                            "ADAPTIVE_ANALYSIS_SKIPPED"
                        ),
                    },
                    "version": (
                        AdaptiveIntelligenceEngine.VERSION
                    ),
                }

            # Provenance
            evidence_package["provenance"] = {
                "historical_data": (
                    "OBSERVED_HISTORICAL"
                ),
                "inventory_level_and_coverage": (
                    "MODEL_DERIVED"
                ),
                "scenario_changes": "SIMULATED",
                "root_cause_interpretation": (
                    "DETERMINISTIC_RCA"
                ),
                "learning": (
                    "DETERMINISTIC_OBSERVED_OUTCOMES"
                ),
                "adaptive_intelligence": (
                    "DETERMINISTIC_READ_ONLY"
                ),
                "llm_used": False,
            }

            # LLM Interpretation
            #
            # This runs only after the deterministic
            # investigation is complete.
            #
            # It cannot modify any deterministic result.
            llm_interpretation = (
                self._run_llm_interpretation(
                    evidence_package
                )
            )

            evidence_package[
                "llm_interpretation"
            ] = llm_interpretation

            # Preserve deterministic provenance and
            # record the LLM interpretation separately.
            if (
                llm_interpretation[
                    "interpretation_status"
                ]
                == "INTERPRETATION_AVAILABLE"
            ):
                evidence_package[
                    "provenance"
                ]["llm_used"] = True

                evidence_package[
                    "provenance"
                ]["llm_interpretation"] = (
                    "LLM_EVIDENCE_INTERPRETATION"
                )

            else:
                evidence_package[
                    "provenance"
                ]["llm_interpretation"] = (
                    "UNAVAILABLE_OR_DISABLED"
                )

            return evidence_package

        finally:
            connection.close()


def main():
    engine = InvestigationEngine()

    incident_id = 1

    result = engine.investigate(incident_id)

    print("=" * 70)
    print("ORACLE-X INVESTIGATION ENGINE")
    print("=" * 70)

    print("\nINVESTIGATION")
    print("-" * 70)
    print(
        f"Investigation ID: "
        f"{result['investigation_id']}"
    )
    print(
        f"Incident ID: "
        f"{result['incident']['incident_id']}"
    )
    print(
        f"Incident Type: "
        f"{result['incident']['incident_type']}"
    )
    print(
        f"Severity: "
        f"{result['incident']['severity']}"
    )
    print(
        f"Source Type: "
        f"{result['incident']['source_type']}"
    )

    print("\nDEMAND EVIDENCE")
    print("-" * 70)

    demand = result["evidence"]["demand"]

    print(
        f"Baseline Daily Orders: "
        f"{demand['baseline_daily_orders']:.2f}"
    )
    print(
        f"Current Daily Orders: "
        f"{demand['current_daily_orders']:.2f}"
    )
    print(
        f"Demand Change: "
        f"{demand['demand_change_pct']:+.2f}%"
    )
    print(
        f"Demand State: "
        f"{demand['demand_state']}"
    )

    print("\nINVENTORY EVIDENCE")
    print("-" * 70)

    inventory = result["evidence"]["inventory"]

    print(
        f"Baseline Inventory Units: "
        f"{inventory['baseline_inventory_units']:.2f}"
    )
    print(
        f"Current Inventory Units: "
        f"{inventory['current_inventory_units']:.2f}"
    )
    print(
        f"Baseline Cover: "
        f"{inventory['baseline_cover_days']:.2f} days"
    )
    print(
        f"Current Cover: "
        f"{inventory['current_cover_days']:.2f} days"
    )
    print(
        f"Cover Decline: "
        f"{inventory['inventory_cover_decline_pct']:.2f}%"
    )
    print(
        f"Inventory State: "
        f"{inventory['inventory_state']}"
    )

    print("\nSUPPLIER EVIDENCE")
    print("-" * 70)

    supplier = result["evidence"]["supplier"]

    print(
        f"Baseline Seller Risk: "
        f"{supplier['baseline_seller_risk']:.2f}"
    )
    print(
        f"Current Seller Risk: "
        f"{supplier['current_seller_risk']:.2f}"
    )
    print(
        f"Supplier Pressure Change: "
        f"{supplier['supplier_pressure_change']:+.2f}"
    )
    print(
        f"Supplier State: "
        f"{supplier['supplier_state']}"
    )

    print("\nCUSTOMER EVIDENCE")
    print("-" * 70)

    customer = result["evidence"]["customer"]

    print(
        f"Baseline Review Score: "
        f"{customer['baseline_review_score']:.2f}"
    )
    print(
        f"Current Review Score: "
        f"{customer['current_review_score']:.2f}"
    )
    print(
        f"Review Score Change: "
        f"{customer['review_score_change']:+.2f}"
    )
    print(
        f"Customer State: "
        f"{customer['customer_state']}"
    )

    print("\nFINANCIAL EVIDENCE")
    print("-" * 70)

    financial = result["evidence"]["financial"]

    print(
        f"Baseline Daily Revenue: "
        f"${financial['baseline_daily_revenue']:,.2f}"
    )
    print(
        f"Current Daily Revenue: "
        f"${financial['current_daily_revenue']:,.2f}"
    )
    print(
        f"Revenue Change: "
        f"{financial['revenue_change_pct']:+.2f}%"
    )
    print(
        f"Baseline AOV: "
        f"${financial['baseline_aov']:,.2f}"
    )
    print(
        f"Current AOV: "
        f"${financial['current_aov']:,.2f}"
    )

    print("\nINVESTIGATION VALIDATION")
    print("-" * 70)

    constraints = result[
        "investigation_constraints"
    ]

    print(
        f"Deterministic: "
        f"{'YES' if constraints['deterministic'] else 'NO'}"
    )
    print(
        f"LLM Used: "
        f"{'YES' if constraints['llm_used'] else 'NO'}"
    )
    print(
        f"Root Cause Inferred: "
        f"{'YES' if constraints['root_cause_inferred'] else 'NO'}"
    )
    print(
        f"Recommendation Generated: "
        f"{'YES' if constraints['recommendation_generated'] else 'NO'}"
    )

    print("\nEVIDENCE SYNTHESIS")
    print("-" * 70)

    synthesis = result["evidence_synthesis"]

    print(
        f"Overall Assessment: "
        f"{synthesis['assessment']['overall_assessment']}"
    )
    print(
        f"Causal Certainty: "
        f"{synthesis['assessment']['causal_certainty']}"
    )

    print("\nCROSS-AGENT CONSENSUS")

    for item in synthesis[
        "cross_agent_consensus"
    ]:
        print(
            f"- {item['topic']}: "
            f"{item['finding']}"
        )

    print("\nUNRESOLVED QUESTIONS")

    for question in synthesis[
        "unresolved_questions"
    ]:
        print(f"- {question}")

    print("\nDEBATE")
    print("-" * 70)

    debate = result["debate"]

    print(
        f"Debate Status: "
        f"{debate['debate_status']}"
    )

    print("\nAgreements")

    for item in debate["agreements"]:
        print(
            f"- {item['topic']}: "
            f"{item['finding']}"
        )

    print("\nUnresolved Questions")

    for question in debate[
        "unresolved_questions"
    ]:
        print(f"- {question}")

    print("\nDECISION")
    print("-" * 70)

    decision = result["decision"]

    print(
        f"Decision Status: "
        f"{decision['decision_status']}"
    )
    print(
        f"Recommended Action: "
        f"{decision['recommended_action']}"
    )
    print(
        f"Rationale: "
        f"{decision['rationale']}"
    )

    print("\nDECISION VALIDATION")
    print("-" * 70)

    decision_validation = result[
        "decision_validation"
    ]

    print(
        f"Validation Status: "
        f"{decision_validation['validation_status']}"
    )
    print(
        f"Errors: "
        f"{decision_validation['errors']}"
    )

    print("\nLEARNING")
    print("-" * 70)

    learning = result.get("learning")

    if learning:
        print(
            f"Learning Status: "
            f"{learning['learning_status']}"
        )
        print(
            f"Learning Conclusion: "
            f"{learning['learning_conclusion']}"
        )
        print(
            f"Outcome Status: "
            f"{learning['outcome']['outcome_status']}"
        )
        print(
            f"Outcome ID: "
            f"{learning['outcome']['outcome_id']}"
        )
        print(
            f"Learning Signals: "
            f"{len(learning['learning_signals'])}"
        )
    else:
        print(
            "Learning was not executed because "
            "the decision was not valid."
        )

    print("\nDECISION QUALITY")
    print("-" * 70)

    decision_quality = result.get(
        "decision_quality"
    )

    if decision_quality:
        print(
            f"Quality: "
            f"{decision_quality['quality_status']}"
        )
        print(
            f"Score: "
            f"{decision_quality['quality_score']}"
        )
        print(
            f"Outcome: "
            f"{decision_quality['outcome_status']}"
        )
        print(
            f"Outcome ID: "
            f"{decision_quality['outcome_id']}"
        )
    else:
        print(
            "Decision quality was not evaluated "
            "because the decision was not valid."
        )

    print("\nADAPTIVE INTELLIGENCE")
    print("-" * 70)

    adaptive = result[
        "adaptive_intelligence"
    ]

    print(
        f"Status: "
        f"{adaptive['adaptive_status']}"
    )
    print(
        f"Observations: "
        f"{adaptive['observation_count']}"
    )
    print(
        f"Insights: "
        f"{len(adaptive['insights'])}"
    )
    print(
        f"Proposals: "
        f"{len(adaptive['proposals'])}"
    )
    print(
        f"Rules Modified: "
        f"{adaptive['constraints']['rules_modified']}"
    )
    print(
        f"Thresholds Modified: "
        f"{adaptive['constraints']['thresholds_modified']}"
    )

    for insight in adaptive["insights"]:
        print(
            f"- {insight['insight_type']}: "
            f"{insight['metric']}"
        )

    print("\nLLM INTERPRETATION")
    print("-" * 70)

    llm_result = result[
        "llm_interpretation"
    ]

    print(
        f"Status: "
        f"{llm_result['interpretation_status']}"
    )

    if (
        llm_result["interpretation_status"]
        == "INTERPRETATION_AVAILABLE"
    ):
        print(
            f"Model: "
            f"{llm_result['model']}"
        )

        interpretation = (
            llm_result["interpretation"]
        )

        print(
            f"Executive Summary: "
            f"{interpretation['executive_summary']}"
        )

        print(
            f"Key Observations: "
            f"{len(interpretation['key_observations'])}"
        )

        print(
            f"Uncertainty Items: "
            f"{len(interpretation['uncertainty'])}"
        )

        print(
            f"Unresolved Questions: "
            f"{len(interpretation['unresolved_questions'])}"
        )

        print(
            f"Limitations: "
            f"{len(interpretation['limitations'])}"
        )

    elif (
        llm_result["interpretation_status"]
        == "INTERPRETATION_UNAVAILABLE"
    ):
        print(
            f"Error Type: "
            f"{llm_result['error_type']}"
        )
        print(
            f"Error: "
            f"{llm_result['error']}"
        )

    print("\nPROVENANCE")
    print("-" * 70)

    print(
        f"Historical Data: "
        f"{result['provenance']['historical_data']}"
    )
    print(
        f"Inventory: "
        f"{result['provenance']['inventory_level_and_coverage']}"
    )
    print(
        f"Scenario Changes: "
        f"{result['provenance']['scenario_changes']}"
    )
    print(
        f"Root Cause: "
        f"{result['provenance']['root_cause_interpretation']}"
    )
    print(
        f"Learning: "
        f"{result['provenance']['learning']}"
    )
    print(
        f"Adaptive Intelligence: "
        f"{result['provenance']['adaptive_intelligence']}"
    )
    print(
        f"LLM Used: "
        f"{result['provenance']['llm_used']}"
    )
    print(
        f"LLM Interpretation: "
        f"{result['provenance']['llm_interpretation']}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()