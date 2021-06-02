# What is this?

7 years ago, I had a really slow phone with a very poor battery, so when I needed a note-taking app, I downloaded the most light-weight one I could find: [com.onto.notepad](https://play.google.com/store/apps/details?id=com.onto.notepad&hl=en_CA&gl=US) by Anton Lashkov.

Now I'm ready to switch to a better app, but this one has no "Export" option. I guess they never expected someone to write >1000 notes.

That's the point of this project: **It will simulate your inputs in order to automatically extract your notes from this awful app.**

---

# Installation:

### Setting up AndroidViewClient:

All you need is Python 3.7 and [AndroidViewClient](https://github.com/dtmilano/AndroidViewClient). You can follow their instructions, or alternatively, you can follow mine:

- Get Python 3.7

- Install AndroidViewClient:

  - Run `pip install --pre androidviewclient --upgrade`

- Install `adb` to your path:

  - Grab the latest [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools).

  - Add them to your path. `adb` should work in terminal.

### Setting up your phone:

- Connect your phone to the PC via USB.

- Run `adb devices` to start the ADB server and make sure it sees your phone.

  - The phone should be listed there.

  - If it shows up as "Unauthorized", go to your phone, click authorize, and try again.

- Next, allow simulated inputs over USB.

  - Go to developer options and enable "USB debugging (Security Settings): Allow granting permissions and simulating input via USB debugging".

  - Note: If you ever use public chargers, it's a bad idea to use this on. Make sure to turn it off after you're done.

# Running:

```
python main.py
```
