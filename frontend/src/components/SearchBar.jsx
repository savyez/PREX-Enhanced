import '../styles/component_style/searchbar.css';

function SearchBar({ placeholder = 'Search...', buttonLabel = 'Search', value, onChange, onSubmit }) {
    return (
        <form className="search-bar" onSubmit={onSubmit}>
            <input type="text" placeholder={placeholder} value={value} onChange={onChange} />
            <button type="submit">{buttonLabel}</button>
        </form>
    );
}

export default SearchBar;
