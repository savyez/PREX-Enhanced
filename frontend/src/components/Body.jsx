import '../styles/body.css';
import Button from './Button';

function Body() {
    return (
        <main className="body">
            <h2>Welcome to PREX</h2>
            <p>This is a sample body content for the PREX application. You can replace this with your actual content.</p>
            <div className="button-container">
                <Button name="See Prices" href="/prices" />
            </div>
        </main>
    );
}

export default Body;
