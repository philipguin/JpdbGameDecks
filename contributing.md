# Contributions

Firstly, thanks for volunteering!

To create and upload your deck, please do the following:

1. Check [here](https://philipguin.github.io/JpdbGameDecks) to ensure it doesn't already exist and isn't already being created by someone.

2. [Open an issue](https://github.com/philipguin/JpdbGameDecks/issues) with title "Contribution: \<Game Names\>"

    * Provide a very rough timeline. _Please do some research before making a commitment!_ Resources for a game often aren't available, and obtaining your own can be prohibitively time-consuming.

    * If there are no issues, then your post will be given the label "greenlit" and you can safely begin working on your deck. (It's very unlikely it won't be greenlit, assuming you did everything correctly.)

3. Create the deck using [jpdb](https://jpdb.io).

    * [Deck-from-text](https://jpdb.io/new_deck_from_text) is the preferred method, since this includes frequency information and the total word count.
     (We potentially lose sorting information this way, but it's well worth the time saved over manual entry.)
     However, it is _strongly recommended_ you sanitize the input text before using it.
     This means applying regex filters to remove English annotations, substitute scripting variables with plausible Japanese text (i.e. to preserve the grammatical structure for analysis), visually looking it over, etc.
     [Sublime Text](https://www.sublimetext.com/) is a great tool for this, but `grep`-ing from the command line is also valid.

    * Use multiple decks for multiple chapters or categories (e.g. story, item descriptions), depending on what'd be most useful and the level of effort involved.

    * You don't have to put in a crazy amount of effort -- just get the low-hanging fruit and be honest about the quality when it's time to upload.

    * Feel free to ask questions!

4. Export the deck from jpdb as a CSV using the tool on <https://jpdb.asayake.xyz> under _Export Decks_.

5. Create an `info.yaml` for your deck:

    Please read the column descriptions in [here](https://philipguin.github.io/JpdbGameDecks), making your best guess for any values you can.
    The goal is to briefly inform users of anything they may want to know before using the deck.
    Keep notes concise and make sure to credit anyone who gathered the input text for your deck.

    Only `name` and `progress` are absolutely mandatory.
    `difficulty-source` and `notes-and-sources` may be left blank if appropriate. 
    Everything else _can_ be blank, but you better have a good reason why!

    Example file:

```yaml
name: Persona Before Time XXVII # Game title, omitting articles at the beginning (like "The").
store-links:               # Prefer Steam, then GOG, then whatever legal source.
  - "https://store.steampowered.com/app/77777/PersonaBeforeTimeXXVII/"
deck-author: Your Name     # Must be identical to other decks you've submitted.
difficulty: 5              # Use jpdb.io difficulty as reference, e.g. in Chat-GPT prompt.
difficulty-source: gpt4o   # LLM used (e.g. Chat-GPT). Leave blank if difficulty gauged without.
progress: complete         # "complete"/"100"/"100%" are special values, anything else is displayed with title in parenthesis.
sortedness: 8              # Leave blank if you just can't tell.
quality: 9                 # Make your best guess. E.g. start at 10 and deduct a point for every significant problem.
notes-and-sources: >-      # You must credit and link sources, if any. '>-' marks a multi-line string that removes newlines.
  Story deck is sorted and solid, but tutorials and other text are in a
  separate deck sorted first by category, then by rough time encountered.
  Based on this <a href="https://homestarrunner.com">transcript</a> by CoolGuy27.

```

6. Submit your changes.

    * Be sure not to include any game text or assets in your submitted files, and to otherwise respect game creators' copyrights.
    
    * __For simple changes__:

        If you're only adding a handful of files, then simply update the initial issue you submitted with said files attached.

    * __For complex changes__:

        If you're adding a number of decks, including a lot of scripts, or changing a number of disparate files, then please do the pull request manually.

        1. Fork the project:

            Click the "Fork" button at the top-right of the [main page](https://github.com/philipguin/JpdbGameDecks).

        2. Clone your fork:

            ```bash
            git clone https://github.com/yourusername/repository-name.git
            cd repository-name
            ```

        3. Ensure you have Python 3.10 installed, then run:

            ```bash
            pip install -r requirements.txt
            ```

        3. Create a new branch:

            ```bash
            git checkout -b name-of-your-branch
            ```

        4. Make your changes:

            * You *must* add or update an `info.yaml` as described above!
            * You *must not* include any direct or translated game text!
            * Place your CSVs in the appropriate game folder, making a new one if necessary.
            * If there are multiple CSVs, consider adding a `README.md` to help the user choose.
            * You can add any useful python scripts or resources for deck generation to an adjacent `src` folder in the game directory.
                There are general purpose scripts under `scripts/` as well.

        5. Commit your changes:

            ```bash
            git add --all
            git commit -m "Description of the changes"
            ```

            If your `info.yaml` is invalid, the commit will fail with helpful error messages (hopefully).
            To see what the resulting table entry's [HTML](docs/_includes/deck-table.html) looks like without committing,
            run `pre-commit run gen-decks-status` in the root directory.

            Try to use multiple commits for unrelated changes, e.g. one commit per game added.

        6. Push to your fork:

            ```bash
            git push origin name-of-your-branch
            ```

        7. [Open a pull request](https://github.com/philipguin/JpdbGameDecks/pulls) and link to it from the issue you posted earlier.



That's it! Thanks for your hard work!