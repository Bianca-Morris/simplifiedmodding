# Design Document
This is less of a complete overview of the application's structure, and more of a list of specific decisions I made and why. I don't think the application is complicated enough or different enough from our last pset to require a complete overview, so this is probably a more valuable way to use the space and time.


## File structure
One of the things that bothered me the most in our PSET 9 work was the way every single route for that application was tossed together in a single file. I spent so much time just scrolling or CTRL+F-ing, trying to find the specific method I needed to update. So, that was something I spent a bunch of time trying to resolve for this project.

You'll see that instead of having a single long file with many routes, I have a pretty barebones `app.py` and several more specific files in the routes folder. These should be pretty self-explanatory: if it relates to authentication, it'll be in `auth.py`; if it's database-specific, it'll be in `db.py`; if it's a standard website route, it'll be in `routes.py`; and if it's not really of the above, I've dumped it into `helpers.py`.


## Secret
As described in the README, there is a single environment variable required for the current implementation of the application. This application, in it's current state, is not meant to be used by anyone other than admin users with permission to create, edit, and destroy posts. The secret key seemed like an easy way for the administrator to configure an additional layer of security while building the application, that could then be used to restrict access to other users by sharing that data outside of the application through secure means.


## Admins and Authentication
There is one more small detail you might notice regarding authentication or while looking at the routes: the `admin_required` decorator function. This currently does nothing because I didn't have time to implement it, but I left it in as an indication of what my plans are for the future.

As I've mentioned before, I eventually want there to be different tiers of users. Admins who can edit and delete posts, and general users who can keep track of their downloads, maybe get lists of mods they've previously downloaded that have since been updated, etc. This decorator will be a vital part of how I'm planning to do that; another layer of authentication that checks permission status on a path-by-path level.

I'm still trying to figure out what the best way to implement this would be, so if you have thoughts, let me know. Should I just make a call to the DB to check the admin status of the user? Or would it be better to store something in the session, a cookie, or local storage upon login? There are a lot of options and I'm still assessing the advantages and drawbacks.


## Images and Videos
Because the content of the site is generated dynamically, by users, and so much of it is visual, the question of what to do about multimedia content came up pretty early. Hooking up a remote image hosting service like AWS s3 or something would be way too complicated given that we had a little over a week to produce a full implementation. So, instead, I built the application to use user-supplied URLs that are then fed into the `<img>` and `<video>` tags used throughout the application.

That being said, I understand that this implementation is highly flawed from a security perspective without additional sanitization of user input. I did some small amount of validation via regex on the client-side to prevent admins from submitting non-link files, but additional validation (to check file type, etc.) on the server side would be ideal for improved security in the next stages of this project's implementation.

I decided not to spend extensive time implementing this validation, however, because I do not intend for this to be the final implementation in the lifecycle of this product. I would rather make the switch directly to using a proper file storage system when I have the time and ability than put a bunch of time into making this inconvenient and insecure implentation incrementally better.


## CSS and Utility Classes
I've been using Bootstrap for several years now in varying capacities, so I'm very comfortable working with Bootstrap's utility classes. When working with Bootstrap in prototyping/front end projects, I typically take the approach of styling everything that I can via utility classes, and then add in CSS for the things that can't be easily done that way. This reduces the amount of extra CSS by quite a bit, and keeps what is there easier to read.

Redundancy is the major disadvantage of doing this in an application structured the way this one is, however, and I recognize that. I have worked mostly with React in the past, which provides an easy structure for creating modular front-end components where you define a list of classes once, and then it's applied everywhere that the component is used. It wasn't until I was too deep into the project to make time to rework everything that I was able to find potential ways to do something similar in Flask (Jinja macros? Or maybe partials?).

In the future, I would hope to work to create more re-usable snippets, and be consistent about using them across the application. This would greatly decrease front-end maintenance time and improve the overall quality of the code base.


## Heroku
You might notice while digging through the repository, that there are a few extra dependencies, an extra file or two, and some other details relating to my (unsuccessful) attempt to get this deployed to Heroku. In the places where I could, I added comments to explain what these pieces do. I don't want to remove them, because as with some of the above features, I am likely to try again.

However, it is important to note that by default, the application will run using a sqlite database NOT a postgres database. It is probably possible to update the environment variable used in `db.py` and run this application using postgres, but I just wasn't able to get the migration tool to work in time, unfortunately.


## In Conclusion
There are a great many things I would have done differently, had I been able to start this project with the knowledge I have now. I am trying to see that as less of a failure and more as evidence of successful learning, however, and I hope you do, too.

See ya,
It's been fun!

:)