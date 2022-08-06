<!-- Adapted from README Template here: https://github.com/othneildrew/Best-README-Template/pull/73 -->

# SimplifiedModding

This is a small Flask site for posting and sharing Sims 4 mods and tutorials.

By Bianca Morris (ALM in Digital Media Design Candidate at HES)

For CS50 Intensive Intro to CS @HSS


[View Demo Video](https://youtu.be/DPaD06I8zgs)


<!-- ABOUT THE PROJECT -->
## About The Project

Although I've been a long-time modder for the Sims franchise, it was only around last year that I started sharing mods I've made for this game. I was inspired by so many creators that came before me, including the wonderful MizoreYukii and Zer0, both of whom have done fantastic work both in terms of modding and in terms of knowledge-sharing within the community.

Especially as modding becomes a potentially lucrative creative endeavor, I think it's really important to make sure that the community of modders grows equitably. Providing new players with the tools they need to learn how to change their game is a vital part of that, especially since so many of the skills underpinning modding are typically out of reach for those without some technical or design background. But the reality is that it's really quite easy to get started, and SimplifiedModding is a snippet of my dream to make the community better, and give more folks, especially women and non-gender conforming folk (a huge portion of the Sims 4 player base) a chance to learn how to make things they find useful.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* Python and Flask
* Bootstrap
* JavaScript and jQuery

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started
To get a local copy up and running follow the following steps:

### Prerequisites

- Python dependencies are listed in the `requirements.txt`. These are auto-installed in the CS50 VS Code workspaces, so shouldn't require additional fiddling.
- A file unzipper or the ability to clone via git.

### Installation

1. Download and unzip or clone the repo
   ```sh
   git clone https://github.com/bianca-morris/simplifiedmodding.git
   ```
2. Move into the working directory
   ```sh
   cd simplifiedmodding
   ```
3. Define Environment Variables
   ```sh
   export ADMIN_SECRET="<Your Secret Here>"
   ```
4. Run the app with Flask
   ```sh
   flask run
   ```
5. Run the app with Flask
   Open http://127.0.0.1:5000 in browser to view

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

The home page, item pages, and search functionality should be pretty self-explanatory. However, the registration functionality may be a little less intutitive. In order to create an admin account capable of creating posts and tutorials for the website, you'll need to have followed the steps in the Installation guide above. It's very important to create an `ADMIN_SECRET` environment variable before running the application, otherwise you will not be able to create an admin account.

From registration, logging in should also be pretty simple. The dashboard can be used to create new posts, view or edit existing posts, and delete items. You can also change your password or view a short profile for the current user.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap
This is a MVP of a much larger, more time-consuming project idea. In the future, I'd hope to do the following:

- [ ] Add additional user types (non-admins) and features
- [ ] Add social engagemnt (links to socials and ways to share)
- [ ] Actually get this deployed... [I tried](https://simplifiedmodding.herokuapp.com/), but it, [uh, didn't go great](https://edstem.org/us/courses/20695/discussion/1665396).

More information on what is likely to change, specifically, is located in the DESIGN document.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

No license, just be nice.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Permalink -->
## Project Link

Project Link: [https://github.com/bianca-morris/simplifiedmodding](https://github.com/bianca-morris/simplifiedmodding)


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
And finally a special thanks to:

* CS50 Staff
* Stack Overflow
* The people who write docs
* EA, I guess

<p align="right">(<a href="#readme-top">back to top</a>)</p>
