# Rounded Currency Converter

A simple Streamlit app that converts currencies and shows two results:

1. the exact converted value
2. the rounded value

The default rounding mode rounds **up to the nearest whole currency unit**, matching the original idea of showing a cleaner rounded result after conversion.

## Features

- Live exchange rates through the Frankfurter API
- No API key required
- Exact converted amount
- Rounded converted amount
- Multiple rounding modes:
  - round up to nearest whole unit
  - round to nearest whole unit
  - round up to nearest 0.05
  - round up to nearest 0.10
  - smart price ending `.99`
  - custom round-up step
- Streamlit Community Cloud ready

## Project files

```text
rounded_currency_converter/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload these files to the repository.
3. Go to Streamlit Community Cloud.
4. Choose the repository, branch, and `app.py` as the entry file.
5. Click **Deploy**.

No secrets are needed because the app uses a public no-key API.

## Notes

Frankfurter rates are reference exchange rates. They are useful for general conversion, but they may not match bank, card, or money-transfer rates exactly.
