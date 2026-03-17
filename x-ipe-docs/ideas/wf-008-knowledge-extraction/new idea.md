let's create a skill called x-ipe-task-based-application-knowledge-extractor. it's core
  function should be 1. give a application root, it should progressively base on the hand on
  information to explore the unknow spaces under it's root folder and sub folders. classify all
  the founding knowleges. and focus on user given purpose of the extraction to iteractively
  getting the whole picker and generate target docs as knowlege put into .intake folder of the
  knowledge base. so here is summarized requirement:
	
# create a x-ipe-task-based-application-knowledge-extractor.
1. receiving a. target knowledge root path, b. purpose of the knowledge extraction.
2. it should support tools skill loading, for example web search tool, or ipe-task-knowledge-extraction-* tools, (for example ipe-task-knowledge-extraction-use-manual.
3. base on the purpose to load knowledge-extraction tool skills, and let get give more detailed deliverable scope and framework.
4. it should base on the existing knowledge structure to define best knowledge explore strategy. (can call web search to learn the best way to explore the knowledge if the web search tool is enabled by user.)
5. base on the strategy to explore iteratively, and should check with ipe-task-knowledge-extraction-* skill to get critique, but constructive feedbacks, and then continue improve the result.
6. since there may have many knowledges required to be generated. so you can generate progressivally into the knolwege intake folder with a root folder to wrap all the generated knowledges.
* before implement this skill, you can search online to see what's the best practice for example reference openclaw or it's top plugins or some other famous tools. and also for the strategy mentioned in above we need to have a basic metrics or hard rule to make sure the strategy is on track.

# create a ipe-task-knowledge-extraction-use-manual
1. you should learn what's the best way to structure application use manual in markdown and what's the key elemente we should have, you can search online if you are not clear. base on this we should have a standard use-manual playbook or playbooks template (for now you can only focus on web app, cli app or mobile app, see if they can share the same template if not you should create many template to adapt all the scenarios)
2. Operation 1: give highlevel use manual extraction strategy
		a. ask to provide application scope and general description of the application 50 to 150 words. need a template in the skill for structual info organization.(better for later validation on it's scope completeness)
		b. have a sub agent to give critique but constructive feedback on the application scope and description, see if anything extra required to generate playbook layout
		c. form use manaul playbook layout. (the playbook layout should be reference the template from the bullet point 1 above  and it should contain all the application scope and description informations, no information loss)
		d. save the playbook layout to a temp place for later retrival
3. Operation 2:  analyze provided knowledge. (focus on collecting the knowledge of provided function scope)
		a. you should ask for providing the knowledge, 
		b. then base on playbook layout to generate acceptance criteria to check if the information is enough for exmple to form step by step instructions or not. 
		c. put it into a temp folder easy for later step retriving.(here we focus on generating acceptance critieria first.)
		d. then fill the playbook and validate with acceptance criteria.
		e. give critique but constructive feedbacks to the playbook and acceptance criteria see if within the function scope the playbook content can meet the acceptance ceriteria, and also if the user manual step is smooth enough to follow. if not repeat operation 2 and ask for more info within the scope.
4. Opeartion 3: explore to extend the scope (focus on getting more scope of works, and then follow operation 2 to dig the scope.)
5. basically operation 2 focus on the deepth, operation 3 is focus on the width of the knowledge to meet the principle MECE.
6. use manual should support image or pictures this kind of rich representation if needed.