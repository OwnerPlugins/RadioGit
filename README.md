<h1 align="center">📻 RadioGit</h1>

[![Version](https://img.shields.io/badge/Version.-1.4-blue.svg)](https://github.com/Belfagor2005/RadioGit)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python package](https://github.com/Belfagor2005/RadioGit/actions/workflows/pylint.yml/badge.svg)](https://github.com/Belfagor2005/RadioGit/actions/workflows/pylint.yml) 
[![Ruff Status](https://github.com/Belfagor2005/RadioGit/actions/workflows/ruff.yml/badge.svg)](https://github.com/Belfagor2005/RadioGit/actions/workflows/ruff.yml)

[![Visitors](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)](https://github.com/Belfagor2005)
[![Donate](https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://ko-fi.com/lululla)
[![Donate](https://img.shields.io/badge/_-Donate-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://paypal.me/belfagor2005)


![Plugin RadioGit](https://github.com/Belfagor2005/RadioGit/blob/main/usr/lib/enigma2/python/Plugins/Extensions/RadioGit/plugin.png?raw=true)

![GitHub Repo Content](https://img.shields.io/badge/github-junguler/m3u--radio--music--playlists-blue) 


# 🎵 M3U IPTV Repo Explorer Plugin


## Overview

The **M3U IPTV Repo Explorer** is a plugin designed to browse, display, and interact with M3U playlist files stored in a GitHub repository. It provides a user-friendly interface to navigate folders and playlists, select radio/music streams, and convert playlists into favorite `.tv` bouquets for Enigma2-based devices.

---

## 🚀 Features

- 🔍 **Browse M3U Playlists**  
  Navigate through folders and list `.m3u` files from a GitHub repository.

- 📂 **Folder Navigation**  
  Explore nested directories containing playlists.

- 🎧 **Stream Selection**  
  Select and play radio/music streams directly from the plugin.

- 📺 **Convert to Bouquet**  
  Convert M3U playlists into favorite `.tv` bouquets compatible with Enigma2.

- 🖥️ **Responsive UI**  
  Supports different screen resolutions (Full HD and HD) with custom skins.

---

## ⚙️ Components

### `M3URepoExplorer`

- Fetches and lists `.m3u` files and folders from the specified GitHub repository URL.
- Handles API requests to GitHub for repository contents.

### Screens

- `m3uiptv1` — Main screen showing top-level playlists and folders.
- `m3uiptv2` — Screen to browse inside a folder.
- `m3uiptv3` — Screen for deeper folder navigation and bouquet conversion.
- `m3uiptv4` — Screen to display individual playlist streams and play or search them.

---

## 🛠️ Usage

1. Set the GitHub repository URL containing your M3U playlists (default is `https://api.github.com/repos/junguler/m3u-radio-music-playlists/contents/`).

2. Navigate playlists and folders using the provided UI buttons:

   - **Red**: Exit  
   - **Green**: Select  
   - **Yellow**: Export playlist to bouquet (`.tv`)  
   - **Blue**: Search (currently hidden in some screens)

3. Select an M3U file to load the streams and play them.

4. Optionally convert playlists to Enigma2 bouquets for easier access.

---

## 🔧 Requirements

- Enigma2-based device or compatible emulator.
- Internet connection for accessing GitHub API.
- Python environment supporting `requests` and standard Enigma2 GUI libraries.

---

## 📦 Installation

Install this plugin by copying its files to your Enigma2 plugin directory and configuring your Enigma2 device to load it.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

Created by **Lululla**

---

## 🚩 Notes

- Playlist and folder browsing rely on the GitHub repository structure and API availability.
- Conversion to bouquets may take some time depending on the playlist size.
- Screen skins adjust automatically based on resolution (1920px width or others).

---

📻 Feel free to open issues or contribute!

---

⭐️ If you find this plugin useful, please give it a star on GitHub!



