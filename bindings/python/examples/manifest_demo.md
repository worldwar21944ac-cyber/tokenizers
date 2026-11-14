# Manifest validation demo

This standalone Python 3.10+ example demonstrates **structural JSON validation** and optional tokenization using the Python binding API already documented in this repository. It does not train a tokenizer, determine whether an institution is distressed, perform KYC, validate Stripe/webhook signatures, move money, or establish legal/compliance status. Tokenization is not a security or policy enforcement mechanism.

## Run the demo and tests

From `bindings/python`:

```bash
python examples/manifest_demo.py --demo
python examples/manifest_demo.py --self-test
```

Validate a JSON file and optionally pin its expected version:

```bash
python examples/manifest_demo.py manifest.json --expected-version 2026.11.02-sovereign-v1
```

To inspect token IDs and pieces too, install/build this repository's Python binding and pass a local tokenizer JSON:

```bash
python examples/manifest_demo.py --demo --tokenizer path/to/tokenizer.json
```

The `--tokenizer` path is an existing tokenizer artifact. This example deliberately does not claim that the current binding can train a tokenizer or expose APIs that are still on the project roadmap. See [`../README.md`](../README.md) for supported Python binding behavior.
