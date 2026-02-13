in ideation, when I create an idea, now there are two options, composing directly or upload idea docs. I would like to add one more tab "UIUX Reference"

UIUX Reference Tab
- it should have a url input box.
- it should have an extra instruction text box.
- and a go to reference button

Go to Reference Button
- when I click on go to reference button, it should bring up console window, and find a non-in progress session. and type the prompt pre-defined for go to reference(in copilot-prompt.json)
- in the prompt it calls uiux-reference skill to guide agent to open the url and provide set of tools to reference uiux.

uiux-reference skill
- it should using chrome-devtool mcp to open url
- pre-define a sets of html/js tools that can be injected to the url page via chrome-devtools
- by default tools are collapsed as hamburger menu. when hover it should expend to show bunch of tools, and user can click on a tool to interactive with it.
	> for example: color picker tool, uiux-reference skill can pre define scripts or templates for color picker, when chrome-devtool opens the url, it can inject color picker into the page, so on the page i can see the color picker and pick the color from page.
	> here is the tool list
	> color picker: picking colors from page
	> page component/element highlighting, just like the inspection function in UIUX Feedback, should also able to take screenshot of the highlighted elements if possible.
	> page component/element comment, which can give comments to the highlighted elements.
- having a callback button, which can send back all collected info from tools.
- uiux-reference skill should pre-define the standard data model for receiving the data callbacks
- uiux-reference skill should call x-ipe-app-and-agent-interaction mcp to send back all the reference data info.

x-ipe-app-and-agent-interaction mcp
- define a new mcp and define new x-ipe api
- it should provide a api for receiving uiux reference.
- the uiux reference api should save all reference info into the new idea folder or selected idea folder.

