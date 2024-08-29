
const JPDB = {

    async checkApiKey(apiKey) {
        const response = await fetch("https://jpdb.io/api/v1/ping", {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
        return response.ok;
    },

    async createEmptyDeck(apiKey, name) {
        const response = await fetch("https://jpdb.io/api/v1/deck/create-empty", {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'name': name,
                'position': 0
            })
        });
        if (!response.ok) throw new Error(`Failed to create deck: ${response.statusText}`);
        return (await response.json()).id;
    },

    async addToDeck(apiKey, deckId, vocab, occurrences) {
        const response = await fetch("https://jpdb.io/api/v1/deck/add-vocabulary", {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'id': deckId,
                'vocabulary': vocab,
                'occurences': occurrences, // API has typo, which we replicate here
                'replace_existing_occurences': false, // ^^^
                'ignore_unknown': true
            })
        });
        if (!response.ok) throw new Error(`Failed to add vocabulary to deck: ${response.statusText}`);
    }

}

export default JPDB;