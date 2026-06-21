import { Link } from 'react-router-dom';
import { getUser } from '../utils/auth.js';
import { useState } from 'react';
import '../styles/page_style/profile.css';

function Profile() {
    const [updateInfo, setUpdateInfo] = useState(false);
    const user = getUser();

    const handleUpdateInfo = () => {
        if (updateInfo) {
            // If currently in 'Submit' mode, handle the submission logic here
            alert("Form submitted!");
            // Optional: Reset state after submission
            // setUpdateInfo(false); 
        } else {
            // If currently in 'Update Info' mode, switch to Edit mode
            alert("Switching to Edit mode...");
        }
        
        // Toggle the state
        setUpdateInfo(!updateInfo);
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
                            <p><b>First Name:</b> {user.first_name}</p>
                            <p><b>Last Name:</b> {user.last_name}</p>
                        </div>
                        <p><b>Username:</b> {user.username}</p>
                        <p><b>Email:</b> {user.email}</p>
                        <p><b>Date of Birth:</b> {user.dob}</p>
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