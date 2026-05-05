class MacroAnalyzer:
    def analyze(self, dxy: float = None, vix: float = None, market_type: str = "forex") -> dict:
        signals = []
        scores = []
        if market_type == "forex" and dxy is not None:
            if dxy > 105:
                signals.append(f"dxy_strong_{dxy:.1f}")
                scores.append(60)
            elif dxy < 100:
                signals.append(f"dxy_weak_{dxy:.1f}")
                scores.append(40)
            else:
                signals.append(f"dxy_neutral_{dxy:.1f}")
                scores.append(50)
        if vix is not None:
            if vix < 15:
                signals.append(f"vix_low_{vix:.1f}")
                scores.append(55)
            elif vix > 25:
                signals.append(f"vix_elevated_{vix:.1f}")
                scores.append(35)
            elif vix > 30:
                signals.append(f"vix_high_{vix:.1f}")
                scores.append(25)
            else:
                signals.append(f"vix_normal_{vix:.1f}")
                scores.append(50)
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "macro_neutral",
            "details": {
                "dxy": dxy,
                "vix": vix,
            },
        }
