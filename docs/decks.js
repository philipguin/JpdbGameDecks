
import JPDB from './jpdb.js';

let cachedJpdbApiKey = null;
let expandedRow = null;

document.addEventListener("DOMContentLoaded", function() {
    const coll = document.querySelectorAll(".columns-expl-btn");
    
    coll.forEach(function(button) {
        button.addEventListener("click", function() {
            this.classList.toggle("active");
            const content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    });
});

function showToast(type, message) {
    const toast = document.getElementById("toast");
    toast.className = "toast show_" + type;
    toast.innerHTML = message;
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}

async function getText(url) {
    const response = await fetch(url, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
    return await response.text();
}

async function getJpdbApiKey() {
    let apiKey = cachedJpdbApiKey;
    if (!apiKey) {
        apiKey = prompt("Please enter your jpdb.io API key (found on the settings page).");
        while (apiKey) {
            if (JPDB.checkApiKey(apiKey)) {
                cachedJpdbApiKey = apiKey;
                break;
            }
            apiKey = prompt("API key invalid, please try again.");
        }
    }
    return apiKey;
}
async function loadCsvData(url) {
    const rows = (await getText(url)).trim().split("\n");
    const vocab = [];
    const occurrences = [];

    rows.forEach(row => {
        const [vid, sid, occurrence] = row.split(",");
        vocab.push([parseInt(vid), parseInt(sid)]);
        occurrences.push(parseInt(occurrence));
    });
    return { vocab, occurrences };
}
async function addDeckToJpdb(relPath) {
    try {
        const fullUrl = 'https://raw.githubusercontent.com/philipguin/JpdbGameDecks/main/decks/' + relPath
        const deckName = relPath.substring(relPath.lastIndexOf("/") + 1, relPath.length - 4);

        const apiKey = await getJpdbApiKey();
        if (!apiKey) {
            showToast('error', "Deck not added, missing API key.");
            return;
        }
        const { vocab, occurrences } = await loadCsvData(fullUrl);
        const deckId = await JPDB.createEmptyDeck(apiKey, deckName);
        await JPDB.addToDeck(apiKey, deckId, vocab, occurrences);
        showToast('success', `Deck added to JPDB: <i>${deckName}</i>`);
    } catch (e) {
        console.error("Error:", e);
        showToast('error', `${e.message}`);
    }
}
function onRowChildExpanded(element) {
    element.find(".info-link-btn").on("click", async function() {
        await addDeckToJpdb(this.getAttribute("data-deck-url"));
    });
}


function isProgressComplete(x) { // NOTE: logic duplicated in gen_decks_status.py
    x = x.toLowerCase();
    return x === 'complete' || x === '100' || x === '100%';
}
function formatName(name, progress) {
    if (isProgressComplete(progress)) return name;
    return `${name} (${progress})`
}
function linkType(url) {
    if (url.startsWith('https://store.steampowered.com')) return 'steam';
    else if (url.startsWith('https://www.gog.com')) return 'gog';
    else if (url.startsWith('https://store.epicgames.com')) return 'epic';
    else return 'other';
}
function iconForLinkType(type) {
    if (type == 'steam') return 'icons/steam.svg';
    if (type == 'gog') return 'icons/gog.png';
    if (type == 'epic') return 'icons/epic_games.png';
    return 'icons/external_link.svg';
}
function altForLinkType(type, gameTitle) {
    if (type == 'steam') return 'Steam store page';
    if (type == 'gog') return 'GOG store page';
    if (type == 'epic') return 'Epic Games store page';
    return 'Store page';
}
function formatStoreLinks(links, gameTitle) {
    if (!links) return '';
    let result = `<div class="store-links">`;
    for (const link of links.split('|')) {
        const type = linkType(link);
        const alt = altForLinkType(type) + ' for ' + gameTitle;
        result += `<a href="${link}" target="_blank" rel="noopener noreferrer">`;
        result += `<img src="${iconForLinkType(type)}" alt="${alt}" width="16" height="16">`;
        result += `</a>`;
    }
    result += '</div>';
    return result;
}
function getDifficultyIndex(value) {
    if (value === null || value === undefined || value == '') return 0;

    const matchUnknown = /^[\?\s]+$/.test(value);
    if (matchUnknown) {
        return 0;
    }
    const matchSingle = /^\s*(\d+)(\s*\?)?\s*$/.exec(value); // (e.g., "12" or "12?")
    if (matchSingle) {
        return parseInt(matchSingle[1], 10);
    }
    const matchRange = /^\s*(\d+)\s*\-\s*(\d+)(\s*\?)?\s*$/.exec(value); // (e.g., "12-15" or "12-15?")
    if (matchRange) {
        const num1 = parseInt(matchRange[1], 10);
        const num2 = parseInt(matchRange[2], 10);
        return Math.round((num1 + num2) / 2);
    }
    throw new Error(`Difficulty format not recognized: "${value}"`);
}
function formatDifficulty(difficulty, diffSrc) {

    const difficultyColors = [
        '#FFFFFF', '#00FF00', '#32FF00', '#64FF00', '#96FF00', '#C8FF00',
        '#FFFF00', '#FFC800', '#FF9600', '#FF6400', '#FF3200', '#FF0000',
    ]
    const color = difficultyColors[getDifficultyIndex(difficulty)];
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
function formatUniqueWords(str) {
    return str;
}
// function formatTotalWords(str, uniqueWordsStr) {
//     if (Math.round(str) <= Math.round(uniqueWordsStr)) return ""; // round converts to number first
//     return `<font size="2">${str}</font>`;
// }
function formatMoreInfo(template, childData) {
    let unique_words = childData[7] || 'Unknown';
    let total_words = childData[8] || 'Unknown';
    let deck_author = childData[9] || 'Unknown';

    const info_table = [];

    info_table.push({ title: 'Contributor', value: deck_author });
    info_table.push({ title: 'Unique Words', value: unique_words });

    if (Math.round(total_words) > Math.round(unique_words)) {
        info_table.push({ title: 'Total Words', value: total_words });
    }

    let deck_links = childData[10] || '';
    deck_links = deck_links
        .split('|')
        .map(url => {
            url = url.replaceAll('\\|', '|'); // unescape our split character
            return {
                url: url,
                title: '+ ' + url.substring(url.indexOf("/") + 1, url.length - 4)
            };
        });

    let notes = childData[11] || '';
    notes = notes
        .split(/\\n\s*\\n/)
        .map(x => `<p>${x.replaceAll('\\n', ' ')}</p>`)
        .join('');

    return Mustache.render(template, {
        info_table: info_table,
        deck_links: deck_links,
        notes: notes
    });
}
async function setupDeckTable() {

    const rows = (await getText('decks.tsv'))
        .split('\n')
        .map(x => x.split('\t'));

    const tableRows = rows.map((row, i) => {
        try {
            return [
                '',
                formatName(row[0], row[1]),
                formatStoreLinks(row[2], row[0]),
                formatDifficulty(row[3], row[4]),
                formatSortedness(row[5]),
                formatQuality(row[6]),
                formatUniqueWords(row[7]),
                //formatTotalWords(row[8], row[7]),
            ];
        } catch(e) {
            console.log(`Exception while formatting row ${i}: ${e}`);
        }
    });
    const table = $('#game-table').DataTable({
		responsive: true,
        columns: [
            {
                className: 'dt-control',
                orderable: false,
                searchable: false,
                data: null,
                defaultContent: '',
            }, {
                className: 'aux-control' // this can expand too
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
            }, {
                width: '25px',
                type: 'html-num',
            }
        ],
        data: tableRows,
	});

    const template = await getText('decks-row-expand.html');

    table.on('click', 'td.dt-control, td.aux-control', function(e) {
        let tr = $(e.target).closest('tr');
        let row = table.row(tr);

        if (row.child.isShown()) {
            row.child.hide();
            expandedRow = null;
        } else {
            if (expandedRow) expandedRow.hide();
            expandedRow = row;
            row.child(formatMoreInfo(template, rows[row.index()])).show();
            onRowChildExpanded(row.child());
        }
    });
}

async function setupMetrics() {
    const lines = (await getText('deck-metrics.tsv')).split('\n');
    const ul = document.createElement('ul');
    for (const line of lines) {
        if (!line.trim()) continue;
        let cells = line.split('\t');
        let li = document.createElement('li');
        li.innerHTML = `${cells[0]}: ${cells[1]}`;
        ul.appendChild(li);
    }
    document.getElementById('metrics').appendChild(ul);
}

$(document).ready(async function() {
    await setupDeckTable();
    await setupMetrics();
});