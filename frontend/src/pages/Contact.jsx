import '../styles/page_style/contact.css';

const Contact = () => {
    return (
        <div className="contact-page">
            <main className="contact-main">
                <section className="contact-hero">
                    <div className="contact-content">
                        <span className="contact-eyebrow">Contact Us</span>
                        <h1>We Are Here To Help</h1>
                        <p>
                            Have a question, suggestion, or issue with PREX? Reach out and
                            we will help you get the right information as quickly as possible.
                        </p>
                    </div>

                    <aside className="contact-panel">
                        <h2>Get In Touch</h2>
                        <ul>
                            <li>
                                <span>Email</span>
                                <a href="mailto:prex.crypto.tracker@gmail.com">prex.crypto.tracker@gmail.com</a>
                            </li>
                            <li>
                                <span>Phone</span>
                                <a href="tel:+11234567890">+1 (123) 456-7890</a>
                            </li>
                            <li>
                                <span>Support</span>
                                <p>Available for account, watchlist, and market-data questions.</p>
                            </li>
                        </ul>
                    </aside>
                </section>

                <section className="contact-details">
                    <h2>Contact made simple</h2>
                    <p>
                        Whether you need support with your account, watchlist, or market data,
                        our team is ready to respond quickly and clearly.
                    </p>
                    <p>
                        We prioritize helpful answers, transparent updates, and fast assistance so you can stay focused on the markets.
                        You can also reach us anytime at <a href="mailto:prex.crypto.tracker@gmail.com"> prex.crypto.tracker@gmail.com</a>.
                    </p>
                </section>
            </main>
        </div>
    );
}

export default Contact;
