import '../styles/page_style/contact.css';

const Contact = () => {
    return (
        <div className="contact-page">
            <main className="contact-main">
                <section className="contact-hero">
                    <div className="contact-content">
                        <span className="contact-eyebrow">Contact Us</span>
                        <h1>Questions about your market workspace?</h1>
                        <p>
                            Contact the PREX team about account access, email verification,
                            watchlists, chart data, or a problem you found in the app.
                        </p>
                    </div>

                    <aside className="contact-panel">
                        <h2>Support topics</h2>
                        <ul>
                            <li>
                                <span>Email</span>
                                <a href="mailto:prex.crypto.tracker@gmail.com">prex.crypto.tracker@gmail.com</a>
                            </li>
                            <li>
                                <span>Support</span>
                                <p>Account access, watchlists, search, seven-day charts, and market-data questions.</p>
                            </li>
                        </ul>
                    </aside>
                </section>

                <section className="contact-details">
                        <h2>Before you contact us</h2>
                        <p>
                        Include the page you were using, the approximate time of the issue,
                        and a short description of what happened. Never include your password,
                        access token, refresh token, or other private credentials.
                        </p>
                        <p>
                        For account or privacy questions, email
                        <a href="mailto:prex.crypto.tracker@gmail.com"> prex.crypto.tracker@gmail.com</a>.
                        </p>
                </section>
            </main>
        </div>
    );
}

export default Contact;
