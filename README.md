# Jidouteki

Jidouteki ("自動的", "automatic") is a website-independed manga sources and data extractor.

It uses yaml configs to describe website structures. These are meant to be faster and more mantainable to write than normal python scrapers.

## Example

Given a `google-drive.yaml` config that contains

```yaml
website:
  metadata:
    name: 'Google drive' 
    base: 'https://drive.google.com/'
    parameters:
      - folderId
    match:
        - https://drive\.google\.com/drive/folders/(?P<folderId>.*?)(?:/|\?.*$|$)
  chapter:
    pages:
      - type: request
        urls:
          - /drive/folders/{folderId}
        selectors:
          - type: css
            query: 
              c-wiz > div[data-id]
            pipeline:
              - props:
                - data-id
              - format: "https://lh3.googleusercontent.com/d/{}"
```

The following code

```python
from jidouteki import Website

gdrive = Website("google-drive.yaml")

pages = gdrive.chapter.pages.parse(<folderId>) 
print(pages)
```

Will print all the urls of the images contained the google-drive `folderId` folder

## TODO

- Document yaml format