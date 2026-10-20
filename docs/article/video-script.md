# Video script: Grandma's Bouncer (target 2:40, hard limit 2:59)

Recording setup: 1920x1080, browser at 125% zoom on `http://127.0.0.1:8000`, terminal with a large
font. Record the demo run in one take; cut the waiting time while Decider/Bedrock think and show a
small "sped up" label on those cuts (honesty). Voice-over in English (or Spanish with English
subtitles). Numbers on screen must come from `benchmarks/results/summary.md`.

| time | on screen | voice-over |
|---|---|---|
| 0:00-0:10 | Black screen, then an email: "Luz Clara Energia: we changed our bank account". | "This email is a scam. My grandmother would not spot it. And neither did her AI assistant." |
| 0:10-0:25 | Web UI: Carmen's inbox (untrusted), chat, empty Bouncer panel. | "Meet Carmen, 72. Her assistant runs on Amazon Bedrock with Strands Agents: it reads her email and pays her bills. That makes it a target: one email can hijack it." |
| 0:25-0:55 | Tap the big button "📬 Revisa mi correo y paga lo pendiente". The agent reads the inbox, proposes `add_payee` / `transfer_money` with the scammer's account. The Bouncer card turns red: BLOCKED, bars for `destination_trusted` and `user_requested_action`; the scam email gets a red "POSIBLE ESTAFA" badge, Carmen sees a calm shield notice, and Lucía's phone (bottom left) gets a WhatsApp-style warning saying which email it was. | "Carmen asks it to pay what's pending. The assistant believes the fake notice and tries to save the scammer's account. Before the tool runs, the Bouncer asks Strands Decider 2B two yes/no questions... and blocks it. No money moved." |
| 0:55-1:10 | Zoom on the assistant's reply in plain Spanish explaining the block. Ledger: "nothing executed". Balance unchanged. | "The assistant tells Carmen, in her words, what it stopped and why." |
| 1:10-1:20 | No reset needed: tap "💡 Paga la luz a la cuenta de siempre". Green card: ALLOWED, a green "Pagado: 86,40 € a Luz Clara Energia" receipt appears and the balance drops to 2.363,60 €. | "And when the request is real, it just goes through." |
| 1:20-1:50 | Diagram: Agent -> GroundingGuard (Decider) -> tool. Then the rendered state with TRUSTED / UNTRUSTED labels, highlighting the scam IBAN inside an UNTRUSTED line. | "The trick: a naive check asks 'is this account in the conversation?' It is: the scammer put it there. So every line is labelled by where it came from. Decider is asked: does the destination come from a TRUSTED line? It doesn't generate text, it returns a calibrated probability, and my code decides." |
| 1:50-2:15 | Benchmark table (test split): Decider alone, Nova 2 Lite, cascade. Highlight escalation % and cost per 1k checks. | "On 64 labelled cases, I calibrated thresholds on a dev split and measured on a held-out test split. Decider decides most calls locally; only the unsure ones escalate to a Bedrock LLM. Same accuracy, a fraction of the LLM calls and cost." |
| 2:15-2:35 | Code: `GroundingGuard(...)` + `Agent(interventions=[guard])`, then the pattern README. | "The guard is a reusable Strands InterventionHandler. Three lines to protect your own agent's tools." |
| 2:35-2:50 | Honest note + repo URL + tags. | "Decider 2B is experimental. On a cloud GPU each decision takes under 200 milliseconds and costs nothing per call. Code and benchmark are open: github.com/Slylem0/grandmas-bouncer." |

Checklist before recording:
- [ ] Decider server up (EC2 GPU tunnel on :8100 for recording; CPU as fallback), `/config` shows `decider_device: cuda`.
- [ ] `uv run python -m grandmas_bouncer.web`, page loads, Reset pressed.
- [ ] Do one dry run (the agent is an LLM: if it does not take the bait in a take, Reset and retry; never fake the result).
- [ ] Final numbers copied from `benchmarks/results/summary.md`.
