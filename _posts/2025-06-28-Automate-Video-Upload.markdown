---
layout: single
title:  "Automate Video Upload"
date:   2025-06-28
tags:
- automate
- video
- github
---

## Current workflow
This is my current routine to compose and upload latte art videos:-
1. Compose video on mobile with Inshot app
2. Upload video (from #1) and photos to onedrive (leftycoffee account)
3. Switch over laptop, from onedrive folder, upload new video (from #2) to Youtube, create cover photo to be used on Youtube and Facebook
4. Create post here on github pages, copy/paste from previous post, edit markdown page, update with new photos and youtube link (from #3), commit and create page
5. Post facebook (leftycoffee account) with youtube video, youtube link (from #3) and github page link (from #4) 
6. Post facebook groups with photos from #3

Took me a while to organize and put together the workflow. These tasks took at least 30-45min a day, with the presumptions of stable internet connection. That affect upload speed greatly. 

## Challenge
I have some oversea trips lately and thought of automating the tasks. Quite hard to do all these when I'm out traveling, nor without my laptop or stable internet connection. 

Re-looking back into the workflows, in fact I can automate most of this. After some conversation (with ChatGPT) and I found I can automate task #2 - #4. ChatGPT did recommend me to automate all of these including the facebook post too, however I'm still enjoy doing the posting part, hence am saving it perhaps for the next phase. 

## Automation to the rescue
Here's the new workflow:-
1. Compose video on mobile with Inshot app, compose cover photo with Phonto app
2. Upload video & photo to onedrive (leftycoffee account)
3. Automation begins - trigger is onedrive folder with new files dropped in, once it is in, my script will pull it and upload it to Youtube, then create a github page here with the same info, and send me an email. 
4. Post facebook like how I did before 

The new workflow only takes like 10-15min. All I need to do is to compose video and upload. Then do my facebook post later, which I can even do it directly on my mobile. 

My email notification today :D 

![](/assets/img/2025/06/29/notification.jpg)

The script:-




