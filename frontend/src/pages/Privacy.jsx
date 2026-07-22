import '../styles/page_style/privacy.css';

const Privacy = () => {
    return (
        <div className="privacy-page">
            <main className="privacy-main">
                <section className="privacy-hero">
                    <div className="privacy-content">
                        <span className="privacy-eyebrow">Privacy Policy</span>
                        <h1>Clear information about how PREX handles your data</h1>
                        <p>
                            This page explains the data PREX needs to provide accounts,
                            watchlists, authentication, and cryptocurrency market features.
                            It is product documentation and should be reviewed with your
                            organization&apos;s legal requirements before production use.
                        </p>
                    </div>

                    <aside className="privacy-panel">
                        <h2>At a Glance</h2>
                        <ul>
                            <li>Your account includes the details you provide during registration.</li>
                            <li>Your watchlists and profile updates are stored to provide the app.</li>
                            <li>Access and refresh tokens are stored in browser local storage.</li>
                            <li>CoinGecko supplies the market data shown in PREX.</li>
                        </ul>
                    </aside>
                </section>

                <section className="privacy-details">
                    <article className="privacy-section">
                        <h2>Information We Collect</h2>
                        <p>
                            PREX stores only the information needed by the current application
                            flows. The backend stores account records, watchlists, watchlist
                            items, and authentication-related token records.
                        </p>
                        <ul>
                            <li>First name, last name, username, date of birth, and email address.</li>
                            <li>A securely hashed password and email-verification status.</li>
                            <li>Watchlist names, coin memberships, and profile changes.</li>
                            <li>Tokens kept by the browser to maintain the signed-in session.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>How We Use Your Data</h2>
                        <p>
                            PREX uses this information to operate the features you request and
                            protect access to your account.
                        </p>
                        <ul>
                            <li>Create and authenticate your account.</li>
                            <li>Send email-verification and password-reset messages.</li>
                            <li>Save and retrieve your watchlists and profile details.</li>
                            <li>Refresh expired sessions and revoke refresh tokens during logout.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>Cookies and Tracking</h2>
                        <p>
                            The current frontend uses browser local storage for the access token,
                            refresh token, and a cached copy of basic user data. The app does not
                            currently implement an analytics-cookie system.
                        </p>
                        <p>
                            Removing this local storage will sign you out on that browser. A future
                            version should consider an HttpOnly cookie session design for improved
                            token protection.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Third-Party Services</h2>
                        <p>
                            PREX requests cryptocurrency market and chart data from CoinGecko.
                            Email delivery uses the SMTP provider configured by the deployment.
                            These services may process requests according to their own privacy
                            policies and terms.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Your Choices</h2>
                        <p>
                            You can update the supported profile fields and delete watchlists
                            from the app. For account export or full account deletion, contact
                            the project team so the request can be handled safely.
                        </p>
                        <ul>
                            <li>Update your first name, last name, or username in Profile.</li>
                            <li>Remove coins or delete watchlists from the Watchlist page.</li>
                            <li>Sign out to clear the browser&apos;s stored session data.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>Security</h2>
                        <p>
                            PREX uses Django password hashing, signed time-limited email links,
                            JWT authentication, token refresh handling, and production HTTPS
                            settings. No online service is completely secure, so keep credentials
                            private and use a strong password.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Children's Privacy</h2>
                        <p>
                            PREX is a cryptocurrency information tool and is not intended for
                            children. Do not use the service if you are not legally permitted to
                            use it in your location.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Policy Changes</h2>
                        <p>
                            This page should be updated whenever the data flows or third-party
                            services change. Review the latest version before relying on it for
                            a production deployment.
                        </p>
                    </article>

                    <article className="privacy-section privacy-contact">
                        <h2>Contact Us</h2>
                        <p>
                            If you have questions about this policy or want to request an account
                            data change, contact us at
                            <a href="mailto:prex.crypto.tracker@gmail.com"> prex.crypto.tracker@gmail.com</a>.
                        </p>
                    </article>
                </section>
            </main>
        </div>
    );
}

export default Privacy;
