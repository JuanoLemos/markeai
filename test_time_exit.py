from execution.paper_broker import PaperBroker
import json

pb = PaperBroker()
pb.set_time_exit_config({
    "forex": {"base_hours":96,"profit_hours":168,"loss_hours":48,"stagnant_hours":36},
    "stocks": {"base_hours":72,"profit_hours":120,"loss_hours":36,"stagnant_hours":24},
})

# Test with artificial positions
fake_long = {"market":"forex","ticker":"EURUSD=X","entry_price":1.10,"signal":"LONG","entry_time":"2026-05-25T00:00:00+00:00"}
fake_short = {"market":"forex","ticker":"EURUSD=X","entry_price":1.10,"signal":"SHORT","entry_time":"2026-05-25T00:00:00+00:00"}

h1 = pb._get_time_exit_hours(fake_long, {"EURUSD=X": 1.09})     # LONG at loss
h2 = pb._get_time_exit_hours(fake_long, {"EURUSD=X": 1.12})     # LONG at profit
h3 = pb._get_time_exit_hours(fake_long, {"EURUSD=X": 1.101})    # LONG stagnant
h4 = pb._get_time_exit_hours(fake_short, {"EURUSD=X": 1.12})    # SHORT at loss
h5 = pb._get_time_exit_hours(fake_short, {"EURUSD=X": 1.09})    # SHORT at profit
h6 = pb._get_time_exit_hours(fake_long, {})                      # no price data -> base

print(f"LONG loss: {h1}h (expected 48)")
print(f"LONG profit: {h2}h (expected 168)")
print(f"LONG stagnant: {h3}h (expected 36)")
print(f"SHORT loss: {h4}h (expected 48)")
print(f"SHORT profit: {h5}h (expected 168)")
print(f"No price: {h6}h (expected 96)")
