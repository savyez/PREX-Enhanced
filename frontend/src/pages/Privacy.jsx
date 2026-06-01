import '../styles/page_style/privacy.css';

const Privacy = () => {
    return (
        <div className="privacy-page">
            <main className="privacy-main">
                <section className="privacy-hero">
                    <div className="privacy-content">
                        <span className="privacy-eyebrow">Privacy Policy</span>
                        <h1>Your Data Is Treated With Respect</h1>
                        <p>
                            PREX is committed to protecting your personal information while
                            giving you the tools to manage your account, watchlists, and
                            market-data experience. This policy explains what we collect,
                            how we use it, and the choices you have.
                        </p>
                    </div>

                    <aside className="privacy-panel">
                        <h2>At a Glance</h2>
                        <ul>
                            <li>We collect account, usage, and preference data.</li>
                            <li>We use data to deliver services, improve reliability, and support you.</li>
                            <li>We do not sell personal information.</li>
                            <li>You can access, correct, or delete your data.</li>
                        </ul>
                    </aside>
                </section>

                <section className="privacy-details">
                    <article className="privacy-section">
                        <h2>Information We Collect</h2>
                        <p>
                            We collect the information needed to create and manage your PREX account,
                            provide saved watchlists, respond to support requests, and deliver a
                            personalized market-data experience.
                        </p>
                        <ul>
                            <li>Account details such as name, email address, and login credentials.</li>
                            <li>Saved watchlists, preferences, and settings you choose in the app.</li>
                            <li>Usage details including pages visited, search activity, and feature use.</li>
                            <li>Support messages, questions, and any information you share with our team.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>How We Use Your Data</h2>
                        <p>
                            Your information is used to operate PREX, keep your account secure,
                            and make the service easier to use. We also rely on data to improve the
                            product and to respond quickly when you need help.
                        </p>
                        <ul>
                            <li>Provide, maintain, and personalize PREX features.</li>
                            <li>Send important account notices, updates, and support responses.</li>
                            <li>Detect and prevent fraud, abuse, and unauthorized access.</li>
                            <li>Analyze usage patterns to improve performance and reliability.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>Cookies and Tracking</h2>
                        <p>
                            PREX uses cookies, local storage, and similar technologies to keep you signed in,
                            remember your preferences, and improve site performance.
                        </p>
                        <p>
                            These technologies help us present content faster and provide a smoother
                            experience when you return to the site.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Third-Party Services</h2>
                        <p>
                            We may work with trusted service providers to operate PREX and deliver
                            market data. These partners receive only the information necessary to
                            perform their services and must protect it according to our standards.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Your Choices</h2>
                        <p>
                            You have control over your data and how we communicate with you.
                            You can request access, correction, or deletion of your information.
                        </p>
                        <ul>
                            <li>Update your profile and preferences in your PREX account.</li>
                            <li>Delete saved watchlists or remove data you no longer want stored.</li>
                            <li>Opt out of marketing messages when applicable.</li>
                        </ul>
                    </article>

                    <article className="privacy-section">
                        <h2>Security</h2>
                        <p>
                            We maintain physical, technical, and administrative safeguards to
                            protect your personal information. While no system is completely
                            secure, we continually review our practices to keep data safe.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Children's Privacy</h2>
                        <p>
                            PREX is not intended for children under 16. We do not knowingly
                            collect personal information from minors without parental consent.
                        </p>
                    </article>

                    <article className="privacy-section">
                        <h2>Policy Changes</h2>
                        <p>
                            We may update this privacy policy as our service evolves. When we do,
                            we will post the changes on this page and update the effective date.
                        </p>
                    </article>

                    <article className="privacy-section privacy-contact">
                        <h2>Contact Us</h2>
                        <p>
                            If you have questions about this policy or want to exercise your data
                            rights, please contact us at 
                            <a href="mailto:visnuk252@prex.com"> prex.crypto.tracker@gmail.com</a>.
                        </p>
                    </article>
                </section>
            </main>
        </div>
    );
}

export default Privacy;
