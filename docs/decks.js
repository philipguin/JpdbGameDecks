
import JPDB from './jpdb.js';


let cachedRows = null;
let cachedRowExpandTemplate = null;
let cachedJpdbApiKey = null;

let expandedRow = null;


document.addEventListener("DOMContentLoaded", function() {
    const coll = document.querySelectorAll(".columns-expl-btn");
    
    // Setup collapser buttons and content
    coll.forEach(function(button) {
        button.addEventListener("click", function() {
            this.classList.toggle("active");
            const content = this.nextElementSibling;
            if (content.style.display === '' || content.style.display === "none") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        });
    });

    function scrollTo(id) {
        const target = document.getElementById(id);
        if (target) {
            if (target.tagName === 'BUTTON') {
                const content = target.nextElementSibling;
                if (content && (content.style.display === '' || content.style.display === 'none')) {
                    target.classList.toggle("active");
                    content.style.display = "block";
                }
            }
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
    // Check if there's a hash in the URL
    const hash = window.location.hash.substring(1);
    if (hash) scrollTo(hash); //TODO: this needs to wait until layout shifts are done, somehow

    // Handle clicks on links that contain hashes
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            scrollTo(targetId);
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
$(document).ready(async function() {

    const table = $('#game-table').DataTable({
		responsive: true,
        paging: false, // This would kill SEO without massive workarounds, unfortunately
        columns: [
            {   // widget
                className: 'dt-control',
                orderable: false,
                searchable: false,
                defaultContent: '',
            }, {
                // name sort index
                visible: false,
            }, {
                // name
                className: 'dt-nowrap aux-control', // this can expand too
                orderData: [1],
                //TODO: sort names by "orthogonal data", see DataTables docs.
                //  Just spit out integer index of name somehow, since it's already sorted like we want.
            }, {
                // store links
                className: 'dt-nowrap',
                width: '80px',
                orderable: false,
                searchable: false,
            }, {
                // difficulty
                className: 'dt-nowrap dt-body-left',
                width: '50px',
            }, {
                // sortedness
                width: '25px',
                type: 'html-num',
            }, {
                // quality
                width: '25px',
                type: 'html-num',
            }, {
                // unique words
                width: '25px',
                type: 'html-num',
            },
        ],
        drawCallback: function() {
            const api = this.api();
            
            // Hack to allow Google/spiders to crawl through all pages, instead of only the first
            //    https://datatables.net/forums/discussion/34445/google-indexing-of-table-pages
            $( 'a.paginate_button', this.api().table().container() ).attr('href', '#!');

             // Hack to copy active-sort-arrow over, not working when we use orderData
            let sortStr = '';
            for (const orderEl of api.order()) {
                if (orderEl[0] != 2) continue;
                sortStr = 'dt-ordering-' + orderEl[1]
                break;
            }
            const headerNames = api.column(2).header();
            headerNames.className = headerNames.className.replace(/\s*dt-ordering-(_asc|_desc)/, '') + ' ' + sortStr;
        },
	});

    table.on('click', 'td.dt-control, td.aux-control', async function(e) {
        let tr = $(e.target).closest('tr');
        let row = table.row(tr);

        if (row.child.isShown()) {
            row.child.hide();
            expandedRow = null;
        } else {
            if (expandedRow) expandedRow.hide();
            expandedRow = null;

            if (cachedRows == null) {
                cachedRows = (await getText('decks.tsv')).split('\n').map(x => x.split('\t'));
            }
            if (cachedRowExpandTemplate == null) {
                cachedRowExpandTemplate = await getText('decks-row-expand.html');
            }
            expandedRow = row;
            row.child(formatMoreInfo(cachedRowExpandTemplate, cachedRows[row.index()])).show();
            onRowChildExpanded(row.child());
        }
    });
});
