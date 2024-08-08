
document.addEventListener("DOMContentLoaded", function() {
    var coll = document.querySelectorAll(".columns-expl-btn");
    
    coll.forEach(function(button) {
        button.addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    });
});

$(document).ready(function() {

    const NUM_DISPLAY_COLUMNS = 7;

    function isProgressComplete(x) { // NOTE: logic duplicated in gen_decks_status.py
        x = x.toLowerCase();
        return x === 'complete' || x === '100' || x === '100%';
    }
    function formatName(name, progress) {
        if (isProgressComplete(progress)) return name;
        return `${name} (${progress})`
    }

    function iconForLinkUrl(url) {
        if (url.startsWith('https://store.steampowered.com')) return 'icons/steam.svg';
        else if (url.startsWith('https://www.gog.com')) return 'icons/gog.png';
        else if (url.startsWith('https://store.epicgames.com')) return 'icons/epic_games.png';
        else return 'icons/external_link.svg';
    }
    function formatLinks(links) {
        if (!links) return '';
        let result = `<div class="store-links">`;
        for (link of links.split('|')) {
            result += `<a href="${link}" target="_blank" rel="noopener noreferrer">`;
            result += `<img src="${iconForLinkUrl(link)}" width="16" height="16">`;
            result += `</a>`;
        }
        result += '</div>';
        return result;
    }

    function getDifficultyIndex(value) {
        if (value === null || value === undefined || value == '') return 0;

        let matchUnknown = /^[\?\s]+$/.test(value);
        if (matchUnknown) {
            return 0;
        }
        let matchSingle = /^\s*(\d+)(\s*\?)?\s*$/.exec(value); // (e.g., "12" or "12?")
        if (matchSingle) {
            return parseInt(matchSingle[1], 10);
        }
        let matchRange = /^\s*(\d+)\s*\-\s*(\d+)(\s*\?)?\s*$/.exec(value); // (e.g., "12-15" or "12-15?")
        if (matchRange) {
            let num1 = parseInt(matchRange[1], 10);
            let num2 = parseInt(matchRange[2], 10);
            return Math.round((num1 + num2) / 2);
        }
        throw new Error(`Difficulty format not recognized: "${value}"`);
    }
    function formatDifficulty(difficulty, diffSrc) {

        const difficultyColors = [
            '#FFFFFF', '#00FF00', '#32FF00', '#64FF00', '#96FF00', '#C8FF00',
            '#FFFF00', '#FFC800', '#FF9600', '#FF6400', '#FF3200', '#FF0000',
        ]
        let color = difficultyColors[getDifficultyIndex(difficulty)];
        if (typeof difficulty === 'string') difficulty = difficulty.replaceAll("-", "&#8209;"); // non-breaking hyphen

        difficulty = `<font color="${color}">${difficulty}</font>`;
        if (diffSrc) {
            difficulty = `${difficulty}&nbsp;<sub>${diffSrc}</sub>`;
        }
        return difficulty;
    }

    function formatSortedness(str) {
        if (str.endsWith('?')) str = `<font color="#f8f">${str.substring(0, str.length - 1)}</font>`;
        return str;
    }

    function formatQuality(str) {
        if (str.endsWith('?')) str = `<font color="#f8f">${str.substring(0, str.length - 1)}</font>`;
        return str;
    }

    function formatMoreInfo(template, childData) {
        let deck_author = childData[0] || 'Unknown'

        let notes = childData[1] || ''
        notes = notes.split(/\\n\s*\\n/).map(x => `<p>${x.replaceAll('\\n', ' ')}</p>`).join('');

        return template
            .replaceAll('\{\{deck_author\}\}', deck_author)
            .replaceAll('\{\{notes\}\}', notes)
        ;
    }

    $.ajax({
        url: 'decks.tsv',
        dataType: 'text',
        success: function(data) {
            let lines = data.split('\n').map(line => line.split('\t'));
            let tableRows = lines.map((line, i) => {
                try {
                    return [
                        '',
                        formatName(line[0], line[1]),
                        formatLinks(line[2]),
                        formatDifficulty(line[3], line[4]),
                        formatSortedness(line[5]),
                        formatQuality(line[6]),
                    ];
                } catch(e) {
                    console.log(`Exception while formatting row ${i}: $e`);
                }
            });
            let tableRowChildren = lines.map(line => {
                return line.slice(NUM_DISPLAY_COLUMNS);
            });
            let table = $('#game-table').DataTable({
    			responsive: true,
                columns: [
                    {
                        className: 'dt-control',
                        orderable: false,
                        searchable: false,
                        data: null,
                        defaultContent: '',
                    }, {

                    }, {
                        width: '80px',
                        orderable: false,
                        searchable: false,
                    }, {
                        width: '50px',
                    }, {
                        width: '25px',
                        type: 'html-num',
                    }, {
                        width: '25px',
                        type: 'html-num',
                    }
                ],
                data: tableRows,
    		});

            $.get('decks-row-expand.html', function(template) {

                table.on('click', 'td.dt-control', function(e) {
                    let tr = $(e.target).closest('tr');
                    let row = table.row(tr);

                    if (row.child.isShown()) {
                        row.child.hide();
                    } else {
                        row.child(formatMoreInfo(template, tableRowChildren[row.index()])).show();
                    }
                });
            });
        }
    });
});