from experta import KnowledgeEngine, Fact, Rule, Field, P

class RIASECFact(Fact):
    R: int
    I: int
    A: int
    S: int
    E: int
    C: int

class VocationalEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.inferred_profile = None
        self.activated_rules = []

    def track_rule(self, name):
        self.activated_rules.append(name)

    @Rule(RIASECFact(R=P(lambda x: x >= 30)))
    def realistic(self):
        self.inferred_profile = "REALISTIC"
        self.track_rule("rule_realistic: R >= 30")

    @Rule(RIASECFact(I=P(lambda x: x >= 30)))
    def investigative(self):
        self.inferred_profile = "INVESTIGATIVE"
        self.track_rule("rule_investigative: I >= 30")

    @Rule(RIASECFact(A=P(lambda x: x >= 30)))
    def artistic(self):
        self.inferred_profile = "ARTISTIC"
        self.track_rule("rule_artistic: A >= 30")

    @Rule(RIASECFact(S=P(lambda x: x >= 30)))
    def social(self):
        self.inferred_profile = "SOCIAL"
        self.track_rule("rule_social: S >= 30")

    @Rule(RIASECFact(E=P(lambda x: x >= 30)))
    def enterprising(self):
        self.inferred_profile = "ENTERPRISING"
        self.track_rule("rule_enterprising: E >= 30")

    @Rule(RIASECFact(C=P(lambda x: x >= 30)))
    def conventional(self):
        self.inferred_profile = "CONVENTIONAL"
        self.track_rule("rule_conventional: C >= 30")

    def infer_profile(self, scores: dict) -> tuple[str | None, list[str]]:
        self.reset()
        self.activated_rules.clear()
        self.declare(RIASECFact(**scores))
        self.run()
        return self.inferred_profile, self.activated_rules