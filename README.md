# Bubble Theme 2026
New look on a Bubble Cards with multiple variants and vibes

| Bubble 2026 | sample1 | sample2 |
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/6dea7d27-f6d8-49f3-9b16-c59e600cd899" height="400"> | <img src="https://github.com/user-attachments/assets/82f30b75-f39e-42b6-b822-b507eac29e23" height="400"> | <img src="https://github.com/user-attachments/assets/83857607-f988-4fc5-8506-b3862c992b6f" height="400"> |
| Sth | Bubble? | or Dubble? |
| <img src="https://github.com/user-attachments/assets/856d9a18-c79c-4caa-a4ff-4c60c2b713ba" height="400"> | <img src="https://github.com/user-attachments/assets/4564c1b6-0446-4788-98b4-5610a42442b1" height="400"> | <img src="https://github.com/user-attachments/assets/1c5e01c7-c078-4afc-9334-4a71ad6fae65" height="400"> |


Silas Mariusz, BIO: [devspark.pl](https://devspark.pl)

Themes designed for [QNAP Club Poland](https://forum.qnap.net.pl), [QNAP Forum](https://forum.qnap.net.pl) crew

Report abuse or security issues: silas _AT&T_ qnapclub.pl


Podziekowania dla UberDudePL za ostanie fixy

Based on clooos Buuble theme

Based on Noctis theme from aFFekopp

With card-mod installed you got this features:

- A mobile view on desktop (like on the screenshot and you need to set your view in subview mode)
- No header on mobile


## Installation

### Without HACS (not recommended)

1. Download this file: [bubble_2026.yaml](https://raw.githubusercontent.com/silasmariusz/Bubble_Theme_2026/main/themes/bubble_2026.yaml)
2. Add this file into a new folder named `bubble_themes_2026` in the `<config>/themes/` folder
3. In your configuration.yaml add this: 
```yaml
frontend:
  themes: !include_dir_merge_named themes
```
4. Save and restart Home Assistant
5. Now go to your personal account settings and select Bubble as your theme

### With HACS

This method allows you to get updates directly in the HACS main page

1. Download HACS following the instructions on [https://hacs.xyz/docs/setup/download](https://hacs.xyz/docs/setup/download/)
2. Proceed to the initial configuration following the instructions on [https://hacs.xyz/docs/configuration/basic](https://hacs.xyz/docs/configuration/basic)
3. On your sidebar go to `HACS` > `Integrations`
4. click on the icon at the right top corner then on `Custom repositories`
5. For the repository add this: `https://github.com/silasmariusz/Bubble_Theme_2026`
6. For the category select `Theme` then click `Add`
7. Now click on `Bubble Theme 2026` then on the `Dowload` button
8. In your configuration.yaml add this: 
```yaml
frontend:
  themes: !include_dir_merge_named themes
```
9. Save and restart Home Assistant
10. Now go to your personal account settings and select Bubble 2026 as your theme

# FAQ

## After installation cant find Bubble 2026 Dubble* themes

Uuh

I see. Did I mention mod card addon and card mod is required? XDDDDD

PLEASE make sure you have installed it

Here is SOP Guide for absolutely anyone modyfing his HA and should be performed always after changes are done:

Have you checked your yaml config is healthy? Steps you should do you always after installing anything or modifying: 


### (Home Assistant actions)

1.	⁠go to Developer Tools from left sidebar
2.	⁠Check if your configuration has no errors (warnings are not errors) but basically do not continue if there are errors (fix them first)
3.	⁠If all is okay then click Actions in Developer tools and start typing reload or themes - you should fine action reload themes
4.	⁠Click execute
5.	⁠Leave developer tools, go to your profile settings in HA (hold on on that page)

### (Browser actions)
6. Hit F12 on keyboard to open Developed Tools (make sure you are on Home Assistant tab in your browser) 7. From the browser developer tools look for Network tab 8. Look for small check box DISABLE CACHE 9. Hit Ctrl+F5 in your browser 10. If there are no errors in console tab tab it’s fine. If there are errors resolve them

### (iOS/Android troubleshooting)
1. (if possivle) Swipe phone left/right to open debug menu if was already enabled, 
2. If above is not working go to HA settings and find Companion App menu 
3. Clear cache

IMO Those steps should be done each time by user always when modyfing any settings in HA. Unfortunately Home Assistant is lack of implementation Test Changes button and if something is wrong Revert button and Apply button if all is fine. HA in Test action could automatically rebuild cache and js/css links. Yes this mean Home Assistant is not friendly for newbies and devs IMHO

HOPE THIS HELPS

## Text white colour on vibe Lime accents is not visible
thats correct behavior. you have to redifine in such case conditionaly text styling

![themes_60](https://github.com/user-attachments/assets/3113ecf8-68d5-4345-aea2-3950e95f4e5e)


