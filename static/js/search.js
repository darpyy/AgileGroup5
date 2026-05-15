const searchbar = document.getElementById('search-input');
const someElement = document.getElementById('search-dropdown');

const getUsers = async () => {
    const response = await fetch('/usernames');
    const users = await response.json();
    // store the data somewhere?
    window.users = users;
};
getUsers();

if (searchbar && someElement) {
    searchbar.addEventListener('input', e => {
        // clear previous results so they don't pile up
        someElement.innerHTML = '';

        // get value of text field
        const searchTerm = searchbar.value.trim();

        // hide dropdown if the box is empty
        if (!searchTerm) {
            someElement.hidden = true;
            return;
        }

        // assuming JSON objects have a username property
        const matches = (window.users || []).filter(u =>
            u.username.includes(searchTerm)
        );

        // iterate over the matches and put them in the html
        matches.map(match => {
            someElement.innerHTML += `<li><a href="/user/${match.username}">${match.username}</a></li>`;
        });

        someElement.hidden = false;
    });

    // close on click outside
    document.addEventListener('click', e => {
        if (!someElement.contains(e.target) && e.target !== searchbar) {
            someElement.hidden = true;
        }
    });

    // close on Escape
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') someElement.hidden = true;
    });
}
