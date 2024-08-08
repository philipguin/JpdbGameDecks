
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

    const NUM_DISPLAY_COLUMNS = 5;

    $.ajax({
        url: 'decks.tsv',
        dataType: 'text',
        success: function(data) {

            function iconForLinkUrl(url) {
                if (url.startsWith('https://store.steampowered.com')) return 'icons/steam.svg';
                else if (url.startsWith('https://www.gog.com')) return 'icons/gog.png';
                else if (url.startsWith('https://store.epicgames.com')) return 'icons/epic_games.png';
                else return 'icons/external_link.svg';
            }
            function formatLinks(links) {
                if (!links) return '';
                let result = '<div class="store-links">';
                for (link of links.split(';')) {
                    result += '<a href="' + link + '" target="_blank" rel="noopener noreferrer">';
                    result += '<img src="' + iconForLinkUrl(link) + '" width="16" height="16">';
                    result += '</a>';
                }
                result += '</div>';
                return result;
            }

            let lines = data.split('\n').map(line => line.split('\t'));
            let tableRows = lines.map(line => {
                return ['', line[0], formatLinks(line[1])].concat(line.slice(2, NUM_DISPLAY_COLUMNS));
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

            function format(template, childData) {
                return template.replace('\{\{notes\}\}', childData[0] || '')
                               .replace('\{\{deck_author\}\}', childData[1] || 'Unknown');
            }
            $.get('decks-row-expand.html', function(template) {

                table.on('click', 'td.dt-control', function(e) {
                    let tr = $(e.target).closest('tr');
                    let row = table.row(tr);

                    if (row.child.isShown()) {
                        row.child.hide();
                    } else {
                        row.child(format(template, tableRowChildren[tr.index()])).show();
                    }
                });
            });

        }
    });
});