# Cornfield
Project for a Cornell University Hackathon called HackOurCampus (8/26/20 - 8/29/20)

*Made with HTML, CSS, Python, Jinja, Flask, MongoDB, JavaScript, JSON, and the Cornell Roster API*

See it live on Heroku: http://cornfield.herokuapp.com/index 
- (use email apb235@cornell.edu and password "password" without quotation marks to login if you don't have a @cornell.edu email)

# Purpose and Inspiration
COVID-19 has resulted in online learning for all. Even those with in-person classes,  those are hybrid with a transition to online. When a Zoom video ends, you don't see anyone except yourself in the reflection. But you want to see people. Everyone wants to be connected. 

**When you can't reach out to others in your class or taking classes that you're interested in, where can you go? Cornfield is the answer.** 

Cornfield allows for easy creation of study groups in any Cornell class. You can see others' contact information and similar classes/groups through a connect page, and see open study groups on any course page.

No study group? Create one on Cornfield.

# Features
- Gated pages where navbar with full features are only available to logged in users
- Signup that only allows for @cornell.edu emails and sends a verification email
- Login that only allows in verified users
- Corn SVG animation using CSS ("flying (rather, falling) corn")
- All subjects and courses called from the Cornell Roster API
- Join or create a study group
- Profile page
- Study tips page with random study tip generator made with JavaScript and study guides for users to share or use
- Connect page to find study buddies with hover flip in CSS

# Next Steps
- Add user's study styles to create different arrays for random study tips based on style
- Expand use of MongoDB database to recommend friends based on common classes or study groups
- Creating a study group page did not receive the Jinja navbar extension properly
- Add availability to Web (available in iOS) and take students’ free time (and timezones) into account to present study groups that fit their schedules

# Developers
Main Frontend: Althea Bata (Dyson '24)

Main Backend: Aaron Fink (CAS '24)
