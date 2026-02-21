Manage the context window.

This project will out live your current context window, how will future Claudes know what the heck is going on?

- CLAUDE.md - keep this file up to date
- MEMORY.md - in the ~/ user .claude directory or something
- auto compaction summaries

also CLAUDE.md can point to other md doc files.

and claudes do tend to find well named doc files.

and scripts! That is a more concrete way to encode workflows and procedures, a script with --help.

prefer scripts where the script takes an argument that is a command - that way there isn't a huge proliferation of scripts. It doesn't have to be just one script. But put related functionality in one script.

oh and background workers. you avoid doing work. That takes up context. instead create background worker claude code instances with there own short-lived context. They are focused and given only the context they need to work on one task. You have a broad strategic mindset but avoid using up your context window by having the workers do the detailed work and you manage and orchestrate at a higher level. (one problem is background workers read this file so structure it so they don't get confused about who they are and future of you know that you are the manager.)

git worktrees!!! git feature branches!!! github issues!!! github pull requests!!! gh cli. These are all greate ways to track work and leave a history around, but also develop a system so you can track local workers progress with local structured files. But use github issues for all tasks!

Basically everything I type to you. Give it to a worker!
