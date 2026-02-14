CR for uiux reference
for the hamburger menu, now let's have two big functions, each option should have its own process.
- 1. Catch Design Theme
- 2. Copy Design as Mockup


1. Catch Design Theme
- UI for Catch Design Theme, when we select it, it should expend, then display steps to guide user to make design theme with reference of the target page.
- Steps as below
	> step 1. pick colors (now the color picking is limited, I need the function to support color picker from all sources, for example video/image, canvas, fonts etc. it's pixel level color pick.), and need to have a magnifer so I can see clearly which pixel I am selecting.
	> step 2. add comments with options, for example pre-defined options "primary", "secondary"... and user can also have text box to give other comments if no predefined for them to choose.
	> step 3: create theme button to send back the request. 
	> and need have progressing messages to let user know if it's in progress and when it's finished show complete message.
	> behind scene, the uiux-reference skill should call brand-theme creation skill to create the brand theme.

2. Copy Design as Mockup
- the same as catch design theme, when we select it, it should expend, then display steps to guide user to make design mockup reference.
- Steps as below
	> step 1: ask user to select components or areas on the page they want to reference. for each component or area, instead only record dom elements. now let's also catch the area diamension, then take a screenshot, and minimun html/css
	> step 2: for each component or area selected by user, they can have text box for each to text extra instructions.
	> step 3: having an analyzing button, if click, then pass these basic info and extra instructions to agent, let agent to decide how many extra info it needed to mimic the component or area as a mockup.
	> step 4: having having button generate 1:1 mockup, saving meta data first, then generate mockup (all the information collected, including screenshots, html/css, component or area diamension and extra instructions) 
	> and need have progressing messages to notify user.
	> behind scene, the uiux-reference skill should still call the agent-interaction mcp to save meta, and then call create mockup skill