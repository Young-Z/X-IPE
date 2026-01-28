since uiux is criticle work for web application development, so I would like to have UIUX Feedback function in x-ipe
under workplace, there would be a sub menu called UIUX Feedback. I can imagine several functions

1. When I click UIUX Feeback, the right side of content will redirect to UIUX Feedback View.
2. in UIUX Feedback View, I should have big area (full of viewport) to show a browser simulator. 


brower similator:
for brower similator, I need following function.
- I should have a bar to enter url, and have "go" button beside it.
- after I click go, it should load url page in browser simulator.
- I should have a inspect button, when I click on it, when my mouse move into the browser simulator, the html element boundary should highlighted and show a small tag what's the element it is.
- when I right click on browser simulator, it should show menu option "providing feedback" or "providing feedback with screenshot"

behavior click "providing feedback" or "providing feedback with screenshot"
- create an feedback entry in expendable feedback list.
- expand and focus on the feedback entry
  > there is a generated name with timestamp for the feedback entry, and we have a delete button on the bar to delete the entry.
  > there is a text box to enter feedbacks
  > there is information small area here to show url and selected elements info.
  > there is thumbnail blew information area to show the screenshot of the selected elemente area
  > there is a button to called feedback.
 
when click on feedback logic
1. it upload the current feedback info to folder ''x-ipe/uiux-feedback/{generated name with timestamp}
 > having feedback.md to have enter feedbacks and information for html element selected, and url
 > having page-screenshot.png for screenshot
2. after save success, on entry should show reported, failed otherwise
3.  after save success, then will should open terminal and type the Get uiux feedback, please visit feedback folder {generated feedback folder} to get details. no enter, stop there.

above is my requirements, and here I also want to know for technical perspective how to do it? what's the tech stack (give me some some points)