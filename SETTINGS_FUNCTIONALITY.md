# Settings Page - Email and Password Change Functionality

## Overview

This document describes the implementation of email change and password change functionality in the document analyzer application. The functionality allows authenticated users to securely update their email address and password through the settings page.

## Backend Implementation

### 1. Database Schema

The `users` table includes the following relevant fields:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Pydantic Schemas

New schemas have been added to handle the change requests:

```python
class ChangeEmailRequest(BaseModel):
    new_email: str
    password: str  # Current password for verification
    
    @validator('new_email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email is required')
        return v.strip().lower()

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
```

### 3. CRUD Operations

Added methods to the `UserCRUD` class:

#### Change Email
```python
def change_user_email(self, user_id: UUID, new_email: str, password: str) -> Optional[User]:
    """Change user email after verifying current password"""
    # 1. Verify current password
    # 2. Check if new email already exists
    # 3. Update email in database
    # 4. Return updated user
```

#### Change Password
```python
def change_user_password(self, user_id: UUID, current_password: str, new_password: str) -> Optional[User]:
    """Change user password after verifying current password"""
    # 1. Verify current password
    # 2. Hash new password
    # 3. Update password in database
    # 4. Return updated user
```

### 4. API Endpoints

Two new endpoints have been added to the profile router:

#### POST `/api/profile/change-email`
- **Purpose**: Change user's email address
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "new_email": "newemail@example.com",
    "password": "current_password"
  }
  ```
- **Response**: 
  - Success (200): `{"message": "Email changed successfully", "new_email": "newemail@example.com"}`
  - Error (400): `{"detail": "Invalid password or email already exists"}`
  - Error (500): `{"detail": "Internal server error"}`

#### POST `/api/profile/change-password`
- **Purpose**: Change user's password
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "current_password": "old_password",
    "new_password": "new_password_123"
  }
  ```
- **Response**:
  - Success (200): `{"message": "Password changed successfully"}`
  - Error (400): `{"detail": "Invalid current password"}`
  - Error (500): `{"detail": "Internal server error"}`

## Frontend Implementation

### 1. Settings Component

The React settings component (`frontend/src/components/settings/settings.tsx`) includes:

- Form state management for both email and password changes
- Proper validation (password confirmation matching)
- API integration with proper error handling
- User feedback through success/error messages
- Loading states during API calls

### 2. Form Structure

#### Email Change Form
```jsx
<form onSubmit={handleChangeEmail}>
  <div className="form-group">
    <label>New Email Address</label>
    <input type="email" value={changeEmailForm.email} required />
  </div>
  <div className="form-group">
    <label>Current Password</label>
    <input type="password" value={changeEmailForm.password} required />
  </div>
  <button type="submit" disabled={loading}>
    {loading ? 'Changing...' : 'Change Email'}
  </button>
</form>
```

#### Password Change Form
```jsx
<form onSubmit={handleChangePassword}>
  <div className="form-group">
    <label>Current Password</label>
    <input type="password" value={changePasswordForm.currentPassword} required />
  </div>
  <div className="form-group">
    <label>New Password</label>
    <input type="password" value={changePasswordForm.newPassword} required />
  </div>
  <div className="form-group">
    <label>Confirm New Password</label>
    <input type="password" value={changePasswordForm.confirmPassword} required />
  </div>
  <button type="submit" disabled={loading}>
    {loading ? 'Changing...' : 'Change Password'}
  </button>
</form>
```

### 3. API Integration

The frontend makes authenticated requests to the backend:

```javascript
const response = await fetch('http://localhost:8000/api/profile/change-email', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    new_email: changeEmailForm.email,
    password: changeEmailForm.password,
  }),
});
```

## Security Features

1. **Password Verification**: Current password must be provided for both email and password changes
2. **Email Uniqueness**: System prevents duplicate email addresses
3. **Password Hashing**: New passwords are securely hashed using bcrypt
4. **Authentication Required**: All endpoints require valid JWT tokens
5. **Input Validation**: Proper validation on both frontend and backend
6. **Error Handling**: Secure error messages that don't leak sensitive information

## Usage Instructions

### For Users:

1. **Navigate to Settings**: Go to the settings page in the application
2. **Change Email**:
   - Enter your new email address
   - Enter your current password for verification
   - Click "Change Email"
   - Receive confirmation message

3. **Change Password**:
   - Enter your current password
   - Enter your new password (minimum 8 characters)
   - Confirm your new password
   - Click "Change Password"
   - Receive confirmation message

### For Developers:

1. **Start the Backend**:
   ```bash
   cd /path/to/document-analyzer
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend**:
   ```bash
   cd /path/to/document-analyzer/frontend
   npm run dev
   ```

3. **Test the Functionality**:
   ```bash
   python test_settings_functionality.py
   ```

## Error Handling

The system includes comprehensive error handling:

- **Frontend**: User-friendly error messages with proper loading states
- **Backend**: Proper HTTP status codes and detailed error messages
- **Database**: Transaction safety and constraint validation
- **Authentication**: Secure token validation and user verification

## Future Enhancements

Potential improvements for the settings functionality:

1. **Email Verification**: Send confirmation emails for email changes
2. **Password Strength Meter**: Visual feedback for password strength
3. **2FA Integration**: Two-factor authentication setup
4. **Account Recovery**: Password reset via email
5. **Audit Log**: Track security-related changes
6. **Rate Limiting**: Prevent brute force attacks on password changes

## Testing

The `test_settings_functionality.py` file provides basic API testing. For comprehensive testing:

1. **Unit Tests**: Test individual CRUD operations
2. **Integration Tests**: Test complete user flows
3. **Security Tests**: Test authentication and authorization
4. **UI Tests**: Test frontend functionality with Selenium or similar

## Troubleshooting

Common issues and solutions:

1. **"Authentication required" error**: Ensure valid JWT token is provided
2. **"Invalid password" error**: Verify current password is correct
3. **"Email already exists" error**: Check if email is already in use
4. **Database connection errors**: Verify database is running and accessible
5. **CORS errors**: Ensure frontend and backend URLs are properly configured
