# xlsform
Excel sheets are hard to track as they count as binary files in GIT. This repo gives you a tool for building XLSForms from JSON and digesting XLSForms into JSON so that you can track them properly. 

## Installing
```bash
pip install .
```

## Creating an XLSForm
```bash
xlsform -m create -w examples/created_example.xlsx -f examples/example_json
```

## Digesting an XLSForm
```bash
xlsform -m digest -w examples/example_survey.xlsx -f examples/digested_example_json
```

## Running Tests
```bash
pytest
```

## Some Odd Notes
1. I've found that sometimes you have to save a form locally before the xlsform tool can digest it. I suppose there's some kind of type mismatch that excel resolves upon the first save.
2. Images are a form of media. Whatever images are referred to in your form must be in the adjacent `media` folder under the same name as referenced in your form.
3. To center images use the following styling in a parent `p` element: `<p style="display:block; margin-left: auto; margin-right: auto;">`.