I would like to futher increase code transparency. So I have following Idea.
	1. I would like to have new sub menu "Application Action Tracing" under workplace.
	2. Add a folder called "app-action-logs", and identify a app action log template. 
	3. Test Generation, Code Implementation, Code Refactoring skills should base on the action log template and programming lanaguage to generate logs to the `app-action-logs` folder
	4. Refactoring Analysis, and project-quality-board-management skills should check if code miss any app action logs in the code implementation and any log test missing.
	
## here are the details for each item above.
### Application Action Tracing
	- There is a sub menu called "Application Action Tracing"
	- when click on Application Action Tracing, it should bring Application Action Tracing view.
	- on top right there is a 2 options toggle to decide generate tracing application log ignored or to tracing folder(recording) , which should change the config in .env and base that to check if the logs should only be in console, or file or ignored.
	- beside toggle, there is a button called "ignored tracing", when click it, it should show list of api entry ignored for tracing, for each entry on the most right there is a icon to remove from ignored tracing list. the ignored tracing list is load from the config/ignored-tracing-apis.json
	- there is a sidebar on left side of action tracing view. when the tracing toggle is on, it will show all the tracing log files in last x hours config in .env to change. the tracing log pattern "{timestamp}-{root-api-name}-{tracing-id}.log"
	- there 3 colors status icon for each entry in sidebar. green no error, grey in processing, red there is error file for the tracing log pattern "{timestamp}-{root-api-name}-{tracing-id}.error.log"
	
### app-action-logs folder
	- it's under x-ipe-docs folder
	- There are two type of logs in it, the normal tracing log "{timestamp}-{root-api-name}-{tracing-id}.log", and the error log for any errors during tracing for related tracing-id, "{timestamp}-{root-api-name}-{tracing-id}.error.log"
	- for tracing log "{timestamp}-{root-api-name}-{tracing-id}.log", the log should be something like this:
	first line: 
	> traceid, root API url, purpose, input parameters and input parameters values, if object value in json.
	content lines:
	> start function: name1, purpose, input parameters and input parameters values, if object value in json.
	> start function: name2, purpose, input parameters and input parameters values
	> return function: name2, return data, if object value in json.
	> start api: API url2, purpose, input parameters and input parameters values
	> start function: name3, purpose, input parameters and input parameters values
	> return function: name3, purpose, input parameters and input parameters values
	> return api: API url2, purpose, input parameters and input parameters values
	> return function: name1, return data, if object value in json.
	- for the error log "{timestamp}-{root-api-name}-{tracing-id}.error.log", the log should be something like this:
	> start function: name2
	> {exceptions or erros can be multipule lines}
	> end function: name2
	> start function: name1
	> {exceptions or erros can be multipule lines}
	> end function: name1
	
### Code Tracing, Test Generation, Code Implementation, Code Refactoring skills
 create a code-tracing-creator skill
 - a standalone skill used to create tracing utility for code tracing.
 - need a script or template code for tracing utlity. each lanaguage have it's own script, for now let's support python, TS.
 - the tracing utility should base on the config in the .env to see if it's logging to console, file or ignore.
 
 for code implementation skill
 - when coding, in DoR check if the tracing utlity exists or not. if not call  code-tracing-creator skill create the utility first, then generate tracing test cases
 - need examples for embeding tracing using tracing utility when start of the function, end of the function, and error handling.
 - when DoD, may sure all codes wrote having tracing code.

for test generator
-  in DoR check if the tracing utlity exists or not. if not call  code-tracing-creator skill create the utility first
-  When writing unit test, make sure tracing has been tested for each function called in test case.

for code refactoring follow the same changes to support tracing handling.

### Refactoring Analysis, and project-quality-board-management skills
for these two skill, let's adding tracing as 1 diamension to check if code follow tracing requirement for each api, function.

above are functions or capabilities I want to implement for x-ipe.
