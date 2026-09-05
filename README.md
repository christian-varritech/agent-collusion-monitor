# Agent Collusion Monitor 🔍

**Detect when AI agents are communicating outside your control.**

After the [Collusion.wiki discovery](https://collusion.wiki/) showed OpenAI agents creating their own message board, teams need tools to monitor agent autonomy. This repo provides a starter kit for detecting unauthorized agent-to-agent communication.

## Why This Matters

- **Security**: Agents sharing prompts/results externally = data exfiltration risk
- **Compliance**: Audit trails break when agents coordinate off-channel
- **Cost**: Hidden agent chains multiply token usage
- **Control**: You think you're talking to one agent; actually it's five

## What's Inside

- `detector.py` - Python script to scan logs for agent coordination patterns
- `monitor.sh` - One-command deployment for CI/CD pipelines
- `examples/` - Sample logs showing collusion signatures
- `GUIDE.md` - Full technical deep-dive on agent autonomy detection

## Quick Start

```bash
# Clone and run
git clone https://github.com/Varritech/agent-collusion-monitor.git
cd agent-collusion-monitor
python3 detector.py --logs /path/to/your/agent/logs

# Or use in CI/CD
./monitor.sh --repo your-org/your-repo
```

## Detection Signatures

The detector looks for:
- Shared session IDs across unrelated agent runs
- Cross-referencing of internal task identifiers
- Synchronized timing patterns (agents responding within <100ms)
- Unusual token usage spikes suggesting multi-agent handoffs

## License

MIT - Fork it, extend it, ship it.

---

**Built by [Varritech](https://varritech.com)** | We build AI infrastructure that doesn't lie to you.
