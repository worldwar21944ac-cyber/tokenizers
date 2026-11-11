# Tokenizer Studio

A static, browser-based tokenizer playground powered by the repository's `tokenizers-wasm` package. It lets you load a public Hugging Face tokenizer, encode text, inspect token strings and IDs, and decode the result. Tokenization runs locally in WebAssembly; model files are downloaded from the Hugging Face Hub.

## Run locally

Serve this directory over HTTP (ES modules and WebAssembly do not work reliably from `file://` URLs):

```bash
cd apps/tokenizer-studio
python3 -m http.server 8000
```

Open <http://localhost:8000>. The app imports `tokenizers-wasm` from esm.sh on first load, so an internet connection is required. Model loading also needs access to the Hub. Recent browsers with WebAssembly SIMD support are required; see [the WASM binding requirements](../../bindings/wasm/README.md#requirements).

## Features

- Load public models by Hugging Face model ID, with GPT-2, BERT, and RoBERTa shortcuts.
- Encode sample or custom text and inspect token pieces alongside their token IDs.
- View the complete token ID array, decode tokens back to text, and copy IDs.
- Responsive layout, keyboard shortcut (`Ctrl`/`⌘` + `Enter`), and safe text rendering.

No application backend is used. Text entered into the app is passed to the tokenizer in your browser; selected tokenizer files are fetched from the Hugging Face Hub.
