# Contributions

Firstly, thanks for helping out!
Japanese scripts are surprisingly hard to find, and quality decks can be difficult to build. Many will appreciate the convenience of having a pre-made deck for their favorite game, so thank you!

To create and upload your deck, please do the following:

1. Check [here](decks_status.md) to ensure it doesn't already exist and isn't already being created by someone.

2. [Open an issue](https://github.com/philipguin/JpdbGameDecks/issues) with title "Contribution: \<Game Names\>"

    * Provide a very rough timeline. _Please do some research before making a commitment!_ Resources for a game often aren't available, and obtaining your own can be prohibitively time-consuming.

    * If there are no issues, then your post will be given the label "approved" and you can safely begin working on your deck. (It's very unlikely it won't be approved, assuming you did everything correctly.)

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

5. Submit your changes.

    * Be sure not to include any game text or assets in your submitted files, and otherwise respect game creators' copyrights.
    
    * __For simple changes__:

        If you're only adding a handful of files, then simply update the initial issue you submitted, attaching all the files and typing out the _complete information_ to be added to <decks_status.md>. (Please see there for details).

    * __For complex changes__:

        If you're adding a number of decks, including a lot of scripts, or changing a number of disparate files, then please do the pull request manually.

        1. Fork the project:

            Click the "Fork" button at the top-right of the [main page](https://github.com/philipguin/JpdbGameDecks).

        2. Clone your fork:

            ```bash
            git clone https://github.com/yourusername/repository-name.git
            cd repository-name
            ```

        3. Create a new branch:

            ```bash
            git checkout -b name-of-your-branch
            ```

        4. Make your changes:

            * You *must* update <decks_status.md> with new rows for added games! (See there for more details.)
            * You *must not* include any direct or translated game text!
            * Place your CSVs in the appropriate game folder, making a new one if necessary.
            * If there are multiple CSVs, consider adding a `README.md` to help the user choose.
            * You can add any useful python scripts or instructions for deck generation to an adjacent `src` folder in the game directory.

        5. Commit your changes:

            ```bash
            git add --all
            git commit -m "Description of the changes"
            ```
            Try to use multiple commits for unrelated changes, e.g. one commit per game added.

        6. Push to your fork:

            ```bash
            git push origin name-of-your-branch
            ```

        7. [Open a pull request](https://github.com/philipguin/JpdbGameDecks/pulls) and link to it from the issue you posted earlier.



That's it! Thank you for your hard work!