I will implement the missing Payment Logic and add Global CSRF Protection to enhance security.

### 1. Install Dependencies
- **Action**: Install `Flask-WTF` for CSRF protection.
- **File**: `requirements.txt` (Update to include `Flask-WTF`).

### 2. Implement Payment Logic (Backend)
- **File**: `app/views/student.py`
- **Change**: Update `pay_utility_bill` function to handle `POST` requests.
- **Logic**:
    - Verify the payment amount.
    - Create a `Payment` record in the database.
    - Update the `UtilityBill` status to `paid`.
    - Flash a success message and redirect to the bill list.

### 3. Implement Global CSRF Protection (Security)
- **File**: `app/__init__.py`
- **Change**: Initialize `CSRFProtect` from `flask_wtf` and attach it to the `app`.
- **File**: `app/templates/*.html` (Multiple files)
- **Change**: Add `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` to all forms in:
    - `login.html` (Login, Register, Forgot Password)
    - `student/pay_utility_bill.html`
    - `student/submit_repair.html`
    - `student/visitor_register.html`
    - `student/submit_dorm_change.html`
    - `student/my_info.html`
    - `admin/*.html` (Forms for adding/editing students, dorms, etc.)
- **File**: `app/templates/admin/visitors.html`
- **Change**: Add `X-CSRFToken` header to the AJAX request for marking visitors as left.

### 4. Verification
- **Test**: Verify that the payment process works (status updates to "Paid").
- **Test**: Verify that forms can still be submitted (CSRF token is valid).
- **Test**: Verify that AJAX requests in Admin panel work.
