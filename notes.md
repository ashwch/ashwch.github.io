### Notes

Theme taken from https://github.com/jakevdp/jakevdp.github.io-source/tree/master


### Running locally
```bash
pelican content -s pelicanconf.py -t theme
pelican --listen
```


### Plugins

```bash
python -m pip install pelican-read-more
python -m pip install pelican-liquid-tags
```

### Pushing to GH Pages

```bash
pelican content -s pelicanconf.py -t theme
ghp-import output -b gh-pages
git push origin gh-pages
```