from ._base import BaseAnalyzer


class OnChainAnalyzer(BaseAnalyzer):
    WHALE_THRESHOLD_USD = 10000

    def analyze(self, polymarket_data: dict = None) -> dict:
        if not polymarket_data:
            return self.empty_result()

        signals = []
        scores = []
        onchain = polymarket_data.get("onchain_data") or {}

        if onchain:
            return self._analyze_onchain(onchain, signals, scores, polymarket_data)

        return self._analyze_trade_only(polymarket_data, signals, scores)

    def _analyze_onchain(self, onchain: dict, signals: list, scores: list, raw: dict) -> dict:
        inflow_usd = onchain.get("inflow_usd", 0)
        outflow_usd = onchain.get("outflow_usd", 0)
        inflow_count = onchain.get("inflow_count", 0)
        outflow_count = onchain.get("outflow_count", 0)
        unique = onchain.get("unique_addresses", 0)
        net = onchain.get("net_usd", 0)

        if inflow_count >= 5:
            signals.append(f"high_inflows_{inflow_count}")
            scores.append(65)
        elif inflow_count >= 2:
            signals.append(f"inflows_{inflow_count}")
            scores.append(55)

        if outflow_count >= 5:
            signals.append(f"high_outflows_{outflow_count}")
            scores.append(35)
        elif outflow_count >= 2:
            signals.append(f"outflows_{outflow_count}")
            scores.append(45)

        if inflow_usd > outflow_usd * 2 and inflow_usd > self.WHALE_THRESHOLD_USD:
            signals.append(f"net_inflow_{net:.0f}")
            scores.append(70)
        elif outflow_usd > inflow_usd * 2 and outflow_usd > self.WHALE_THRESHOLD_USD:
            signals.append(f"net_outflow_{net:.0f}")
            scores.append(30)

        if unique >= 50:
            signals.append(f"active_wallets_{unique}")
            scores.append(60)
        elif unique >= 10:
            signals.append(f"moderate_wallets_{unique}")
            scores.append(55)
        elif unique <= 3:
            signals.append(f"low_activity_{unique}")
            scores.append(45)

        trade_vol = raw.get("market_details", {}).get("volume24hr", 0) or 0
        try:
            tv = float(trade_vol)
            if tv > 100000:
                signals.append(f"high_volume_{tv:.0f}")
                scores.append(60)
            elif tv > 10000:
                signals.append(f"volume_{tv:.0f}")
                scores.append(55)
        except (ValueError, TypeError):
            pass

        if not scores:
            return self._empty_result()

        avg_score = sum(scores) / len(scores)
        signal = "LONG" if avg_score >= 55 else "SHORT" if avg_score <= 45 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals),
            "details": {
                "inflow_usd": inflow_usd,
                "outflow_usd": outflow_usd,
                "net_usd": net,
                "unique_addresses": unique,
                "whale_transfers": inflow_count + outflow_count,
            },
        }

    def _analyze_trade_only(self, raw: dict, signals: list, scores: list) -> dict:
        trade_history = raw.get("trade_history", [])
        if trade_history:
            large = [t for t in trade_history if float(t.get("size", 0)) > 1000]
            if large:
                yes = sum(1 for t in large if t.get("side") == "BUY")
                no = sum(1 for t in large if t.get("side") == "SELL")
                if yes > no * 2:
                    signals.append("whale_accumulation")
                    scores.append(70)
                elif no > yes * 2:
                    signals.append("whale_distribution")
                    scores.append(30)
        details = raw.get("market_details", {})
        vol_24h = float(details.get("volume24hr", 0) or 0)
        if vol_24h > 0:
            ls = min(vol_24h / 100000, 1) * 20
            scores.append(50 + ls)
            signals.append(f"volume_24h_{vol_24h:.0f}")
        else:
            scores.append(50)
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "no_onchain_data",
            "details": {
                "volume_24h": vol_24h,
                "large_trades": len([t for t in trade_history if float(t.get("size", 0)) > 1000]) if trade_history else 0,
            },
        }

