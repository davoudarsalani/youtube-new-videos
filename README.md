# Check out a YouTube channel for new videos currently only using google-api-python-client python module
<div align='center'>
<img alt='last-commit' src='https://img.shields.io/github/last-commit/davoudarsalani/youtube-new-videos?&labelColor=black&color=grey&style=flat'>
<img alt='commit-activity' src='https://img.shields.io/github/commit-activity/m/davoudarsalani/youtube-new-videos?&labelColor=black&color=grey&style=flat'>
</div>
<br>

```yml
- name: Checkout repo
  uses: actions/checkout@v2

- name: Checking for new videos
  uses: ./.github/actions/google-api-python-client
  with:
    owner:
    channel_id:
    google_api: ${{ secrets.GOOGLE_API }}
    TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
    TELEGRAM_TO: ${{ secrets.TELEGRAM_TO }}
```
