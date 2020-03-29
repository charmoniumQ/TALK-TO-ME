# TALK TO ME!!

## What does this actually do?

It aggregates the things you have said in response to other people,
gives you some statistics, tries to train a chat bot, and crashes.

Maybe eventually, it will not crash.

## Installation instructions

1. Clone the repo.
2. [Download your fb data][1] with these options:
  - date_range: all
  - format: JSON
  - quality: low
  - files:
    - messages
3. Place the unmodified zip here.
4. Modify, read, and run `main.sh` (modify the last line).
5. To hack on this, run `devmain.sh` instead. If you have already run
   `main.sh`, `rm -rf env/` so that `devmain.sh` installs
   dev-dependencies.

[1]: https://www.facebook.com/help/212802592074644?helpref=faq_content
