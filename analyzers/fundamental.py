from datetime import datetime, timezone


class FundamentalAnalyzer:
    def analyze(self, ticker: str = "", price_data: dict = None, fund_data: dict = None) -> dict:
        if fund_data:
            if self._is_etf(fund_data):
                return self._analyze_etf(ticker, price_data, fund_data)
            return self._analyze_fundamentals(ticker, price_data, fund_data)
        if not price_data:
            return self._empty_result()
        return self._analyze_volume_only(price_data)

    def _is_etf(self, fund_data: dict) -> bool:
        qt = fund_data.get("quoteType", "")
        if qt in ("ETF", "MUTUALFUND"):
            return True
        if not qt and not fund_data.get("trailingPE") and not fund_data.get("marketCap"):
            return True
        return False

    def _analyze_fundamentals(self, ticker: str, price_data: dict, fund: dict) -> dict:
        signals = []
        adjustments = []

        trailingPE = fund.get("trailingPE")
        forwardPE = fund.get("forwardPE")
        market_cap = fund.get("marketCap")
        div_yield = fund.get("dividendYield")
        beta = fund.get("beta")
        avg_vol = fund.get("averageVolume")
        volume_24h = price_data.get("volume_24h", 0) if price_data else 0
        pb = fund.get("priceToBook")

        if trailingPE is not None and trailingPE > 0:
            if trailingPE < 15:
                signals.append(f"pe_low_{trailingPE:.1f}")
                adjustments.append(15)
            elif trailingPE < 20:
                signals.append(f"pe_fair_{trailingPE:.1f}")
                adjustments.append(5)
            elif trailingPE < 30:
                signals.append(f"pe_premium_{trailingPE:.1f}")
                adjustments.append(-5)
            else:
                signals.append(f"pe_high_{trailingPE:.1f}")
                adjustments.append(-15)
            if forwardPE and forwardPE > 0 and trailingPE > 0:
                pe_diff = round((forwardPE - trailingPE) / trailingPE * 100, 1)
                if pe_diff < -10:
                    signals.append(f"forward_pe_improving_{pe_diff:.0f}%")
                    adjustments.append(5)
                elif pe_diff > 10:
                    signals.append(f"forward_pe_deteriorating_{pe_diff:.0f}%")
                    adjustments.append(-5)

        if market_cap is not None:
            if market_cap >= 2e11:
                signals.append(f"mega_cap")
                adjustments.append(5)
            elif market_cap >= 1e10:
                signals.append(f"large_cap")
                adjustments.append(0)
            elif market_cap >= 2e9:
                signals.append(f"mid_cap")
                adjustments.append(-5)
            else:
                signals.append(f"small_cap")
                adjustments.append(-10)

        if div_yield is not None and div_yield > 0:
            dy_pct = div_yield
            if dy_pct >= 3:
                signals.append(f"high_yield_{dy_pct:.1f}%")
                adjustments.append(10)
            elif dy_pct >= 1:
                signals.append(f"mod_yield_{dy_pct:.1f}%")
                adjustments.append(5)

        if beta is not None:
            if beta > 1.5:
                signals.append(f"high_beta_{beta:.1f}")
                adjustments.append(5)
            elif beta < 0.5:
                signals.append(f"low_beta_{beta:.1f}")
                adjustments.append(-5)

        if avg_vol and volume_24h > 0:
            vol_ratio = volume_24h / avg_vol
            if vol_ratio > 2:
                signals.append(f"volume_spike_{vol_ratio:.1f}x")
                adjustments.append(5)
            elif vol_ratio < 0.5:
                signals.append(f"volume_low_{vol_ratio:.1f}x")
                adjustments.append(-5)

        if pb is not None and pb > 0:
            if pb < 1.5:
                signals.append(f"pb_low_{pb:.1f}")
                adjustments.append(5)
            elif pb > 5:
                signals.append(f"pb_high_{pb:.1f}")
                adjustments.append(-5)

        earnings_date = fund.get("earningsDate")
        if earnings_date:
            try:
                ed = datetime.fromisoformat(str(earnings_date).replace("Z", "+00:00"))
                days_to = (ed - datetime.now(timezone.utc)).days
                if 0 <= days_to <= 7:
                    signals.append(f"earnings_in_{days_to}d")
                    adjustments.append(-5)
                elif 7 < days_to <= 30:
                    signals.append(f"earnings_{days_to}d_away")
                    adjustments.append(0)
            except (ValueError, TypeError):
                pass

        if not adjustments:
            return self._empty_result()

        raw_score = 50 + sum(adjustments)
        final_score = max(0, min(100, raw_score))
        signal = "LONG" if final_score >= 55 else "SHORT" if final_score <= 45 else "WAIT"

        return {
            "signal": signal,
            "score": round(float(final_score), 1),
            "reasoning": "; ".join(signals) if signals else "fundamental_neutral",
            "details": {
                "adjustments": adjustments,
                "total_delta": sum(adjustments),
                "raw_score": raw_score,
                "fund_data": {
                    k: v for k, v in fund.items()
                    if k in ("trailingPE", "forwardPE", "marketCap", "dividendYield", "beta", "averageVolume", "priceToBook")
                },
            },
        }

    def _analyze_etf(self, ticker: str, price_data: dict, fund_data: dict) -> dict:
        signals = []
        adjustments = []

        aum = fund_data.get("totalAssets")
        if aum is not None:
            if aum > 10e9:
                signals.append(f"large_aum_{aum/1e9:.1f}B")
                adjustments.append(10)
            elif aum > 500e6:
                signals.append(f"mid_aum_{aum/1e6:.0f}M")
                adjustments.append(5)
            elif aum < 100e6:
                signals.append(f"small_aum_{aum/1e6:.0f}M")
                adjustments.append(-5)

        expense = fund_data.get("expenseRatio")
        if expense is not None:
            if expense <= 0.001:
                signals.append(f"ultra_low_fee_{expense*100:.2f}%")
                adjustments.append(10)
            elif expense <= 0.005:
                signals.append(f"low_fee_{expense*100:.2f}%")
                adjustments.append(5)
            elif expense > 0.01:
                signals.append(f"high_fee_{expense*100:.2f}%")
                adjustments.append(-5)

        ytd = fund_data.get("ytdReturn")
        if ytd is not None:
            if ytd > 0.10:
                signals.append(f"strong_ytd_{ytd*100:.0f}%")
                adjustments.append(10)
            elif ytd > 0.05:
                signals.append(f"positive_ytd_{ytd*100:.0f}%")
                adjustments.append(5)
            elif ytd > 0:
                signals.append(f"slight_ytd_{ytd*100:.0f}%")
                adjustments.append(2)
            elif ytd < -0.10:
                signals.append(f"weak_ytd_{ytd*100:.0f}%")
                adjustments.append(-10)
            elif ytd < -0.05:
                signals.append(f"negative_ytd_{ytd*100:.0f}%")
                adjustments.append(-5)

        avg_vol = fund_data.get("averageVolume")
        volume_24h = price_data.get("volume_24h", 0) if price_data else 0
        if avg_vol and volume_24h > 0:
            vol_ratio = volume_24h / avg_vol
            if vol_ratio > 2:
                signals.append(f"volume_spike_{vol_ratio:.1f}x")
                adjustments.append(5)
            elif vol_ratio > 1.5:
                signals.append(f"volume_above_avg_{vol_ratio:.1f}x")
                adjustments.append(3)
            elif vol_ratio < 0.5:
                signals.append(f"volume_low_{vol_ratio:.1f}x")
                adjustments.append(-3)

        change = price_data.get("change_24h_pct", 0) if price_data else 0
        if change > 3:
            signals.append(f"strong_up_{change:.1f}%")
            adjustments.append(5)
        elif change > 1:
            signals.append(f"up_{change:.1f}%")
            adjustments.append(3)
        elif change < -3:
            signals.append(f"strong_down_{change:.1f}%")
            adjustments.append(-5)
        elif change < -1:
            signals.append(f"down_{change:.1f}%")
            adjustments.append(-3)

        curr_price = price_data.get("price", 0) if price_data else 0
        high52 = fund_data.get("fiftyTwoWeekHigh")
        low52 = fund_data.get("fiftyTwoWeekLow")
        if curr_price and high52 and low52 and high52 > low52:
            range_pos = (curr_price - low52) / (high52 - low52)
            if range_pos > 0.90:
                signals.append(f"near_52w_high_{range_pos:.0%}")
                adjustments.append(8)
            elif range_pos > 0.75:
                signals.append(f"above_75pct_{range_pos:.0%}")
                adjustments.append(3)
            elif range_pos < 0.10:
                signals.append(f"near_52w_low_{range_pos:.0%}")
                adjustments.append(-8)
            elif range_pos < 0.25:
                signals.append(f"below_25pct_{range_pos:.0%}")
                adjustments.append(-3)

        if not adjustments:
            return self._empty_result()

        raw_score = 50 + sum(adjustments)
        final_score = max(0, min(100, raw_score))
        signal = "LONG" if final_score >= 55 else "SHORT" if final_score <= 45 else "WAIT"

        return {
            "signal": signal,
            "score": round(float(final_score), 1),
            "reasoning": "; ".join(signals) if signals else "etf_neutral",
            "details": {
                "adjustments": adjustments,
                "total_delta": sum(adjustments),
                "raw_score": raw_score,
                "type": "etf",
            },
        }

    def _analyze_volume_only(self, price_data: dict) -> dict:
        signals = []
        scores = []
        volume = price_data.get("volume_24h", 0)
        avg_volume = price_data.get("avg_volume_20d", volume)
        if avg_volume > 0:
            vol_ratio = volume / avg_volume
            if vol_ratio > 2.0:
                signals.append(f"volume_spike_{vol_ratio:.1f}x")
                scores.append(65)
            elif vol_ratio > 1.5:
                signals.append(f"volume_above_avg_{vol_ratio:.1f}x")
                scores.append(55)
            elif vol_ratio < 0.5:
                signals.append(f"volume_low_{vol_ratio:.1f}x")
                scores.append(45)
            else:
                signals.append(f"volume_normal_{vol_ratio:.1f}x")
                scores.append(50)
        change = price_data.get("change_24h_pct", 0)
        if abs(change) > 3:
            if change > 0:
                signals.append(f"strong_up_day_{change:.1f}%")
                scores.append(35)
            else:
                signals.append(f"strong_down_day_{change:.1f}%")
                scores.append(65)
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "fundamental_neutral",
            "details": {
                "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 0,
                "change_24h_pct": change,
            },
        }

    def _empty_result(self):
        return {"signal": "WAIT", "score": 50, "reasoning": "no_fundamental_data", "details": {}}
