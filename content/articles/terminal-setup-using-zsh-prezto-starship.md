Title: Terminal setup using ZSH, Prezto and Starship on MacOS
Date: 2023-12-23
Modified: 2023-12-23
Category: Programming
Tags: terminal, setup, prezto, starship, zsh
Slug: terminal-setup-using-zsh-prezto-starship.md
Authors: Ashwini Chaudhary
Summary: Terminal setup using ZSH, Prezto and Starship on MacOS


ZSH installation
===

Starting with Catalina the default shell was changed to zsh. You can verify your current shell using:

```bash
➜ echo $SHELL
/bin/zsh
```

If it's not `zsh` for you, you can install it using [Homebrew](https://brew.sh/)

```bash
brew install zsh
```

Once installed we need to make `zsh` the default shell using:

```bash
chsh -s /bin/zsh
```


Prezto installation
===


[Prezto](https://github.com/sorin-ionescu/prezto) is a configuration framework for `zsh`. Another well known alternative is [Oh My Zsh](https://ohmyz.sh/).

I was using Oh My Zsh previously but it had performance issues and switching to Prezto has helped with the performance issues. Oh My Zsh has a much bigger community and receives regular updates and is bit more beginner friendly.


Before installing make sure to make a back of your `.zshrc` file if you had one already as Prezto can ve problematic with existing `.zshrc` files.

## Clone the Prezto repo

```bash
git clone --recursive https://github.com/sorin-ionescu/prezto.git "${ZDOTDIR:-$HOME}/.zprezto"
```


## Link the new zsh config files provided by Prezto to your home directory

```bash
setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done
```

Once installed you'll find the Prezto configuration in `.zpreztorc` file in your home directory. The default file looks like this: [https://github.com/sorin-ionescu/prezto/blob/master/runcoms/zpreztorc](https://github.com/sorin-ionescu/prezto/blob/master/runcoms/zpreztorc)


The list of modules are available here: [https://github.com/sorin-ionescu/prezto/blob/master/runcoms/zpreztorc](https://github.com/sorin-ionescu/prezto/blob/master/runcoms/zpreztorc)

```markdown
zstyle ':prezto:load' pmodule \
 'lazy-load' \
 'environment' \
 'terminal' \
 'editor' \
 'history' \
 'directory' \
 'spectrum' \
 'utility' \
 'completion' \
 'osx' \
 'ssh' \
 'git' \
 'python' \
 'node' \
 'syntax-highlighting' \
 'history-substring-search' \
 'prompt' \
 'autosuggestions'
```

Here `lazy-load` is a 3rd party module to lazily load functions that are time consuming: https://github.com/xcv58/zsh-lazy-load

To install this module if you want, do the following:

```bash
cd $HOME/.zprezto
git submodule add https://github.com/xcv58/zsh-lazy-load.git modules/lazy-load
```

Once that is done `'lazy-load'` should be the first item in your modules list as shown above.

In my current `.zshrc` file I'm using it to lazily load `nvm` and `virtualenvwrapper`:

```bash
# .zshrc

func load_virtualenv() {
  source path_to_virtualenvwrapper.sh
}

func load_nvm () {
    source path_to_nvm.sh
}


# At the end of .zshrc
lazy_load load_virtualenv load_nvm
```

## Selecting theme

Prezto comes with a bunch of themes. To list the themes use `prompt -l` and to preview one use `prompt -p name`. Once you've picked a theme open your `.zpreztorc` file and add it  `zstyle ':prezto:module:prompt' theme 'pure'` (here `'pure'` is the prompt theme's name).


## Fonts

Currently, I'm using GitHub's [Monaspace font](https://github.com/githubnext/monaspace#monaspace), its Krypton variation. This font supports ligatures.

Other fonts I highly recommend:

- [Nerd font](https://www.nerdfonts.com/font-downloads) -- great for terminal prompt
- [Fira Code](https://github.com/tonsky/FiraCode) (supports ligatures)
- Monaco (ships with MacOS and great for code but lacks ligatures). [A ligature version](https://github.com/GianCastle/FiraMonaco) is also available but I've not tried it personally. The Powerline mentioned here is a [prompt theme](https://github.com/davidjrice/prezto_powerline).


**Font setup in iTerm 2:**

![Font setup in iTerm 2](https://i.imgur.com/E5t5mPe.png)

**Font setup in VS Code:**

![Font setup in VS Code](https://i.imgur.com/bvNgNz0.png)

![Ligatures setup in VS Code](https://i.imgur.com/ausDfmG.png)



Prompt Customization
===

I'm using [Starship](https://starship.rs/) for customizing the prompt. Note that by default it requires [Nerd Font](https://www.nerdfonts.com/font-downloads).

To install it Homebrew can be used:

```bash
brew install starship
```

Then open your `.zshrc` file and add the following at the end:

```bash
eval "$(starship init zsh)"
```

To configure Starship you need to create a config file first:

```bash
mkdir -p ~/.config && touch ~/.config/starship.toml
```

Then define the items you'd want:

```toml
format = """
$custom\
$username\
$hostname\
$shlvl\
$directory\
$git_branch\
$git_commit\
$git_state\
$git_status\
$package\
$elixir\
$golang\
$nodejs\
$python\
$ruby\
$rust\
$terraform\
$nix_shell\
$aws\
$env_var\
$line_break\
$status\n\
$cmd_duration\
$character"""
add_newline = true
```

Then for each item you can further make your own modification, for example here's how username, directory and git status looks like for me:

```toml
[username]
disabled = false
show_always = true
style_user = "white bold"
style_root = "white bold"
format = "[xonix_$user]($style) "

[directory]
truncation_length = 100  # no truncation
truncate_to_repo = true
format = "[$path]($style) "

## Git settings
[git_branch]
style = "bold purple"
truncation_length = 100  # no truncation
truncation_symbol = "..."

[custom.xonix]
command = "echo -n '🍺 '"
when = "true"
```

The resulting prompt looks like:

![Starship configured prompt](https://i.imgur.com/Y9VQ4SW.png)

The setting available under any such action is in the docs: [username](https://starship.rs/config/#username), [directory](https://starship.rs/config/#directory), [git_branch](https://starship.rs/config/#git_branch) and [custom](https://starship.rs/config/#custom-commands)


Find detailed documentation here: [https://starship.rs/config/#prompt](https://starship.rs/config/#prompt)


Checking performance
===

If your shell is taking a while to load then it can be profiled by adding `zmodload zsh/zprof` at the start of `.zshrc` file and `zprof` at the end of the file. In addition individual modules can be timed using `time (pmodload '<module_name>')`.
