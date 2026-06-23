import { Link } from 'react-router-dom';
import { getUser } from '../utils/auth.js';
import { useEffect, useState } from 'react';
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
            <div className="empty-profile">
                <h2 className="empty-profile-title">Profile</h2>
                {user ? (
                    <>
                        <p><b>User Id:</b> {user.id}</p>
                        <div className="name-row">
                            <p>
                                <b>First Name:</b>{' '}
                                {updateInfo ? (
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name || ''}
                                        onChange={handleChange}
                                    />
                                ) : (
                                    user.first_name
                                )}
                            </p>
                            <p>
                                <b>Last Name:</b>{' '}
                                {updateInfo ? (
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name || ''}
                                        onChange={handleChange}
                                    />
                                ) : (
                                    user.last_name
                                )}
                            </p>
                        </div>
                        <p>
                            <b>Username:</b>{' '}
                            {updateInfo ? (
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username || ''}
                                    onChange={handleChange}
                                />
                            ) : (
                                user.username
                            )}
                        </p>
                        <p>
                            <b>Email:</b> {user.email}
                        </p>
                        <p>
                            <b>Date of Birth:</b>{' '}
                            {user.dob}
                        </p>
                    </>
                ) : (
                    <>
                        <p>You need to login to see your profile.</p>
                        <Link className="button explore-prices" to="/login">Login</Link>
                    </>
                )}
                
                <button 
                    className='update-info-button' 
                    onClick={handleUpdateInfo}
                >
                    {buttonText}
                </button>
            </div>
        </main>
    );
}

export default Profile;
