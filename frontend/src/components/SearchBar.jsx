import '../styles/searchbar.css';

function SearchBar() {
    return (
        <div className="search-bar">
            <input type="text" placeholder="Search coins..." />
            <button>Search</button>
        </div>
    );
}

export default SearchBar;
