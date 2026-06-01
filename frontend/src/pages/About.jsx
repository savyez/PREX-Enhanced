import Navbar from "../components/Navbar";
import '../styles/page_style/about.css';

const About = () => {
    return (
        <div className="about-page">
            <main className="about-main">
                <section className="about-hero">
                    <div className="about-content">
                        <span className="about-eyebrow">About Us</span>
                        <h1>Creating Better Experiences For Every Visitor</h1>
                        <p>
                            Welcome to our website. We are dedicated to delivering helpful,
                            high-quality content and services with a smooth experience from
                            the first click to the final detail.
                        </p>
                    </div>

                    <aside className="about-panel">
                        <h2>What Drives Us</h2>
                        <ul>
                            <li>Useful content that is easy to understand</li>
                            <li>Reliable service shaped around real user needs</li>
                            <li>A friendly experience that keeps improving</li>
                        </ul>
                    </aside>
                </section>
            </main>
        </div>
    );
}

export default About;
