# Testing

> [!NOTE]  
> Return back to the [README.md](README.md) file.


## Code Validation


### HTML

| Directory | File | Screenshot | Notes |
| --- | --- | --- | --- |
| templates | 404.html | ![screenshot](documentation/validation/html/404.png) | |
| templates | 500.html | ![screenshot](documentation/validation/html/500.png) | |
| templates | about.html | ![screenshot](documentation/validation/html/about.png) | |
| templates | cart.html | ![screenshot](documentation/validation/html/cart.png) | |
| templates | checkout.html | ![screenshot](documentation/validation/html/checkout.png) | |
| templates | contact.html | ![screenshot](documentation/validation/html/contact.png) | |
| templates | faq.html | ![screenshot](documentation/validation/html/faq.png) | |
| templates | index.html | ![screenshot](documentation/validation/html/index.png) | |
| templates | library.html | ![screenshot](documentation/validation/html/library.png) | |
| templates | wishlist.html | ![screenshot](documentation/validation/html/wishlist.png) | |

### Python (PEP8)
All Python files have been validated using PEP8 online checker with no significant issues.

Key files tested:
- forms.py
- views.py
- models.py
- urls.py
- settings.py

### CSS

I have used the recommended [CSS Jigsaw Validator](https://jigsaw.w3.org/css-validator) to validate all of my CSS files.

### JavaScript

I have used the recommended [JShint Validator](https://jshint.com) to validate all of my JS files.

## Browser Compatibility

I've tested my deployed project on multiple browsers to check for compatibility issues. Every page of the website is both functional and fully compatible with Google Chrome, Microsoft Edge and Mozilla Firefox. 


## Responsiveness

I've tested my deployed project with viewports of multiple width through DevTools. Every page is fully responsive - the website was designed on a mobile-first basis and is both fully functional and well-stylised for mobile, tablet, laptop and desktop users.

## Lighthouse Audit

All pages have achieved high lighthouse scores for both desktop and mobile users. 

## Manual Testing and Defensive Programming

Extensive manual testing was conducted across all user authentication flows and form submissions. The CustomSignupForm (referenced in forms.py, lines 10-98) implements robust validation including regex pattern matching for usernames, requiring a combination of letters, numbers, and special characters. Email confirmation is enforced through double-entry validation, and user type selection is mandatory. The social authentication flow (visible in set_user_type.html, lines 49-69) includes additional security measures requiring users to set up proper credentials even when using OAuth providers. Form validation includes defensive checks against SQL injection and XSS attacks through Django's built-in form validation and cleaning methods. The signup process (CustomSignupView, lines 469-507) includes automatic profile picture assignment with proper file handling and validation. All form submissions implement CSRF protection, and database queries are protected against injection attacks through Django's ORM. Error handling is comprehensive, with user-friendly messages displayed for all possible error states. The authentication system prevents unauthorized access to protected routes, with proper session management and timeout handling. Input validation is implemented both client-side (through HTML5 validation attributes) and server-side (through form cleaning methods), ensuring data integrity. The password requirements follow security best practices, enforcing minimum length and complexity requirements. All form submissions are validated against XSS attacks by escaping special characters and implementing proper content security policies. The system includes proper error handling for edge cases such as duplicate usernames, invalid email formats, and incomplete form submissions. User feedback is immediate and clear, with success and error messages implemented throughout the authentication flow.

## Bugs

### 1 - Social Authentication Error
During implementation of Google OAuth, users encountered a 'User has no attribute id' error during the callback phase. This was traced to the custom User model implementation. The fix involved modifying the pre_social_login adapter to use 'pk' instead of 'id', aligning with Django's recommended practice for custom user models.

### 2 - Form Validation Issues
The CustomSignupForm (referenced in forms.py) initially had issues with username validation. The fix involved implementing a more robust clean_username method with proper regex pattern matching and explicit validation error messages. This ensures usernames meet all requirements (length, special characters, uniqueness) before submission.

### 3 - Profile Picture Upload
There were issues with profile picture uploads after social authentication. The problem was traced to the CustomSignupView. The solution involved implementing proper file handling with ContentFile and adding defensive checks before attempting to save the default profile picture.

### 4 - Password Reset Flow
The password reset functionality in the UserTypeAndPasswordForm wasn't properly handling social auth users. Fixed by adding conditional logic in the form initialization. This ensures proper form field rendering regardless of authentication method.

### 5 - Form Styling Inconsistencies
Bootstrap styling was inconsistently applied across form fields. Resolved by implementing a uniform approach in the form's __init__ method. This ensures consistent styling across all form inputs while maintaining proper form validation feedback.

All bugs have been resolved and thoroughly tested to ensure proper functionality. The fixes include proper error handling, user feedback, and maintain security best practices throughout the authentication flow.

## Unfixed Bugs

There are no remaining bugs that I am aware of.