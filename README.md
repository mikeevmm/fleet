# fleet

Microblog (or just blog) to your [Flounder] page from your terminal.

## What?

If you're the type of person who thinks writing your [Flounder] posts from vim¹ sounds cool then you're the target audience. Bonuses of this are formatting is consistent, posts are dated automatically, and long entries are prompted to be promoted to gemlog entries.

¹Or emacs, *I guess.*

## How?

```bash
git clone git@github.com:mikeevmm/fleet.git
cd fleet
bash install.sh     # Follow instructions
```

then,

```bash
fleet
```

## Yes, but *how*?

Python and sshfs. And a little parsing combinating, which could have been regex, frankly.

## What else?

fleet uses your `$VISUAL` editor to prompt you for your posts. If this variable is unset, it defaults to `/usr/bin/vim`.

You can submit your post by saving and quitting from the editor; if you leave with an empty message, or unchanged, the post is aborted.

Small posts will be posted to `<your username>.flounder.online/journal.gmi`; posts are grouped under a level 1 header indicating the date of posting.

[You can see my journal as an example.](https://miguelmurca.flounder.online/journal.gmi)

If a post is longer than a tweet (280 characters), fleet will ask you whether you want to write a gemlog instead. In this case, you'll be prompted for a title, and a file will be created in the `gemlog` folder, with title `<year>-<month>-<day><title>.gmi`.

Just in case anything goes wrong, a backup of the existing `journal.gmi` file is saved before changes. You can find this backup in this folder, under the name `.journal.bak`.

Submitting the post can take some time (~10 seconds). This is normal and is due to sshfs.

## License

`fleet` is licensed under a GNU General Public License v2. This [informally means that][tldr]:

    You may copy, distribute and modify the software as long as you track
    changes/dates in source files. Any modifications to or software including
    (via compiler) GPL-licensed code must also be made available under the GPL
    along with build & install instructions.

See LICENSE for the full text.

## Support

Getting donations, no matter how small, lets me know that people use and 
appreciate the software I've put out. (Enough so to pay for it.)

If you like `fleet`, please consider [buying me a coffee][coffee].

[Flounder]: https://flounder.online
[tldr]: https://tldrlegal.com/license/gnu-general-public-license-v2#summary
[coffee]: https://www.paypal.me/miguelmurca/2.50
