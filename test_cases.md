# Book-Streaming Application - Complete Test Cases Document

## Table of Contents
1. [Authentication Tests](#1-authentication-tests)
2. [Book Management Tests](#2-book-management-tests)
3. [Mark/Bookmark Tests](#3-markbookmark-tests)
4. [Reading Session Tests](#4-reading-session-tests)
5. [Review Tests](#5-review-tests)
6. [Social/Follow Tests](#6-socialfollow-tests)
7. [User Profile Tests](#7-user-profile-tests)
8. [Unit Tests - Validation](#8-unit-tests---validation)
9. [Unit Tests - Models](#9-unit-tests---models)
10. [Unit Tests - Utilities Extended](#10-unit-tests---utilities-extended)
11. [Edge Cases](#11-edge-cases)
12. [End-to-End Tests](#12-end-to-end-tests)
13. [Miscellaneous Tests](#13-miscellaneous-tests)

---

## 1. Authentication Tests

### 1.1 Registration Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TA01 | Register with valid data | 1. POST /auth/register<br>2. Valid user data | email: test@example.com<br>name: Test User<br>password: TestPass123! | Status 201<br>user_id returned<br>Password not in response | As Expected | Pass |
| TA02 | Register with duplicate email | 1. Register user<br>2. Register same email | email: existing@test.com | Status 400<br>"already registered" | As Expected | Pass |
| TA03 | Register with invalid email | 1. POST /auth/register<br>2. Invalid email format | email: notanemail | Status 400/422<br>Validation error | As Expected | Pass |
| TA04 | Register with weak password | 1. POST /auth/register<br>2. Weak password | password: weak | Status 400/422<br>Password validation failed | As Expected | Pass |

### 1.2 Login Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TA05 | Login with valid credentials | 1. POST /auth/login<br>2. Valid email/password | email: test@example.com<br>password: TestPass123! | Status 200<br>access_token returned<br>token_type: bearer | As Expected | Pass |
| TA06 | Login with wrong password | 1. POST /auth/login<br>2. Wrong password | password: WrongPassword1! | Status 401<br>"invalid" in response | As Expected | Pass |
| TA07 | Login with non-existent email | 1. POST /auth/login<br>2. Unknown email | email: nonexistent@example.com | Status 401 | As Expected | Pass |
| TA08 | Login returns user info | 1. POST /auth/login<br>2. Check response | Valid credentials | user_id, email, name, streak in response | As Expected | Pass |

### 1.3 Authentication Flow Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TA09 | Register then login flow | 1. Register<br>2. Login<br>3. Access /users/me | New user | All steps succeed | As Expected | Pass |
| TA10 | Protected route without token | 1. GET /users/me<br>2. No Authorization header | None | Status 401 | As Expected | Pass |
| TA11 | Protected route invalid token | 1. GET /users/me<br>2. Invalid Bearer token | Bearer invalid-token | Status 401 | As Expected | Pass |

---

## 2. Book Management Tests

### 2.1 Book Creation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TB01 | Create book with valid data | 1. POST /books<br>2. Auth + valid data | title: Test Book<br>author_name: Author | Status 201<br>book_id returned | As Expected | Pass |
| TB02 | Create book without auth | 1. POST /books<br>2. No auth header | title: Test Book | Status 401 | As Expected | Pass |
| TB03 | Create book empty title | 1. POST /books<br>2. Empty title | title: "" | Status 400/422 | As Expected | Pass |
| TB04 | Create book empty author | 1. POST /books<br>2. Empty author | author_name: "" | Status 400/422 | As Expected | Pass |

### 2.2 Book Retrieval Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TB05 | Get list of books | 1. GET /books | None | Status 200<br>Array of books | As Expected | Pass |
| TB06 | Get book by ID | 1. GET /books/{id} | Valid book_id | Status 200<br>Book details | As Expected | Pass |
| TB07 | Get non-existent book | 1. GET /books/{id} | Invalid book_id | Status 404 | As Expected | Pass |
| TB08 | Search books by title | 1. GET /books?title=search | title: partial | Status 200<br>Filtered results | As Expected | Pass |
| TB09 | Search books by author | 1. GET /books?author=search | author: partial | Status 200<br>Filtered results | As Expected | Pass |
| TB10 | Books pagination | 1. GET /books?limit=5&offset=0 | limit: 5 | Max 5 results | As Expected | Pass |

### 2.3 Book Update Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TB11 | Update book title (owner) | 1. PUT /books/{id}<br>2. Auth as owner | title: Updated | Status 200<br>Title updated | As Expected | Pass |
| TB12 | Update book (non-owner) | 1. PUT /books/{id}<br>2. Different user | Different token | Status 404 | As Expected | Pass |

### 2.4 Book Deletion Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TB13 | Delete own book | 1. DELETE /books/{id}<br>2. Auth as owner | Owner token | Status 200 | As Expected | Pass |
| TB14 | Delete book without auth | 1. DELETE /books/{id}<br>2. No auth | None | Status 401 | As Expected | Pass |
| TB15 | Delete non-existent book | 1. DELETE /books/{id} | Invalid book_id | Status 404 | As Expected | Pass |
| TB16 | Delete book (non-owner) | 1. DELETE /books/{id}<br>2. Different user | Different token | Status 404 | As Expected | Pass |

---

## 3. Mark/Bookmark Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TM01 | Mark a book | 1. POST /books/{id}/mark | Valid book_id | Status 200 | As Expected | Pass |
| TM02 | Mark already marked book | 1. Mark book<br>2. Mark again | Same book | Status 400 | As Expected | Pass |
| TM03 | Unmark a book | 1. DELETE /books/{id}/mark | Marked book | Status 200 | As Expected | Pass |
| TM04 | Unmark not marked book | 1. DELETE /books/{id}/mark | Not marked | Status 404 | As Expected | Pass |
| TM05 | Get marked books list | 1. GET /users/me/marks | Valid auth | Status 200<br>Array | As Expected | Pass |
| TM06 | Check if marked (yes) | 1. GET /books/{id}/is-marked | Marked book | is_marked: true | As Expected | Pass |
| TM07 | Check if marked (no) | 1. GET /books/{id}/is-marked | Not marked | is_marked: false | As Expected | Pass |

---

## 4. Reading Session Tests

### 4.1 Session Creation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TRS01 | Start reading session | 1. POST /books/{id}/reading-sessions | start_time: now | Status 201 | As Expected | Pass |
| TRS02 | Start session without auth | 1. POST<br>2. No auth | start_time | Status 401 | As Expected | Pass |
| TRS03 | Start session non-existent book | 1. POST invalid book | Invalid book_id | Status 404 | As Expected | Pass |
| TRS04 | Start session with end time | 1. POST with both times | start + end time | Status 201<br>Duration calculated | As Expected | Pass |

### 4.2 Session Update Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TRS05 | End reading session | 1. Start session<br>2. PUT end_time | Valid session | Status 200<br>Duration set | As Expected | Pass |
| TRS06 | End non-existent session | 1. PUT invalid session | Invalid session_id | Status 404 | As Expected | Pass |
| TRS07 | End session without auth | 1. PUT<br>2. No auth | Valid session | Status 401 | As Expected | Pass |
| TRS08 | End already ended session | 1. End<br>2. End again | Ended session | Status 400 | As Expected | Pass |

### 4.3 Session Retrieval Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TRS09 | Get my reading sessions | 1. GET /users/me/reading-sessions | Valid auth | Status 200 | As Expected | Pass |
| TRS10 | Filter sessions by book | 1. GET ?book_id={id} | Specific book | Filtered results | As Expected | Pass |
| TRS11 | Sessions pagination | 1. GET ?limit=5 | limit: 5 | Max 5 results | As Expected | Pass |
| TRS12 | Get book reading sessions | 1. GET /books/{id}/reading-sessions | Valid book | Status 200 | As Expected | Pass |

### 4.4 Reading Stats Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TRS13 | Get weekly stats | 1. GET ?period=week | period: week | Status 200 | As Expected | Pass |
| TRS14 | Get monthly stats | 1. GET ?period=month | period: month | Status 200 | As Expected | Pass |
| TRS15 | Get yearly stats | 1. GET ?period=year | period: year | Status 200 | As Expected | Pass |
| TRS16 | Stats without auth | 1. GET<br>2. No auth | None | Status 401 | As Expected | Pass |

---

## 5. Review Tests

### 5.1 Review Creation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TR01 | Create review with rating/comment | 1. POST /books/{id}/reviews | rating: 4.0<br>comment: Great! | Status 201 | As Expected | Pass |
| TR02 | Create review rating only | 1. POST<br>2. Rating only | rating: 5.0 | Status 201 | As Expected | Pass |
| TR03 | Create duplicate review | 1. Create<br>2. Create again | Same book | Status 400 | As Expected | Pass |
| TR04 | Create review invalid rating | 1. POST<br>2. Rating > 5 | rating: 10 | Status 400 | As Expected | Pass |
| TR05 | Create review without auth | 1. POST<br>2. No auth | rating: 4.0 | Status 401 | As Expected | Pass |

### 5.2 Review Retrieval Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TR06 | Get book reviews | 1. GET /books/{id}/reviews | Valid book | Status 200<br>items array | As Expected | Pass |
| TR07 | Get my reviews | 1. GET /users/me/reviews | Valid auth | Status 200 | As Expected | Pass |
| TR08 | Get reviews summary | 1. GET /books/{id}/reviews/summary | Valid book | average_rating, total | As Expected | Pass |
| TR09 | Reviews sorted by date | 1. GET ?sort_by=created_at | sort_by param | Sorted results | As Expected | Pass |
| TR10 | Reviews sorted by rating | 1. GET ?sort_by=rating | sort_by param | Sorted results | As Expected | Pass |

### 5.3 Review Update/Delete Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TR11 | Update own review | 1. PUT /reviews/{id} | New rating | Status 200 | As Expected | Pass |
| TR12 | Delete own review | 1. DELETE /reviews/{id} | Owner token | Status 200 | As Expected | Pass |
| TR13 | Delete non-existent review | 1. DELETE invalid | Invalid id | Status 404 | As Expected | Pass |
| TR14 | Delete without auth | 1. DELETE<br>2. No auth | None | Status 401 | As Expected | Pass |

---

## 6. Social/Follow Tests

### 6.1 Follow Action Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TS01 | Follow another user | 1. POST /users/{id}/follow | Target user_id | Status 200 | As Expected | Pass |
| TS02 | Follow same user twice | 1. Follow<br>2. Follow again | Same user | Status 400 | As Expected | Pass |
| TS03 | Follow yourself | 1. POST self | Own user_id | Status 400 | As Expected | Pass |
| TS04 | Follow non-existent user | 1. POST invalid | Invalid user | Status 404 | As Expected | Pass |
| TS05 | Follow without auth | 1. POST<br>2. No auth | None | Status 401 | As Expected | Pass |
| TS06 | Unfollow a user | 1. Follow<br>2. DELETE | Following user | Status 200 | As Expected | Pass |
| TS07 | Unfollow not following | 1. DELETE | Not following | Status 404 | As Expected | Pass |

### 6.2 Follower Retrieval Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TS08 | Get users I follow | 1. GET /users/me/following | Valid auth | Status 200 | As Expected | Pass |
| TS09 | Get my followers | 1. GET /users/me/followers | Valid auth | Status 200 | As Expected | Pass |
| TS10 | Following pagination | 1. GET ?limit=5 | limit: 5 | Max 5 results | As Expected | Pass |
| TS11 | Followers pagination | 1. GET ?limit=5 | limit: 5 | Max 5 results | As Expected | Pass |
| TS12 | Get following without auth | 1. GET<br>2. No auth | None | Status 401 | As Expected | Pass |
| TS13 | Get followers without auth | 1. GET<br>2. No auth | None | Status 401 | As Expected | Pass |

### 6.3 Follow Status Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TS14 | Check status (following) | 1. Follow<br>2. GET status | Following | is_following: true | As Expected | Pass |
| TS15 | Check status (not following) | 1. GET status | Not following | is_following: false | As Expected | Pass |
| TS16 | Status without auth | 1. GET<br>2. No auth | None | Status 401 | As Expected | Pass |

---

## 7. User Profile Tests

### 7.1 Profile Update Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TU01 | Update user name | 1. PUT /users/me | name: Updated | Status 200 | As Expected | Pass |
| TU02 | Update password | 1. PUT<br>2. Login new pw | password: NewSecure123! | Password works | As Expected | Pass |
| TU03 | Update weak password | 1. PUT | password: weak | Status 400/422 | As Expected | Pass |
| TU04 | Update without auth | 1. PUT<br>2. No auth | name: New | Status 401 | As Expected | Pass |

### 7.2 Public Profile Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TU05 | Get other user's profile | 1. GET /users/{id}/profile | Valid user | Status 200 | As Expected | Pass |
| TU06 | Get non-existent profile | 1. GET invalid | Invalid user | Status 404 | As Expected | Pass |
| TU07 | Get profile without auth | 1. GET<br>2. No auth | Valid user | Status 401 | As Expected | Pass |

### 7.3 User Search Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TU08 | Search users by name | 1. GET /users?query=test | query: test | Matching users | As Expected | Pass |
| TU09 | Search users no query | 1. GET /users | None | All users | As Expected | Pass |
| TU10 | Search no results | 1. GET ?query=xyz | Non-matching | Empty array | As Expected | Pass |
| TU11 | Search pagination | 1. GET ?limit=5 | limit: 5 | Max 5 results | As Expected | Pass |
| TU12 | Search without auth | 1. GET<br>2. No auth | None | Status 401 | As Expected | Pass |

### 7.4 User Reading Sessions Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TU13 | Get other user's sessions | 1. GET /users/{id}/reading-sessions | Valid user | Status 200 | As Expected | Pass |
| TU14 | User sessions pagination | 1. GET ?limit=5 | limit: 5 | Max 5 results | As Expected | Pass |
| TU15 | Sessions non-existent user | 1. GET invalid | Invalid user | Status 404 | As Expected | Pass |
| TU16 | Sessions without auth | 1. GET<br>2. No auth | Valid user | Status 401 | As Expected | Pass |

---

## 8. Unit Tests - Validation

### 8.1 Email Validation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UV01 | Valid email formats | 1. Call validate_email() | user@example.com, user.name@domain.org | Returns True | As Expected | Pass |
| UV02 | Invalid email formats | 1. Call validate_email() | notanemail, @domain.com, user@ | Returns False | As Expected | Pass |

### 8.2 Password Validation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UV03 | Valid passwords | 1. Call validate_password() | SecurePass123! | is_valid: True | As Expected | Pass |
| UV04 | Password too short | 1. Call validate_password() | Abc1! | is_valid: False | As Expected | Pass |
| UV05 | Password no uppercase | 1. Call validate_password() | securepass123! | is_valid: False | As Expected | Pass |
| UV06 | Password no lowercase | 1. Call validate_password() | SECUREPASS123! | is_valid: False | As Expected | Pass |
| UV07 | Password no digit | 1. Call validate_password() | SecurePass! | is_valid: False | As Expected | Pass |
| UV08 | Password no special char | 1. Call validate_password() | SecurePass123 | is_valid: False | As Expected | Pass |

### 8.3 Author Name Validation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UV09 | Valid author names | 1. Call validate_author_name() | J.K. Rowling, George Orwell | Returns True | As Expected | Pass |
| UV10 | Empty author name | 1. Call validate_author_name() | "" | Returns False | As Expected | Pass |
| UV11 | Whitespace only name | 1. Call validate_author_name() | "   " | Returns False | As Expected | Pass |
| UV12 | Name too long | 1. Call validate_author_name() | 200+ chars | Returns False | As Expected | Pass |

### 8.4 Utility Function Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UV13 | Generate ID uniqueness | 1. Generate 100 IDs | None | All unique | As Expected | Pass |
| UV14 | Generate ID format | 1. Generate ID | None | Valid UUID format | As Expected | Pass |
| UV15 | Hash password not plain | 1. hash_password() | TestPass123! | Hash != plain | As Expected | Pass |
| UV16 | Sanitize filename special chars | 1. sanitize_filename() | file<>:"/\|?*.txt | Special chars removed | As Expected | Pass |
| UV17 | Sanitize filename empty | 1. sanitize_filename() | "" | Returns default | As Expected | Pass |
| UV18 | Get cover URL with filename | 1. get_cover_url() | cover.jpg | Full URL path | As Expected | Pass |
| UV19 | Get cover URL empty | 1. get_cover_url() | None | Returns None | As Expected | Pass |

---

## 9. Unit Tests - Models

### 9.1 User Model Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UM01 | UserCreate valid | 1. Create UserCreate | Valid data | Model created | As Expected | Pass |
| UM02 | UserCreate invalid email | 1. Create | Invalid email | ValidationError | As Expected | Pass |
| UM03 | UserCreate weak password | 1. Create | Weak password | ValidationError | As Expected | Pass |
| UM04 | UserCreate empty name | 1. Create | Empty name | ValidationError | As Expected | Pass |
| UM05 | UserLogin valid | 1. Create UserLogin | Valid data | Model created | As Expected | Pass |
| UM06 | UserUpdate optional fields | 1. Create UserUpdate | Empty | All fields None | As Expected | Pass |
| UM07 | UserUpdate with name | 1. Create | name only | name set, password None | As Expected | Pass |
| UM08 | UserResponse from dict | 1. Create from dict | Valid dict | All fields mapped | As Expected | Pass |

### 9.2 Book Model Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UM09 | BookBase valid | 1. Create BookBase | Valid data | Model created | As Expected | Pass |
| UM10 | BookBase with date | 1. Create | With publish_date | Date stored | As Expected | Pass |
| UM11 | BookBase empty title | 1. Create | Empty title | ValidationError | As Expected | Pass |
| UM12 | BookBase empty author | 1. Create | Empty author | ValidationError | As Expected | Pass |
| UM13 | BookBase title trimmed | 1. Create | "  Title  " | Title trimmed | As Expected | Pass |
| UM14 | BookUpdate all optional | 1. Create | Empty | All fields None | As Expected | Pass |
| UM15 | BookResponse from dict | 1. Create from dict | Valid dict | All fields mapped | As Expected | Pass |

### 9.3 Review Model Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UM16 | ReviewCreate valid | 1. Create | rating + comment | Model created | As Expected | Pass |
| UM17 | ReviewCreate rating only | 1. Create | rating only | Model created | As Expected | Pass |
| UM18 | ReviewCreate comment only | 1. Create | comment only | Model created | As Expected | Pass |
| UM19 | Review rating > 5 | 1. Create | rating: 10 | ValidationError | As Expected | Pass |
| UM20 | Review rating < 0 | 1. Create | rating: -1 | ValidationError | As Expected | Pass |
| UM21 | ReviewResponse from dict | 1. Create from dict | Valid dict | All fields mapped | As Expected | Pass |

### 9.4 Reading Session Model Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UM22 | ReadingSessionBase valid | 1. Create | start_time | Model created | As Expected | Pass |
| UM23 | ReadingSession end < start | 1. Create | end before start | ValidationError | As Expected | Pass |

---

## 10. Unit Tests - Utilities Extended

### 10.1 Password Verification Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE01 | Verify correct password | 1. Hash password<br>2. Verify | Correct password | Returns True | As Expected | Pass |
| UE02 | Verify wrong password | 1. Hash password<br>2. Verify different | Wrong password | Returns False | As Expected | Pass |
| UE03 | Verify invalid hash format | 1. Verify with bad hash | Invalid hash | Returns False | As Expected | Pass |
| UE04 | Verify empty password | 1. Verify "" | Empty string | Returns False | As Expected | Pass |

### 10.2 Image Extension Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE05 | JPEG extension | 1. get_image_extension() | image/jpeg | Returns .jpg | As Expected | Pass |
| UE06 | JPG extension | 1. get_image_extension() | image/jpg | Returns .jpg | As Expected | Pass |
| UE07 | PNG extension | 1. get_image_extension() | image/png | Returns .png | As Expected | Pass |
| UE08 | WebP extension | 1. get_image_extension() | image/webp | Returns .webp | As Expected | Pass |
| UE09 | Unknown extension | 1. get_image_extension() | unknown/type | Returns .jpg | As Expected | Pass |

### 10.3 Streak Calculation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE10 | First login no previous | 1. calculate_streak() | last_login: None | streak: 1 | As Expected | Pass |
| UE11 | Same day login | 1. calculate_streak() | Same day | Streak unchanged | As Expected | Pass |
| UE12 | Consecutive day login | 1. calculate_streak() | Yesterday | Streak +1 | As Expected | Pass |
| UE13 | Streak broken | 1. calculate_streak() | 3+ days ago | Streak reset to 1 | As Expected | Pass |

### 10.4 Rate Limiter Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE14 | Allows first request | 1. RateLimiter.is_allowed() | First request | Returns True | As Expected | Pass |
| UE15 | Allows under limit | 1. Multiple requests under limit | Under max | Returns True | As Expected | Pass |
| UE16 | Blocks over limit | 1. Exceed limit | Over max | Returns False | As Expected | Pass |
| UE17 | Different users tracked separately | 1. Requests from 2 users | user1, user2 | Each has own limit | As Expected | Pass |

### 10.5 Image Validation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE18 | Valid image file | 1. validate_image_file() | Valid JPEG | Returns True | As Expected | Pass |
| UE19 | Invalid content type | 1. validate_image_file() | text/plain | Returns False | As Expected | Pass |
| UE20 | File too large | 1. validate_image_file() | > max size | Returns False | As Expected | Pass |
| UE21 | Empty filename | 1. validate_image_file() | No filename | Returns False | As Expected | Pass |

### 10.6 Book Data Validation Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE22 | Valid book data | 1. validate_book_data() | Valid title/author | is_valid: True | As Expected | Pass |
| UE23 | Empty title validation | 1. validate_book_data() | Empty title | is_valid: False | As Expected | Pass |
| UE24 | Empty author validation | 1. validate_book_data() | Empty author | is_valid: False | As Expected | Pass |

### 10.7 Delete Book Cover Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| UE25 | Delete existing cover | 1. delete_book_cover() | Existing file | File deleted | As Expected | Pass |
| UE26 | Delete non-existent cover | 1. delete_book_cover() | Missing file | No error | As Expected | Pass |
| UE27 | Delete with path traversal | 1. delete_book_cover() | ../file | Blocked/ignored | As Expected | Pass |

---

## 11. Edge Cases

### 11.1 Book Edge Cases

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TE01 | Create book empty title | 1. POST /books | title: "" | Status 400/422 | As Expected | Pass |
| TE02 | Create book empty author | 1. POST /books | author: "" | Status 400/422 | As Expected | Pass |
| TE03 | Books pagination | 1. GET ?limit=5&offset=0 | Pagination params | Paginated results | As Expected | Pass |
| TE04 | Filter by author | 1. GET ?author=name | Author filter | Filtered books | As Expected | Pass |
| TE05 | Filter by title | 1. GET ?title=name | Title filter | Filtered books | As Expected | Pass |
| TE06 | Update not owner | 1. PUT<br>2. Different user | Other user's book | Status 404 | As Expected | Pass |
| TE07 | Delete not owner | 1. DELETE<br>2. Different user | Other user's book | Status 404 | As Expected | Pass |

### 11.2 Review Edge Cases

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TE08 | Invalid rating | 1. POST review | rating: 10 | Status 400 | As Expected | Pass |
| TE09 | Duplicate review | 1. Create<br>2. Create again | Same book | Status 400 | As Expected | Pass |
| TE10 | Get book reviews | 1. GET /books/{id}/reviews | Valid book | Status 200 | As Expected | Pass |
| TE11 | Get my reviews | 1. GET /users/me/reviews | Valid auth | Status 200 | As Expected | Pass |
| TE12 | Update review | 1. PUT /reviews/{id} | New data | Status 200 | As Expected | Pass |

### 11.3 Mark Edge Cases

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TE13 | Mark already marked | 1. Mark<br>2. Mark again | Same book | Status 400 | As Expected | Pass |
| TE14 | Unmark not marked | 1. Unmark | Not marked | Status 404 | As Expected | Pass |
| TE15 | Get marked books | 1. GET /users/me/marks | Valid auth | Status 200 | As Expected | Pass |

### 11.4 Reading Session Edge Cases

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TE16 | End already ended | 1. End<br>2. End again | Ended session | Status 400 | As Expected | Pass |
| TE17 | Invalid stats period | 1. GET ?period=invalid | Bad period | Status 400 | As Expected | Pass |

### 11.5 Social Edge Cases

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TE18 | Follow already following | 1. Follow<br>2. Follow again | Same user | Status 400 | As Expected | Pass |
| TE19 | Follow self | 1. Follow own ID | Self | Status 400 | As Expected | Pass |

---

## 12. End-to-End Tests

### 12.1 Complete User Journey Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| E2E01 | New user complete flow | 1. Register<br>2. Login<br>3. Create Book<br>4. Review<br>5. Mark | New user | All steps succeed | As Expected | Pass |
| E2E02 | Book discovery flow | 1. Browse<br>2. Search<br>3. View Details<br>4. Mark | Browsing user | All steps succeed | As Expected | Pass |
| E2E03 | Review interaction flow | 1. Create Review<br>2. Update Review<br>3. View Reviews | Review user | All steps succeed | As Expected | Pass |

### 12.2 Error Handling Journey Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| E2E04 | Unauthorized actions flow | 1. Try protected endpoints<br>2. Without auth | No auth | All return 401 | As Expected | Pass |
| E2E05 | Not found resources flow | 1. Access invalid IDs | Invalid IDs | All return 404 | As Expected | Pass |

---

## 13. Miscellaneous Tests

### 13.1 Health Check Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH01 | Health check endpoint | 1. GET /health | None | status: healthy | As Expected | Pass |

### 13.2 Admin Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH02 | Verify a book | 1. PATCH /admin/books/{id}/verify | verify: true | Book verified | As Expected | Pass |
| TH03 | Unverify a book | 1. PATCH /admin/books/{id}/verify | verify: false | Book unverified | As Expected | Pass |
| TH04 | Verify non-existent | 1. PATCH invalid | Invalid book | Status 404 | As Expected | Pass |

### 13.3 Book Stats Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH05 | Get book stats | 1. GET /books/stats | None | total_books count | As Expected | Pass |

### 13.4 Book Filter Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH06 | Filter verified books | 1. GET ?verified=true | verified: true | Only verified | As Expected | Pass |
| TH07 | Filter unverified books | 1. GET ?verified=false | verified: false | Only unverified | As Expected | Pass |

### 13.5 Frontend Routes Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH08 | Serve index | 1. GET / | None | Status 200 | As Expected | Pass |
| TH09 | Serve dashboard | 1. GET /dashboard | None | Status 200 | As Expected | Pass |
| TH10 | Serve login | 1. GET /login | None | Status 200 | As Expected | Pass |
| TH11 | Serve timer | 1. GET /timer | None | Status 200 | As Expected | Pass |
| TH12 | Serve profile | 1. GET /profile | None | Status 200 | As Expected | Pass |
| TH13 | Serve social | 1. GET /social | None | Status 200 | As Expected | Pass |
| TH14 | Serve user-profile | 1. GET /user-profile | None | Status 200 | As Expected | Pass |

### 13.6 Check Mark Status Tests

| Test Case ID | Test Scenario | Test Steps | Test Data | Expected Results | Actual Results | Pass/Fail |
|---|---|---|---|---|---|---|
| TH15 | Check is marked (yes) | 1. Mark<br>2. Check | Marked book | is_marked: true | As Expected | Pass |
| TH16 | Check is marked (no) | 1. Check | Not marked | is_marked: false | As Expected | Pass |

---

## Test Summary

| Category | Tests |
|---|---|
| Authentication (test_auth.py) | 11 |
| Book Management (test_books.py) | 18 |
| Mark/Bookmark | 7 |
| Reading Sessions (test_reading_sessions.py) | 17 |
| Reviews | 14 |
| Social/Follow (test_social.py) | 19 |
| User Profile (test_users.py) | 16 |
| Unit - Validation (test_utils.py) | 18 |
| Unit - Models (test_models.py) | 24 |
| Unit - Utilities Extended (test_utils_extended.py) | 35 |
| Edge Cases (test_edge_cases.py) | 25 |
| End-to-End (test_user_journey.py) | 5 |
| Miscellaneous (test_misc.py) | 20 |
| **TOTAL** | **229** |

---

*Document Generated: December 2024*
*Application: Book-Streaming Platform*
*Test Coverage: 84%*
