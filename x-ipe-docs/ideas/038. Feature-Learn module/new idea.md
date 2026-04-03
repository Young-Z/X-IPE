let's add a learning function

1. it's entry is under workplace ideation, let's have a menu for it.
2. one of it's capability is very similar to uiux reference function.
  > 1. we should have GUI for user to select target website.
  > 2. user should able click to a button to 'track the behavior'
  > 3. after click on the button it should open a avaiable terminal session, and typing prompt.
  > 4. calling a skill 'x-ipe-learning-behavior-tracker-for-web', it should just like UIUX reference skill, which embedding a js to the target website.
  > 5. after embedding it should have a action called 'recording', when it's on, it should record call user event such as click, drag, right click, typing...and also the event related element selector and related element info for example text, Accessibility tags...(the selector should be differentable with other elements.)
  > 6. the embeding script and the tracked data should be persist to the local storage, so when page redirect, the script can be quickly reinject and the tracked data can be refetched and continue it's tracking context.
  > 7. just like UIUX reference, the behavior tracker skill should leverage chrome-devtools mcp for script injection, and it should monitor the page, if page redirected, it should reinject the script from localstorage and restore it's tracking context, the tracking context should be apear in the injected toolbox as a list, and there are comment textbox beside each different user behavior event.
  > 8. there should be a sub agent in the tracker skill, constently pooling the tracked list after the injected toolbox. it should give comments to these tracked event, by either understanding the web page view, the behavior context, then write back the comments(the comments can be constently updated if AI agent have new more mature understanding of the behavior, for some meanless behavior it can mark 'Not-On-Key-Path').
  > 9. BTW on the GUI below target website, let's having a text box to fill tracking purpose, AI agent can use it as a major goal for this tracking.

