import '../styles/component_style/searchbar.css';
import Button from './Button';

function SearchBar({
    id = 'search-input',
    name = 'search',
    placeholder = 'Search...',
    buttonLabel = 'Search',
    value,
    onChange,
    onSubmit,
}) {
    return (
        <form className="search-bar" onSubmit={onSubmit}>
            <input
                id={id}
                name={name}
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={onChange}
            />
            <Button type="submit">{buttonLabel}</Button>
        </form>
    );
}

export default SearchBar;
