from ._base import BaseAnalyzer


class OrderBookAnalyzer(BaseAnalyzer):
    def analyze(self, order_book: dict) -> dict:
        if not order_book or "error" in order_book:
            return self.empty_result()
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        if not bids or not asks:
            return self.empty_result()
        bid_volume = sum(float(b.get("size", 0)) for b in bids)
        ask_volume = sum(float(a.get("size", 0)) for a in asks)
        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return self.empty_result()
        imbalance = bid_volume / ask_volume if ask_volume > 0 else 999
        best_bid = float(bids[0].get("price", 0))
        best_ask = float(asks[0].get("price", 0))
        spread = best_ask - best_bid
        spread_pct = (spread / best_ask * 100) if best_ask > 0 else 0
        depth_5_bid = sum(float(b.get("size", 0)) for b in bids[:5])
        depth_5_ask = sum(float(a.get("size", 0)) for a in asks[:5])
        depth_ratio = depth_5_bid / depth_5_ask if depth_5_ask > 0 else 999
        signals = []
        scores = []
        if imbalance > 2.0:
            signals.append(f"heavy_bid_side_{imbalance:.1f}x")
            scores.append(70)
        elif imbalance > 1.5:
            signals.append(f"bid_dominated_{imbalance:.1f}x")
            scores.append(60)
        elif imbalance < 0.5:
            signals.append(f"heavy_ask_side_{imbalance:.1f}x")
            scores.append(30)
        elif imbalance < 0.67:
            signals.append(f"ask_dominated_{imbalance:.1f}x")
            scores.append(40)
        else:
            signals.append(f"balanced_{imbalance:.1f}x")
            scores.append(50)
        if spread_pct < 0.1:
            scores.append(60)
            signals.append("tight_spread")
        elif spread_pct > 1.0:
            scores.append(40)
            signals.append("wide_spread")
        if depth_ratio > 2.0:
            scores.append(65)
            signals.append(f"bid_depth_{depth_ratio:.1f}x")
        elif depth_ratio < 0.5:
            scores.append(35)
            signals.append(f"ask_depth_{depth_ratio:.1f}x")
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals),
            "details": {
                "bid_volume": round(bid_volume, 2),
                "ask_volume": round(ask_volume, 2),
                "imbalance": round(imbalance, 2),
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread_pct": round(spread_pct, 3),
                "depth_ratio_5": round(depth_ratio, 2),
            },
        }

