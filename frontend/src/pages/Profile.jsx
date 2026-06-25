import { Link } from 'react-router-dom';
import { getUser } from '../utils/auth.js';
import { useEffect, useState } from 'react';
import Button from '../components/Button.jsx';
import { updateUserProfile } from '../utils/api.js';
import '../styles/page_style/profile.css';

function Profile() {
    const [updateInfo, setUpdateInfo] = useState(false);
    const [user, setUser] = useState(() => getUser());
    const [formData, setFormData] = useState(() => getUser() || {});

    useEffect(() => {
        const currentUser = getUser();
        setUser(currentUser);
        setFormData(currentUser || {});
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previousFormData) => ({
            ...previousFormData,
            [name]: value,
        }));
    };

    const handleUpdateInfo = () => {
        if (!updateInfo) {
            setFormData(user || {});
            setUpdateInfo(true);
        } else {
            const payload = {};

            if ((formData.first_name || '').trim() !== '') {
                payload.first_name = formData.first_name.trim();
            }

            if ((formData.last_name || '').trim() !== '') {
                payload.last_name = formData.last_name.trim();
            }

            if ((formData.username || '').trim() !== '') {
                payload.username = formData.username.trim();
            }

            if (Object.keys(payload).length === 0) {
                setUpdateInfo(false);
                return;
            }

            updateUserProfile(user.id, payload)
                .then((response) => {
                    const updatedUser = response.user;
                    localStorage.setItem('user', JSON.stringify(updatedUser));
                    setUser(updatedUser);
                    setFormData(updatedUser);
                    setUpdateInfo(false);
                })
                .catch((error) => {
                    alert(error.message);
                });
        }
    };

    // Determine button text based on state
    const buttonText = updateInfo ? "Submit" : "Update Info";

    return (
        <main className="profile-page">
            <section className="profile-shell">
                <header className="profile-hero">
                    <div>
                        <p className="profile-kicker">Account</p>
                        <h1 className="profile-title">Profile</h1>
                        <p className="profile-subtitle">
                            Review your account details and update the fields that matter most.
                        </p>
                    </div>
                    {user ? (
                        <div className="profile-avatar" aria-hidden="true">
                            {(user.username || 'U').slice(0, 1).toUpperCase()}
                        </div>
                    ) : null}
                </header>

                <div className="profile-card">
                {user ? (
                    <>
                        <div className="profile-grid">
                            <section className="profile-section profile-section-wide">
                                <span className="profile-label">User ID</span>
                                <p className="profile-value mono">{user.id}</p>
                            </section>

                            <section className="profile-section profile-section-wide">
                                <span className="profile-label">Username</span>
                                {updateInfo ? (
                                    <input
                                        className="profile-input"
                                        type="text"
                                        name="username"
                                        value={formData.username || ''}
                                        onChange={handleChange}
                                    />
                                ) : (
                                    <p className="profile-value">{user.username}</p>
                                )}
                            </section>

                            <div className="profile-row">
                                <section className="profile-section">
                                    <span className="profile-label">First Name</span>
                                    {updateInfo ? (
                                        <input
                                            className="profile-input"
                                            type="text"
                                            name="first_name"
                                            value={formData.first_name || ''}
                                            onChange={handleChange}
                                        />
                                    ) : (
                                        <p className="profile-value">{user.first_name || 'Not provided'}</p>
                                    )}
                                </section>

                                <section className="profile-section">
                                    <span className="profile-label">Last Name</span>
                                    {updateInfo ? (
                                        <input
                                            className="profile-input"
                                            type="text"
                                            name="last_name"
                                            value={formData.last_name || ''}
                                            onChange={handleChange}
                                        />
                                    ) : (
                                        <p className="profile-value">{user.last_name || 'Not provided'}</p>
                                    )}
                                </section>
                            </div>

                            <section className="profile-section profile-section-wide">
                                <span className="profile-label">Email</span>
                                <p className="profile-value">{user.email}</p>
                            </section>

                            <section className="profile-section profile-section-wide">
                                <span className="profile-label">Date of Birth</span>
                                <p className="profile-value">{user.dob || 'Not provided'}</p>
                            </section>
                        </div>

                        <div className="profile-actions">
                            <button
                                className="update-info-button"
                                onClick={handleUpdateInfo}
                            >
                                {buttonText}
                            </button>
                            <Button
                                className="profile-settings-button"
                                href="/settings"
                                name="Go to Settings"
                            />
                        </div>
                    </>
                ) : (
                    <>
                        <p className="empty-profile-copy">You need to login to see your profile.</p>
                        <Link className="button explore-prices profile-login-button" to="/login">Login</Link>
                    </>
                )}
                </div>
            </section>
        </main>
    );
}

export default Profile;
